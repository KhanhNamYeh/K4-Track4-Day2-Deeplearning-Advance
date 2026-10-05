"""Danh sách thí nghiệm (exp_id -> Config) và hàng đợi chạy tuần tự, chạy tiếp được khi bị ngắt.

    python code/experiments.py B01 B02          # chạy các exp_id cụ thể
    python code/experiments.py B                # chạy cả nhóm B
    python code/experiments.py --list           # in danh sách

Mọi thí nghiệm đi qua MỘT hàm train.run(Config(...)); exp_id chỉ khác nhau ở các field ghi trong
`EXPERIMENTS`. Nhóm T dùng backbone ghi trong `T_BACKBONE` (chọn sau Bước 1).
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train import Config, run  # noqa: E402

# ---- Bước 1: backbone, cùng công thức nền T00, seed 0 ----
BACKBONES = {
    "B01": ("resnet50", "resnet50"),
    "B02": ("convnext_tiny", "convnext_tiny"),
    "B03": ("deit_small_patch16_224", "deit_small"),
    "B04": ("swin_tiny_patch4_window7_224", "swin_tiny"),
    "B05": ("efficientnet_b0", "efficientnet_b0"),
    "B06": ("mobilenetv3_large_100", "mobilenetv3_large"),
}

# ---- Bước 2: công thức huấn luyện, mỗi dòng khác T00 đúng MỘT yếu tố ----
T_BACKBONE = "convnext_tiny"  # chọn sau Bước 1: F1 val cao nhất (B02) và độ trễ thấp
# exp_id: (trục, mô tả, thay đổi so với T00)
TRAINING = {
    "T00": ("-", "baseline", {}),
    "T01": ("A", "init_scratch", {"init": "scratch"}),
    "T02": ("A", "init_frozen", {"init": "frozen"}),
    "T03": ("B", "aug_color", {"aug": "color"}),
    "T04": ("B", "aug_trivial", {"aug": "trivial"}),
    "T05": ("B", "cutmix", {"mix": "cutmix"}),
    "T06": ("C", "label_smoothing", {"loss": "ls", "label_smoothing": 0.1}),
    "T07": ("C", "focal_g2", {"loss": "focal", "focal_gamma": 2.0}),
    "T08": ("C", "ce_class_weighted", {"loss": "ce_weighted", "class_weight_beta": 0.0}),
    "T09": ("D", "balanced_sampler", {"sampler": "balanced"}),
    "T10": ("E", "same_lr", {"lr_head": 1e-4}),
    "T11": ("F", "ema", {"ema_decay": 0.998}),
}


def experiments() -> dict[str, Config]:
    exps = {}
    for eid, (name, desc) in BACKBONES.items():
        exps[eid] = Config(exp_id=eid, desc=desc, backbone=name, seed=0)
    for eid, (_, desc, kw) in TRAINING.items():
        exps[eid] = Config(exp_id=eid, desc=desc, backbone=T_BACKBONE, seed=0, **kw)
    return exps


def main(argv: list[str]) -> None:
    exps = experiments()
    if not argv or argv[0] == "--list":
        for k, c in exps.items():
            print(k, c.backbone, c.desc)
        return
    ids = []
    for a in argv:
        ids += [k for k in exps if k == a or (len(a) == 1 and k.startswith(a))]
    log = Path("runs") / "queue_log.jsonl"
    log.parent.mkdir(exist_ok=True)
    for eid in ids:
        t0 = time.time()
        try:
            s = run(exps[eid])
            rec = {"exp_id": eid, "status": "ok", "val_macro_f1": s["val_macro_f1"], "min": (time.time() - t0) / 60}
        except Exception as e:  # ghi lỗi rồi chạy tiếp thí nghiệm sau
            traceback.print_exc()
            rec = {"exp_id": eid, "status": f"error: {e!r}", "min": (time.time() - t0) / 60}
        print("QUEUE", json.dumps(rec), flush=True)
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
    print("QUEUE DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
