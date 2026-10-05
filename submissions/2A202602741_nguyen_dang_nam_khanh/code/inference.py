"""inference.py - các phương pháp suy luận (Bước 3 của GUIDE.md).

Mọi hàm chạy ở chế độ eval, không gradient. Chọn phương pháp CHỈ dựa trên val; nhiệt độ T khớp
trên VAL rồi áp dụng sang test (README.md, S2 và S4).

Giao diện:
    predict_logits(model, loader, device, view=None) -> (filenames, y_true, logits[N, 9])
    aggregate_views(list_of_logits, space)           -> probs[N, 9]
    fit_temperature(val_logits, val_labels)          -> float T
    apply_temperature(logits, T)                     -> probs
    ensemble_probs(list_of_probs)                    -> probs
    fuse_conv_bn(model)                              -> model (BN đã gộp vào conv)
"""
from __future__ import annotations

import copy

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def predict_logits(model, loader, device, view=None, amp: bool = True):
    """Chạy model trên loader theo đúng thứ tự file. `view(x)` trả về một batch hoặc list batch
    (khi đó trả về list logit, mỗi phần tử một view)."""
    model.eval()
    names, ys, outs = [], [], None
    with torch.inference_mode():
        for x, y, f in loader:
            x = x.to(device, non_blocking=True)
            xs = view(x) if view is not None else x
            single = not isinstance(xs, (list, tuple))
            xs = [xs] if single else list(xs)
            if outs is None:
                outs = [[] for _ in xs]
            for i, xi in enumerate(xs):
                with torch.autocast("cuda", dtype=torch.float16, enabled=amp and device.type == "cuda"):
                    outs[i].append(model(xi.contiguous(memory_format=torch.channels_last)).float().cpu().numpy())
            names.extend(f)
            ys.append(y.numpy())
    logits = [np.concatenate(o) for o in outs]
    return names, np.concatenate(ys), (logits[0] if len(logits) == 1 else logits)


def view_identity(x):
    return x


def view_hflip(x):
    """Lật ngang batch (N, C, H, W) theo chiều rộng."""
    return torch.flip(x, dims=[3])


def views_hflip_tta(x):
    return [x, view_hflip(x)]


def views_multicrop(x, crop: int, flip: bool = False):
    """5 crop (4 góc + giữa) kích thước `crop` từ batch x (đầu vào lớn hơn crop, ví dụ ảnh 256)."""
    h, w = x.shape[-2:]
    tops = [(0, 0), (0, w - crop), (h - crop, 0), (h - crop, w - crop), ((h - crop) // 2, (w - crop) // 2)]
    views = [x[..., t:t + crop, l:l + crop] for t, l in tops]
    if flip:
        views += [view_hflip(v) for v in views]
    return views


def views_multiscale(x, sizes):
    """Resize batch về từng kích thước. CNN có global pooling chấp nhận mọi kích thước; ViT/Swin thì không."""
    return [x if x.shape[-1] == s else F.interpolate(x, size=(s, s), mode="bilinear",
                                                     align_corners=False, antialias=True) for s in sizes]


def _softmax(z):
    z = np.asarray(z, dtype=np.float64)
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


def aggregate_views(logits_per_view, space: str = "prob"):
    """Gộp K view: "prob" = trung bình softmax; "logit" = trung bình logit rồi softmax."""
    stack = np.stack([np.asarray(v, dtype=np.float64) for v in logits_per_view])
    if space == "prob":
        return _softmax(stack).mean(0)
    if space == "logit":
        return _softmax(stack.mean(0))
    raise ValueError(f"space không hợp lệ: {space}")


def ensemble_probs(list_of_probs):
    """Trung bình xác suất của nhiều mô hình (cùng tập ảnh, cùng thứ tự)."""
    p = np.mean(np.stack([np.asarray(q, dtype=np.float64) for q in list_of_probs]), 0)
    return p / p.sum(1, keepdims=True)


def fit_temperature(val_logits, val_labels) -> float:
    """T > 0 cực tiểu NLL trên VAL: lưới thô trên log T rồi tinh bằng LBFGS. Không khớp trên test."""
    z = torch.as_tensor(np.asarray(val_logits), dtype=torch.float64)
    y = torch.as_tensor(np.asarray(val_labels), dtype=torch.long)
    grid = torch.linspace(np.log(0.05), np.log(10.0), 200, dtype=torch.float64)
    nll = torch.stack([F.cross_entropy(z / t.exp(), y) for t in grid])
    log_t = grid[nll.argmin()].clone().requires_grad_(True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = F.cross_entropy(z / log_t.exp(), y)
        loss.backward()
        return loss

    opt.step(closure)
    return float(log_t.exp().item())


def apply_temperature(logits, T: float):
    return _softmax(np.asarray(logits, dtype=np.float64) / T)


def _fuse(conv: nn.Conv2d, bn: nn.BatchNorm2d) -> nn.Conv2d:
    fused = nn.Conv2d(conv.in_channels, conv.out_channels, conv.kernel_size, conv.stride, conv.padding,
                      conv.dilation, conv.groups, bias=True, padding_mode=conv.padding_mode)
    fused = fused.to(conv.weight.device, conv.weight.dtype)
    std = torch.sqrt(bn.running_var + bn.eps)
    gamma = bn.weight if bn.weight is not None else torch.ones_like(std)
    beta = bn.bias if bn.bias is not None else torch.zeros_like(std)
    scale = gamma / std
    with torch.no_grad():
        fused.weight.copy_(conv.weight * scale.reshape(-1, 1, 1, 1))
        b = conv.bias if conv.bias is not None else torch.zeros_like(bn.running_mean)
        fused.bias.copy_(beta + (b - bn.running_mean) * scale)
    return fused


def fuse_conv_bn(model):
    """Gộp mọi cặp (Conv2d -> BatchNorm2d) liền kề trong cùng một container:
        w' = gamma * w / sqrt(var + eps),  b' = beta + gamma * (b - mean) / sqrt(var + eps).
    Xử lý hai dạng: (a) nn.Sequential / thứ tự module con Conv rồi BN; (b) timm BatchNormAct2d
    đi sau conv được nhận diện như BN (phần activation giữ lại). Trả về BẢN SAO đã gộp.
    Không áp dụng cho kiến trúc không có BN (ViT, Swin, ConvNeXt dùng LayerNorm)."""
    model = copy.deepcopy(model).eval()
    n_fused = 0

    def bn_like(m):
        return isinstance(m, nn.BatchNorm2d)

    def strip_bn(bn):
        # timm BatchNormAct2d: giữ drop + act, bỏ phần chuẩn hoá
        if type(bn) is nn.BatchNorm2d:
            return nn.Identity()
        return nn.Sequential(getattr(bn, "drop", nn.Identity()), getattr(bn, "act", nn.Identity()))

    for parent in list(model.modules()):
        children = list(parent.named_children())
        for (n1, m1), (n2, m2) in zip(children, children[1:]):
            if isinstance(m1, nn.Conv2d) and bn_like(m2) and m2.num_features == m1.out_channels:
                setattr(parent, n1, _fuse(m1, m2))
                setattr(parent, n2, strip_bn(m2))
                n_fused += 1
    model.n_fused = n_fused
    return model


def check_fusion(model, fused, img_size: int = 224, device=None) -> float:
    """Sai số lớn nhất giữa đầu ra trước/sau gộp (FP32)."""
    device = device or next(model.parameters()).device
    x = torch.randn(4, 3, img_size, img_size, device=device)
    with torch.inference_mode():
        a, b = model.float().eval()(x), fused.float().eval()(x)
    return float((a - b).abs().max())
