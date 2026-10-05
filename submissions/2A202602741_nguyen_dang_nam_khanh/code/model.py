"""model.py - tạo backbone, đóng băng, nhóm tham số, đếm params/GMAC.

Giao diện (giữ nguyên theo starter):
    build_model(name, pretrained, num_classes, drop_rate, init) -> nn.Module
    freeze_backbone(model)                                        -> None
    param_groups(model, lr_backbone, lr_head, weight_decay)       -> list[dict] cho optimizer
    count_params(model) -> float (triệu)     count_gmacs(model, img_size) -> float

GMAC đếm bằng torch.utils.flop_counter.FlopCounterMode (có sẵn trong PyTorch): công cụ này trả về
FLOPs với quy ước 1 MAC = 2 FLOPs, nên GMAC = FLOPs / 2e9. Chỉ đếm conv/matmul (bỏ qua
activation, norm), có thể lệch vài phần trăm so với fvcore/ptflops.
"""
from __future__ import annotations

SUGGESTED_BACKBONES = {
    "resnet50": "resnet50",
    "resnext50": "resnext50_32x4d",
    "convnext_tiny": "convnext_tiny",
    "deit_small": "deit_small_patch16_224",
    "swin_tiny": "swin_tiny_patch4_window7_224",
    "efficientnet_b0": "efficientnet_b0",
    "mobilenetv3": "mobilenetv3_large_100",
}


def build_model(name: str, pretrained: bool = True, num_classes: int = 9,
                drop_rate: float = 0.0, init: str = "finetune", drop_path_rate: float = 0.0):
    """Tạo model 9 lớp qua timm. init: "scratch" | "frozen" | "finetune".

    Tag trọng số thực sự được tải ghi ở `model.weight_tag` (từ model.pretrained_cfg).
    """
    import timm

    if init not in ("scratch", "frozen", "finetune"):
        raise ValueError(f"init không hợp lệ: {init}")
    use_pretrained = pretrained and init != "scratch"
    kw = {"drop_path_rate": drop_path_rate} if drop_path_rate > 0 else {}
    model = timm.create_model(name, pretrained=use_pretrained, num_classes=num_classes,
                              drop_rate=drop_rate, **kw)
    cfg = getattr(model, "pretrained_cfg", {}) or {}
    tag = cfg.get("tag") or ""
    arch = cfg.get("architecture") or name
    model.weight_tag = f"{arch}.{tag}" if (use_pretrained and tag) else (arch if use_pretrained else "random-init")
    model.frozen = False
    if init == "frozen":
        freeze_backbone(model)
    return model


def head_parameters(model):
    """Tập id các tham số thuộc head mới (classifier của timm)."""
    return {id(p) for p in model.get_classifier().parameters()}


def freeze_backbone(model) -> None:
    """requires_grad=False cho mọi tham số trừ head; đánh dấu model.frozen để train loop
    giữ backbone (đặc biệt BatchNorm) ở chế độ eval, xem set_train_mode()."""
    head = head_parameters(model)
    for p in model.parameters():
        p.requires_grad = id(p) in head
    model.frozen = True


def set_train_mode(model) -> None:
    """model.train(), nhưng nếu backbone đóng băng thì mọi module trừ head về eval
    (BN không cập nhật running stats, dropout trong backbone tắt)."""
    model.train()
    if getattr(model, "frozen", False):
        model.eval()
        model.get_classifier().train()


def param_groups(model, lr_backbone: float, lr_head: float, weight_decay: float):
    """3 nhóm như slide trang 52:
      - backbone ndim > 1: lr_backbone, weight_decay
      - backbone norm/bias (ndim <= 1): lr_backbone, weight_decay = 0
      - head: lr_head; weight của head có wd, bias của head wd = 0
    Bỏ qua tham số requires_grad=False. Bỏ nhóm rỗng.
    """
    head = head_parameters(model)
    groups = {"backbone_decay": [], "backbone_no_decay": [], "head_decay": [], "head_no_decay": []}
    for p in model.parameters():
        if not p.requires_grad:
            continue
        part = "head" if id(p) in head else "backbone"
        kind = "decay" if p.ndim > 1 else "no_decay"
        groups[f"{part}_{kind}"].append(p)
    spec = {
        "backbone_decay": (lr_backbone, weight_decay),
        "backbone_no_decay": (lr_backbone, 0.0),
        "head_decay": (lr_head, weight_decay),
        "head_no_decay": (lr_head, 0.0),
    }
    return [{"params": ps, "lr": spec[k][0], "weight_decay": spec[k][1], "name": k}
            for k, ps in groups.items() if ps]


def count_params(model) -> float:
    """Số tham số (triệu), kể cả tham số bị đóng băng."""
    return sum(p.numel() for p in model.parameters()) / 1e6


def count_gmacs(model, img_size: int = 224) -> float:
    """GMAC cho một ảnh 3 x img_size x img_size (FlopCounterMode, FLOPs / 2)."""
    import torch
    from torch.utils.flop_counter import FlopCounterMode

    was_training = model.training
    model.eval()
    device = next(model.parameters()).device
    x = torch.zeros(1, 3, img_size, img_size, device=device)
    counter = FlopCounterMode(display=False)
    with counter, torch.no_grad():
        model(x)
    model.train(was_training)
    return counter.get_total_flops() / 2e9
