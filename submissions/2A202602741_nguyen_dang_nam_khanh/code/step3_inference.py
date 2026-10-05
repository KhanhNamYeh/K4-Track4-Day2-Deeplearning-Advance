"""Bước 3: so sánh phương pháp suy luận trên VAL (không huấn luyện lại) + độ trễ.

    python code/step3_inference.py --exp T00 [--ensemble B01 B02 ...] [--ema-exp T11]

Ghi results/inference_val.json và results/latency.json. Chỉ dùng VAL (quy tắc S2, S4).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dataset as D  # noqa: E402
import inference as I  # noqa: E402
from benchmark import latency_report  # noqa: E402
from eval import compute_metrics  # noqa: E402
from experiments import experiments  # noqa: E402
from train import load_trained, run_dir  # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OUT = Path("results")


def metrics(y, probs) -> dict:
    m = compute_metrics(y, probs.argmax(1), probs)
    return {"val_macro_f1": m["macro_f1"], "val_top1": m["top1"], "val_ece": m["ece"],
            "val_nll": m["nll"], "val_f1_per_class": m["f1"].tolist()}


def val_loader(img_size_eval: int, crop: bool = True):
    _, val_df, _ = D.load_split("data/labels", 0)
    if crop:
        tf = D.build_transforms(False, img_size_eval)
    else:  # ảnh đầy đủ 256 rồi resize về img_size_eval
        from torchvision.transforms import v2
        tf = v2.Compose([v2.Resize(img_size_eval, antialias=True), v2.ToDtype(torch.float32, scale=True),
                         v2.Normalize(D.IMAGENET_MEAN, D.IMAGENET_STD)])
    return D.make_loader(val_df, "data/images", tf, 64, False, None, 2), val_df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--ensemble", nargs="*", default=[])
    ap.add_argument("--ema-exp", default=None)
    ap.add_argument("--resolutions", nargs="*", type=int, default=[224, 256, 288, 320])
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    exps = experiments()
    cfg = exps[args.exp]
    model = load_trained(cfg, DEV)
    res, lat = {}, []

    loader, val_df = val_loader(224)
    names, y, z = I.predict_logits(model, loader, DEV)
    assert names == val_df["Filename"].tolist()
    base_logits = z
    res["I00"] = {"method": "1 view (center crop 224)", "K": 1, **metrics(y, I._softmax(z))}

    _, _, zz = I.predict_logits(model, loader, DEV, view=I.views_hflip_tta)
    res["I01"] = {"method": "TTA lật ngang, gộp xác suất", "K": 2, **metrics(y, I.aggregate_views(zz, "prob"))}
    res["I01b"] = {"method": "TTA lật ngang, gộp logit", "K": 2, **metrics(y, I.aggregate_views(zz, "logit"))}

    full, _ = val_loader(256)  # CenterCrop(256) = ảnh nguyên
    _, _, zc = I.predict_logits(model, full, DEV, view=lambda x: I.views_multicrop(x, 224, flip=False))
    res["I02"] = {"method": "TTA 5 crop 224 từ ảnh 256, gộp xác suất", "K": 5, **metrics(y, I.aggregate_views(zc, "prob"))}
    res["I03"] = {"method": "TTA 5 crop 224, gộp logit (so với I02)", "K": 5, **metrics(y, I.aggregate_views(zc, "logit"))}
    _, _, zs = I.predict_logits(model, full, DEV, view=lambda x: I.views_multiscale(x, [224, 256, 288]))
    res["I02b"] = {"method": "TTA 3 tỉ lệ (224/256/288 ảnh nguyên), gộp xác suất", "K": 3, **metrics(y, I.aggregate_views(zs, "prob"))}

    for r in args.resolutions:
        ld, _ = val_loader(r, crop=False)
        try:
            _, _, zr = I.predict_logits(model, ld, DEV)
            res[f"I04_{r}"] = {"method": f"Độ phân giải kiểm tra {r} (ảnh nguyên resize)", "K": 1,
                               "img_size": r, **metrics(y, I._softmax(zr))}
        except Exception as e:  # ViT/Swin không nhận kích thước khác
            res[f"I04_{r}"] = {"method": f"Độ phân giải {r}", "error": repr(e)}

    if args.ensemble:
        probs = [I._softmax(np.load(run_dir(exps[e]) / "val_logits.npy")) for e in args.ensemble]
        res["I05"] = {"method": "Ensemble trung bình xác suất: " + "+".join(args.ensemble),
                      "K": len(args.ensemble), **metrics(y, I.ensemble_probs(probs))}

    if args.ema_exp:
        ze = np.load(run_dir(exps[args.ema_exp]) / "val_logits.npy")
        res["I06"] = {"method": f"Trọng số EMA ({args.ema_exp}), 1 view", "K": 1, **metrics(y, I._softmax(ze))}

    # Temperature scaling: khớp T trên val. Báo ECE val trước/sau (T khớp trên chính val nên
    # ECE val sau TS lạc quan; số chính thức trước/sau là trên test ở Bước 4).
    T = I.fit_temperature(base_logits, y)
    res["I07"] = {"method": f"Temperature scaling (T={T:.4f}, khớp trên val)", "K": 1, "T": T,
                  **metrics(y, I.apply_temperature(base_logits, T))}

    fused = I.fuse_conv_bn(model.float())
    err = I.check_fusion(model, fused, 224, DEV) if fused.n_fused else None
    _, _, zf = I.predict_logits(fused, loader, DEV, amp=False)
    res["I08"] = {"method": f"Gộp BN vào conv ({fused.n_fused} cặp), FP32", "K": 1,
                  "max_abs_diff": err, **metrics(y, I._softmax(zf))}
    _, _, z32 = I.predict_logits(model, loader, DEV, amp=False)
    res["I08_fp32"] = {"method": "1 view FP32 (không AMP)", "K": 1, **metrics(y, I._softmax(z32))}

    # ---- độ trễ: batch 1 và 32, đo đúng cách (warmup 10, synchronize, 100 lần) ----
    base = dict(device="cuda", warmup=10, iters=100)
    for dtype in ("fp32", "amp", "fp16"):
        for bs in (1, 32):
            lat.append({"config": f"{cfg.backbone} 1 view", **latency_report(model, bs, 224, dtype, **base)})
    if fused.n_fused:
        for dtype in ("fp32", "fp16"):
            for bs in (1, 32):
                lat.append({"config": f"{cfg.backbone} gộp BN", **latency_report(fused, bs, 224, dtype, fused_bn=True, **base)})
    for k, name in ((2, "TTA lật K=2"), (5, "TTA 5 crop K=5"), (3, "TTA 3 tỉ lệ (xấp xỉ, 3 lượt 224)")):
        lat.append({"config": f"{cfg.backbone} {name}", **latency_report(model, 1, 224, "amp", views=k, **base)})
    for r in args.resolutions:
        try:
            lat.append({"config": f"{cfg.backbone} res {r}", **latency_report(model, 1, r, "amp", **base)})
        except Exception:
            pass
    for e in args.ensemble:
        m = load_trained(exps[e], DEV)
        lat.append({"config": f"{exps[e].backbone} ({e}) 1 view", **latency_report(m, 1, 224, "amp", **base)})
        del m

    meta = {"exp": args.exp, "backbone": cfg.backbone, "ensemble": args.ensemble, "ema_exp": args.ema_exp}
    (OUT / "inference_val.json").write_text(json.dumps({"meta": meta, "results": res}, indent=2, ensure_ascii=False))
    (OUT / "latency.json").write_text(json.dumps(lat, indent=2, ensure_ascii=False))
    for k, v in res.items():
        print(k, v.get("method"), {m: round(v[m], 4) for m in ("val_macro_f1", "val_top1", "val_ece") if m in v})
    print("BƯỚC 3 XONG")


if __name__ == "__main__":
    main()
