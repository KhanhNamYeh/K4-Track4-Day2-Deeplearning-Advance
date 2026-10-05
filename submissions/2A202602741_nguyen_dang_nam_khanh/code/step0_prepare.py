"""Bước 0: tải dữ liệu, kiểm tra chia dữ liệu (README 2.1), EDA, kiểm tra pipeline (GUIDE 1.3).

Chạy từ thư mục làm việc (chứa eval.py và code/):   python code/step0_prepare.py
Kết quả ghi vào eda/: split_check.json, class_distribution.png, samples.png, augment_check.png,
pipeline_check.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dataset as D  # noqa: E402

ZIP_URL = "https://zenodo.org/records/7939060/files/images.zip?download=1"
ZIP_MD5 = "b7b30f96d466fba86016aa5a26606e0f"
LABELS_BASE = "https://raw.githubusercontent.com/AlexOlsen/DeepWeeds/master/labels"
PAPER_TABLE1 = {"Chinee Apple": 1125, "Lantana": 1064, "Parkinsonia": 1031, "Parthenium": 1022,
                "Prickly Acacia": 1062, "Rubber Vine": 1009, "Siam Weed": 1074, "Snake Weed": 1016,
                "Negatives": 9106}
DATA = Path("data")
EDA = Path("eda")


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download() -> Path:
    (DATA / "labels").mkdir(parents=True, exist_ok=True)
    z = DATA / "images.zip"
    if not z.exists():
        print("Tải images.zip ...", flush=True)
        subprocess.run(["wget", "-q", "-O", str(z), ZIP_URL], check=True)
    digest = md5(z)
    assert digest == ZIP_MD5, f"MD5 sai: {digest}"
    print("MD5 OK:", digest)
    img_dir = DATA / "images"
    if not img_dir.exists() or len(os.listdir(img_dir)) < D.TOTAL_IMAGES:
        img_dir.mkdir(exist_ok=True)
        subprocess.run(["unzip", "-q", "-n", str(z), "-d", str(img_dir)], check=True)
        # nếu zip có thư mục con, chuyển ảnh lên img_dir
        subs = [p for p in img_dir.iterdir() if p.is_dir()]
        for s in subs:
            for f in s.iterdir():
                f.rename(img_dir / f.name)
            s.rmdir()
    for name in ["labels", "train_subset0", "val_subset0", "test_subset0"]:
        dst = DATA / "labels" / f"{name}.csv"
        if not dst.exists():
            urllib.request.urlretrieve(f"{LABELS_BASE}/{name}.csv", dst)
    print("Số file ảnh:", len(os.listdir(img_dir)))
    return img_dir


def eda(img_dir: Path, train_df, val_df, test_df, info: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    from PIL import Image

    pc = pd.DataFrame(info["per_class"])
    pc["total"] = pc.sum(1)
    pc["paper_table1"] = [PAPER_TABLE1[c] for c in pc.index]
    pc["diff_vs_paper"] = pc["total"] - pc["paper_table1"]
    pc.to_csv(EDA / "class_counts.csv")
    print(pc.to_string())
    info["imbalance_ratio_max_over_min"] = float(pc["total"].max() / pc["total"].min())

    fig, ax = plt.subplots(figsize=(11, 4.5))
    xs = np.arange(len(pc))
    for i, s in enumerate(["train", "val", "test"]):
        ax.bar(xs + (i - 1) * 0.27, pc[s], 0.27, label=f"{s} (n={info['n'][s]})")
    ax.set_xticks(xs, pc.index, rotation=25, ha="right")
    ax.set_ylabel("số ảnh")
    ax.set_yscale("log")
    ax.set_title("DeepWeeds fold 0: số ảnh theo lớp và tập (trục log)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(EDA / "class_distribution.png", dpi=120)
    plt.close(fig)

    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(9, 4, figsize=(8, 18))
    for c in range(9):
        files = train_df[train_df["Label"] == c]["Filename"].to_numpy()
        for j, f in enumerate(rng.choice(files, 4, replace=False)):
            axes[c, j].imshow(Image.open(img_dir / f))
            axes[c, j].axis("off")
        axes[c, 0].set_title(D.CLASS_NAMES[c], loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(EDA / "samples.png", dpi=90)
    plt.close(fig)

    sizes = {Image.open(img_dir / f).size for f in train_df["Filename"].sample(300, random_state=0)}
    modes = {Image.open(img_dir / f).mode for f in train_df["Filename"].sample(300, random_state=0)}
    info["image_sizes_sample"] = sorted(map(list, sizes))
    info["image_modes_sample"] = sorted(modes)


def pipeline_checks(img_dir: Path, train_df, val_df) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import torch
    import torch.nn.functional as F
    from model import build_model
    from train import set_seed

    out = {}
    set_seed(0)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tf_train = D.build_transforms(True, 224, "basic")
    tf_eval = D.build_transforms(False, 224)

    # 1) loss ban đầu với head mới
    loader = D.make_loader(val_df, img_dir, tf_eval, 128, False, num_workers=2)
    model = build_model("resnet50", True, 9).to(dev).eval()
    losses = []
    with torch.inference_mode():
        for b, (x, y, _) in enumerate(loader):
            losses.append(F.cross_entropy(model(x.to(dev)), y.to(dev)).item())
            if b == 3:
                break
    out["initial_loss_resnet50_pretrained_newhead"] = float(np.mean(losses))
    out["ln9"] = math.log(9)
    print(f"Loss ban đầu: {out['initial_loss_resnet50_pretrained_newhead']:.4f} (ln 9 = {math.log(9):.4f})")

    # 2) overfit một batch nhỏ (16 ảnh, không augmentation)
    ds = D.DeepWeedsDataset(train_df.groupby("Label").head(2).head(16), img_dir, tf_eval)
    x = torch.stack([ds[i][0] for i in range(len(ds))]).to(dev)
    y = torch.tensor([ds[i][1] for i in range(len(ds))], device=dev)
    model = build_model("resnet50", True, 9).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    model.train()
    curve = []
    for step in range(60):
        loss = F.cross_entropy(model(x), y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        curve.append(loss.item())
    out["overfit_16_images_loss_first_last"] = [curve[0], curve[-1]]
    print(f"Overfit 16 ảnh: loss {curve[0]:.4f} -> {curve[-1]:.6f}")

    # 3) ảnh sau augmentation (giải chuẩn hoá) kèm nhãn
    ds = D.DeepWeedsDataset(train_df.sample(12, random_state=1), img_dir, tf_train)
    mean, std = torch.tensor(D.IMAGENET_MEAN)[:, None, None], torch.tensor(D.IMAGENET_STD)[:, None, None]
    fig, axes = plt.subplots(3, 4, figsize=(10, 8))
    for a, i in zip(axes.flat, range(12)):
        img, lab, f = ds[i]
        a.imshow((img * std + mean).clamp(0, 1).permute(1, 2, 0).numpy())
        a.set_title(f"{D.CLASS_NAMES[lab]}\n{f}", fontsize=8)
        a.axis("off")
    fig.suptitle("Ảnh train sau augmentation 'basic' (đã giải chuẩn hoá) và nhãn")
    fig.tight_layout()
    fig.savefig(EDA / "augment_check.png", dpi=90)
    plt.close(fig)
    return out


def main() -> None:
    EDA.mkdir(exist_ok=True)
    img_dir = download()
    train_df, val_df, test_df = D.load_split(DATA / "labels", 0)
    info = D.check_split(train_df, val_df, test_df, img_dir)
    eda(img_dir, train_df, val_df, test_df, info)
    D.load_image_cache(img_dir)
    (EDA / "split_check.json").write_text(json.dumps(info, indent=2, ensure_ascii=False))
    checks = pipeline_checks(img_dir, train_df, val_df)
    (EDA / "pipeline_check.json").write_text(json.dumps(checks, indent=2))
    print("BƯỚC 0 XONG")


if __name__ == "__main__":
    main()
