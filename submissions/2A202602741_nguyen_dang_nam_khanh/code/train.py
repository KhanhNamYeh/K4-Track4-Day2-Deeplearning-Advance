"""train.py - vòng huấn luyện dùng chung cho mọi thí nghiệm (B, T, F).

Một hàm `run(cfg)` cho mọi cấu hình; đổi thí nghiệm bằng cách đổi `Config`.

    python train.py --set exp_id=B01 backbone=resnet50 seed=0

Chỉ số chọn checkpoint (macro-F1 val) tính bằng eval.compute_metrics của repo gốc.
Mỗi lần chạy ghi vào <out_dir>/<exp_id>/seed<k>/:
    config.json, history.csv, steps_lr.npy, summary.json, val_logits.npy (+ test_logits.npy ở Bước 4),
    best.pt (checkpoint tốt nhất theo macro-F1 val), last.pt (để chạy tiếp khi phiên Colab bị ngắt)
và <pred_dir>/<exp_id>_seed<k>_val.csv, curves/<exp_id>_<mota>.png.
"""
from __future__ import annotations

import argparse
import copy
import dataclasses
import json
import os
import platform
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _p in (HERE, HERE.parent, HERE.parent.parent.parent):  # code/, bài nộp, gốc repo (eval.py)
    if (_p / "eval.py").exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from eval import compute_metrics, save_predictions  # noqa: E402


@dataclass
class Config:
    # --- định danh ---
    exp_id: str = "T00"
    desc: str = ""                    # mô tả ngắn, dùng trong tên ảnh curves/<exp_id>_<desc>.png
    seed: int = 0
    fold: int = 0
    # --- mô hình ---
    backbone: str = "resnet50"
    init: str = "finetune"            # scratch | frozen | finetune
    drop_rate: float = 0.0
    drop_path_rate: float = 0.0
    # --- dữ liệu / augmentation ---
    img_size: int = 224
    aug: str = "basic"                # basic | color | trivial | randaug | basic_vflip
    sampler: str | None = None        # None | balanced
    mix: str | None = None            # None | mixup | cutmix
    mix_alpha: float = 1.0
    # --- loss ---
    loss: str = "ce"                  # ce | ls | focal | ce_weighted
    label_smoothing: float = 0.1
    focal_gamma: float = 2.0
    class_weight_beta: float | None = None
    # --- tối ưu (công thức nền, GUIDE.md mục 1.4; epoch giảm 12 -> 10 vì ngân sách Colab miễn phí) ---
    optimizer: str = "adamw"          # adamw | sgd
    epochs: int = 10
    batch_size: int = 64
    lr_backbone: float = 1e-4
    lr_head: float = 1e-3
    weight_decay: float = 0.05
    warmup_epochs: float = 1.0
    ema_decay: float | None = None
    amp: bool = True
    grad_clip: float | None = None
    num_workers: int = 2
    max_train_batches: int | None = None   # chỉ dùng để kiểm tra pipeline nhanh
    # --- đường dẫn ---
    images_dir: str = "data/images"
    labels_dir: str = "data/labels"
    out_dir: str = "runs"
    pred_dir: str = "predictions"
    curves_dir: str = "curves"
    # --- chỉ bật ở Bước 4 (chung kết): ghi predictions trên TEST. Mặc định TẮT (quy tắc S4). ---
    save_test_predictions: bool = False


def run_dir(cfg: Config) -> Path:
    return Path(cfg.out_dir) / cfg.exp_id / f"seed{cfg.seed}"


def pred_path(cfg: Config, split: str) -> Path:
    return Path(cfg.pred_dir) / f"{cfg.exp_id}_seed{cfg.seed}_{split}.csv"


def curve_path(cfg: Config) -> Path:
    name = f"{cfg.exp_id}_{cfg.desc}" if cfg.desc else cfg.exp_id
    if cfg.exp_id.startswith("F") or cfg.seed != 0:
        name += f"_seed{cfg.seed}"
    return Path(cfg.curves_dir) / f"{name}.png"


def set_seed(seed: int) -> None:
    """random, numpy, torch CPU/CUDA. cudnn.benchmark=True để nhanh: kết quả lặp lại được ở
    mức thống kê, không bit-exact (ghi trong báo cáo)."""
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False


def build_optimizer(model, cfg: Config):
    import torch
    from model import param_groups
    groups = param_groups(model, cfg.lr_backbone, cfg.lr_head, cfg.weight_decay)
    if cfg.optimizer == "adamw":
        return torch.optim.AdamW(groups, betas=(0.9, 0.999))
    if cfg.optimizer == "sgd":
        return torch.optim.SGD(groups, momentum=0.9, nesterov=True)
    raise ValueError(f"optimizer không hợp lệ: {cfg.optimizer}")


def build_scheduler(optimizer, cfg: Config, steps_per_epoch: int):
    """Warmup tuyến tính rồi cosine về 0, cập nhật THEO BƯỚC (iteration)."""
    import math
    import torch
    total = max(1, cfg.epochs * steps_per_epoch)
    warm = int(round(cfg.warmup_epochs * steps_per_epoch))

    def factor(step: int) -> float:
        if warm > 0 and step < warm:
            return (step + 1) / warm
        t = (step - warm) / max(1, total - warm)
        return 0.5 * (1.0 + math.cos(math.pi * min(1.0, t)))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, factor)


class EMA:
    """W_ema <- d * W_ema + (1 - d) * W cho mọi tham số VÀ buffer dạng số thực (gồm running
    mean/var của BN, nên thống kê BN của bản EMA khớp với trọng số EMA); buffer nguyên
    (num_batches_tracked) được chép thẳng. decay hiệu dụng = min(d, (1+n)/(10+n)) để bản EMA
    không bị kéo về trọng số khởi đầu khi số bước ít."""

    def __init__(self, model, decay: float):
        self.decay = decay
        self.module = copy.deepcopy(model).eval()
        for p in self.module.parameters():
            p.requires_grad_(False)
        self.updates = 0

    def update(self, model) -> None:
        import torch
        self.updates += 1
        d = min(self.decay, (1 + self.updates) / (10 + self.updates))
        with torch.no_grad():
            msd = model.state_dict()
            for k, v in self.module.state_dict().items():
                src = msd[k].detach()
                if v.dtype.is_floating_point:
                    v.mul_(d).add_(src, alpha=1 - d)
                else:
                    v.copy_(src)


def train_one_epoch(model, loader, criterion, optimizer, scheduler, scaler, cfg: Config,
                    device, ema: EMA | None = None) -> dict:
    import torch
    from losses import mix_batch, mixed_loss
    from model import set_train_mode

    set_train_mode(model)
    total, n, correct, lrs = 0.0, 0, 0, []
    for b, (x, y, _) in enumerate(loader):
        if cfg.max_train_batches and b >= cfg.max_train_batches:
            break
        x = x.to(device, non_blocking=True).to(memory_format=torch.channels_last)
        y = y.to(device, non_blocking=True)
        with torch.autocast("cuda", dtype=torch.float16, enabled=cfg.amp and device.type == "cuda"):
            if cfg.mix:
                x_mix, targets = mix_batch(x, y, cfg.mix_alpha, cfg.mix)
                logits = model(x_mix)
                loss = mixed_loss(criterion, logits.float(), targets)
            else:
                logits = model(x)
                loss = criterion(logits.float(), y)
        optimizer.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        if cfg.grad_clip:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        scaler.step(optimizer)
        scaler.update()
        lrs.append(optimizer.param_groups[0]["lr"])
        scheduler.step()
        if ema is not None:
            ema.update(model)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"loss = {loss.item()} ở batch {b}")
        total += loss.item() * x.shape[0]
        n += x.shape[0]
        if not cfg.mix:
            correct += (logits.argmax(1) == y).sum().item()
    return {"train_loss": total / max(n, 1), "train_top1": (correct / n) if (n and not cfg.mix) else float("nan"),
            "lrs": lrs}


def evaluate(model, loader, criterion, device, amp: bool = True):
    """Chạy model ở chế độ eval, không gradient. Trả về (filenames, y_true, logits, loss)."""
    import torch
    model.eval()
    names, ys, outs, total, n = [], [], [], 0.0, 0
    with torch.inference_mode():
        for x, y, f in loader:
            x = x.to(device, non_blocking=True).to(memory_format=torch.channels_last)
            y = y.to(device, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.float16, enabled=amp and device.type == "cuda"):
                logits = model(x).float()
            if criterion is not None:
                total += torch.nn.functional.cross_entropy(logits, y, reduction="sum").item()
            n += x.shape[0]
            names.extend(f)
            ys.append(y.cpu().numpy())
            outs.append(logits.cpu().numpy())
    return names, np.concatenate(ys), np.concatenate(outs), total / max(n, 1)


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def plot_curves(history: list[dict], path: str | Path, title: str, step_lrs=None) -> None:
    """3 panel: loss train/val; macro-F1 và top-1 val (và top-1 train nếu có); LR theo bước."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ep = [h["epoch"] for h in history]
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
    ax[0].plot(ep, [h["train_loss"] for h in history], "o-", label="train loss")
    ax[0].plot(ep, [h["val_loss"] for h in history], "s-", label="val loss (CE)")
    ax[0].set(xlabel="epoch", ylabel="loss", title="Loss")
    ax[0].legend()
    ax[1].plot(ep, [h["val_macro_f1"] for h in history], "o-", label="val macro-F1")
    ax[1].plot(ep, [h["val_top1"] for h in history], "s-", label="val top-1")
    tr = [h.get("train_top1", float("nan")) for h in history]
    if not all(np.isnan(tr)):
        ax[1].plot(ep, tr, "^--", alpha=0.6, label="train top-1 (có augmentation)")
    best = max(history, key=lambda h: (h["val_macro_f1"], -h["epoch"]))
    ax[1].axvline(best["epoch"], color="gray", ls=":", label=f"best epoch {best['epoch']} (F1={best['val_macro_f1']:.4f})")
    ax[1].set(xlabel="epoch", ylabel="metric", title="Val metric")
    ax[1].legend(fontsize=8)
    if step_lrs is not None and len(step_lrs):
        ax[2].plot(np.arange(len(step_lrs)) / max(1, len(step_lrs) / len(ep)), step_lrs)
        ax[2].set(xlabel="epoch (theo bước)", ylabel="LR backbone", title="Lịch LR (warmup + cosine)")
    for a in ax:
        a.grid(alpha=0.3)
    fig.suptitle(title)
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def env_info() -> dict:
    import timm
    import torch
    import torchvision
    return {"python": platform.python_version(), "torch": torch.__version__,
            "torchvision": torchvision.__version__, "timm": timm.__version__,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"}


def build_criterion_for(cfg: Config, train_df, device):
    from dataset import NUM_CLASSES
    from losses import build_criterion, class_weights
    if cfg.loss == "ce_weighted":
        counts = np.bincount(train_df["Label"].astype(int), minlength=NUM_CLASSES)
        w = class_weights(counts, cfg.class_weight_beta or 0.0)
        return build_criterion("ce_weighted", weight=w).to(device)
    return build_criterion(cfg.loss, smoothing=cfg.label_smoothing, gamma=cfg.focal_gamma).to(device)


def run(cfg: Config) -> dict:
    """Huấn luyện một cấu hình, chọn checkpoint theo MACRO-F1 VAL (hòa lấy epoch sớm hơn),
    lưu logit/predictions val; test chỉ khi cfg.save_test_predictions (Bước 4)."""
    import pandas as pd
    import torch
    import dataset as D
    from model import build_model, count_gmacs, count_params

    rd = run_dir(cfg)
    rd.mkdir(parents=True, exist_ok=True)
    if (rd / "summary.json").exists():
        summary = json.loads((rd / "summary.json").read_text())
        if cfg.save_test_predictions and "test" not in summary:
            summary["test"] = evaluate_test(cfg)
            (rd / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"[{cfg.exp_id} seed{cfg.seed}] đã huấn luyện xong, không train lại")
        return summary
    set_seed(cfg.seed)
    (rd / "config.json").write_text(json.dumps({**dataclasses.asdict(cfg), "env": env_info()}, indent=2))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_df, val_df, test_df = D.load_split(cfg.labels_dir, cfg.fold)
    D.check_split(train_df, val_df, test_df, cfg.images_dir, verbose=False)
    tf_train = D.build_transforms(True, cfg.img_size, cfg.aug)
    tf_eval = D.build_transforms(False, cfg.img_size)
    train_loader = D.make_loader(train_df, cfg.images_dir, tf_train, cfg.batch_size, True,
                                 cfg.sampler, cfg.num_workers, cfg.seed)
    val_loader = D.make_loader(val_df, cfg.images_dir, tf_eval, 128, False, None, cfg.num_workers)

    model = build_model(cfg.backbone, True, D.NUM_CLASSES, cfg.drop_rate, cfg.init, cfg.drop_path_rate)
    n_params, gmacs = count_params(model), count_gmacs(model, cfg.img_size)
    model = model.to(device).to(memory_format=torch.channels_last)
    criterion = build_criterion_for(cfg, train_df, device)
    optimizer = build_optimizer(model, cfg)
    steps = len(train_loader) if not cfg.max_train_batches else min(len(train_loader), cfg.max_train_batches)
    scheduler = build_scheduler(optimizer, cfg, steps)
    scaler = torch.amp.GradScaler("cuda", enabled=cfg.amp and device.type == "cuda")
    ema = EMA(model, cfg.ema_decay) if cfg.ema_decay else None

    history, step_lrs, start_epoch = [], [], 1
    best = {"f1": -1.0, "epoch": 0}
    last = rd / "last.pt"
    if last.exists():  # chạy tiếp sau khi phiên bị ngắt
        ck = torch.load(last, map_location=device, weights_only=False)
        model.load_state_dict(ck["model"])
        optimizer.load_state_dict(ck["optimizer"])
        scheduler.load_state_dict(ck["scheduler"])
        scaler.load_state_dict(ck["scaler"])
        if ema is not None:
            ema.module.load_state_dict(ck["ema"])
            ema.updates = ck["ema_updates"]
        history, step_lrs, best = ck["history"], ck["step_lrs"], ck["best"]
        start_epoch = ck["epoch"] + 1
        torch.set_rng_state(ck["rng_cpu"])
        print(f"[{cfg.exp_id} seed{cfg.seed}] tiếp tục từ epoch {start_epoch}")

    eval_model = ema.module if ema is not None else model
    for epoch in range(start_epoch, cfg.epochs + 1):
        t0 = time.perf_counter()
        tr = train_one_epoch(model, train_loader, criterion, optimizer, scheduler, scaler, cfg, device, ema)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_train = time.perf_counter() - t0
        names, y_val, logits, val_loss = evaluate(eval_model, val_loader, criterion, device, cfg.amp)
        m = compute_metrics(y_val, logits.argmax(1), softmax(logits))
        step_lrs.extend(tr["lrs"])
        h = {"epoch": epoch, "train_loss": tr["train_loss"], "train_top1": tr["train_top1"],
             "val_loss": val_loss, "val_macro_f1": m["macro_f1"], "val_top1": m["top1"],
             "val_bal_acc": m["balanced_acc"], "val_ece": m["ece"], "lr_end": tr["lrs"][-1],
             "epoch_train_s": t_train, "epoch_total_s": time.perf_counter() - t0}
        history.append(h)
        print(f"[{cfg.exp_id} s{cfg.seed}] ep {epoch:2d} train_loss {h['train_loss']:.4f} "
              f"val_loss {val_loss:.4f} F1 {m['macro_f1']:.4f} top1 {m['top1']:.4f} ({t_train:.0f}s)", flush=True)
        if m["macro_f1"] > best["f1"]:  # hòa thì giữ epoch sớm hơn
            best = {"f1": m["macro_f1"], "epoch": epoch}
            torch.save({"model": eval_model.state_dict(), "epoch": epoch}, rd / "best.pt")
            np.save(rd / "val_logits.npy", logits)
        torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(),
                    "scheduler": scheduler.state_dict(), "scaler": scaler.state_dict(),
                    "ema": ema.module.state_dict() if ema else None,
                    "ema_updates": ema.updates if ema else 0,
                    "history": history, "step_lrs": step_lrs, "best": best, "epoch": epoch,
                    "rng_cpu": torch.get_rng_state()}, last)

    pd.DataFrame(history).to_csv(rd / "history.csv", index=False)
    np.save(rd / "steps_lr.npy", np.asarray(step_lrs))
    val_logits = np.load(rd / "val_logits.npy")
    y_val = val_df["Label"].astype(int).to_numpy()
    save_predictions(pred_path(cfg, "val"), val_df["Filename"].tolist(), y_val, softmax(val_logits))
    mv = compute_metrics(y_val, val_logits.argmax(1), softmax(val_logits))
    plot_curves(history, curve_path(cfg), f"{cfg.exp_id} | {cfg.backbone} | {cfg.desc} | seed {cfg.seed}", step_lrs)

    summary = {
        "exp_id": cfg.exp_id, "seed": cfg.seed, "backbone": cfg.backbone,
        "weight_tag": getattr(model, "weight_tag", ""), "params_M": n_params, "gmacs": gmacs,
        "best_epoch": best["epoch"], "val_macro_f1": mv["macro_f1"], "val_top1": mv["top1"],
        "val_bal_acc": mv["balanced_acc"], "val_ece": mv["ece"],
        "val_f1_per_class": mv["f1"].tolist(), "val_recall_per_class": mv["recall"].tolist(),
        "train_s_per_epoch": float(np.mean([h["epoch_train_s"] for h in history])),
        "epochs": cfg.epochs, "env": env_info(),
    }
    if cfg.save_test_predictions:
        summary["test"] = evaluate_test(cfg)
    (rd / "summary.json").write_text(json.dumps(summary, indent=2))
    if last.exists():
        last.unlink()  # chỉ giữ best.pt
    return summary


def load_trained(cfg: Config, device=None):
    """Nạp checkpoint tốt nhất (theo val) của một lần chạy đã xong."""
    import torch
    import dataset as D
    from model import build_model
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(cfg.backbone, False, D.NUM_CLASSES, cfg.drop_rate, "finetune", cfg.drop_path_rate)
    ck = torch.load(run_dir(cfg) / "best.pt", map_location=device, weights_only=False)
    model.load_state_dict(ck["model"])
    return model.to(device).to(memory_format=torch.channels_last).eval()


def evaluate_test(cfg: Config) -> dict:
    """Bước 4: đánh giá checkpoint tốt nhất trên TOÀN BỘ test, ĐÚNG MỘT LẦN mỗi seed.
    Từ chối chạy nếu đã có test_logits.npy (để không chạy test lặp lại)."""
    import torch
    import dataset as D
    rd = run_dir(cfg)
    out = rd / "test_logits.npy"
    if out.exists():
        raise RuntimeError(f"{out} đã tồn tại: test chỉ được chạy một lần mỗi seed")
    _, _, test_df = D.load_split(cfg.labels_dir, cfg.fold)
    loader = D.make_loader(test_df, cfg.images_dir, D.build_transforms(False, cfg.img_size), 128, False,
                           None, cfg.num_workers)
    model = load_trained(cfg)
    names, y, logits, _ = evaluate(model, loader, None, torch.device("cuda" if torch.cuda.is_available() else "cpu"), cfg.amp)
    assert names == test_df["Filename"].tolist()
    np.save(out, logits)
    save_predictions(pred_path(cfg, "test"), names, y, softmax(logits))
    m = compute_metrics(y, logits.argmax(1), softmax(logits))
    return {"macro_f1": m["macro_f1"], "top1": m["top1"], "ece": m["ece"]}


def _cast(value: str, field_type):
    v = value.strip()
    if v.lower() in ("none", "null"):
        return None
    t = str(field_type)
    if "bool" in t:
        if v.lower() in ("1", "true", "yes"):
            return True
        if v.lower() in ("0", "false", "no"):
            return False
        raise ValueError(f"không ép được '{value}' sang bool")
    if "int" in t and "float" not in t:
        return int(v)
    if "float" in t:
        return float(v)
    return v


def parse_overrides(pairs: list[str]) -> dict:
    """['seed=1', 'loss=focal', 'ema_decay=none'] -> dict đã ép kiểu theo field của Config."""
    fields = {f.name: f.type for f in dataclasses.fields(Config)}
    out = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"'{pair}' không có dạng KEY=VALUE")
        k, v = pair.split("=", 1)
        if k not in fields:
            raise KeyError(f"'{k}' không phải field của Config")
        out[k] = _cast(v, fields[k])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Huấn luyện một cấu hình DeepWeeds")
    ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    args = ap.parse_args()
    cfg = Config(**parse_overrides(args.set))
    print(json.dumps(run(cfg), indent=2, default=str))


if __name__ == "__main__":
    main()
