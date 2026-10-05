"""dataset.py - đọc DeepWeeds, kiểm tra chia dữ liệu, transform, DataLoader.

Giao diện (giữ nguyên theo starter):
    load_split(labels_dir, fold=0)            -> (train_df, val_df, test_df)
    check_split(train_df, val_df, test_df, images_dir) -> dict  (số liệu để ghi báo cáo)
    build_transforms(train, img_size, aug)    -> torchvision transform
    DeepWeedsDataset[i]                       -> (image_tensor, label:int, filename:str)
    make_loader(df, images_dir, transform, batch_size, train, sampler, num_workers)

Lựa chọn cài đặt:
  - Ảnh gốc 256x256 JPEG được giải mã MỘT lần thành mảng uint8 (N, 256, 256, 3) và lưu cache
    `.npy` cạnh thư mục ảnh (~3,4 GB). DataLoader đọc từ RAM nên không bị nghẽn giải mã JPEG
    trên 2 vCPU của Colab. Nội dung ảnh không đổi so với đọc trực tiếp bằng PIL.
  - Transform dùng torchvision.transforms.v2 trên tensor uint8 (CHW).
  - Val/test: ảnh 256 -> CenterCrop(img_size) (img_size=224 ở công thức nền). Không resize thêm.
"""
from __future__ import annotations

import os
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

NUM_CLASSES = 9
# Thứ tự lớp theo cột `Label` của labels.csv (0 = Chinee Apple ... 7 = Snake Weed, 8 = Negatives).
CLASS_NAMES = [
    "Chinee Apple", "Lantana", "Parkinsonia", "Parthenium", "Prickly Acacia",
    "Rubber Vine", "Siam Weed", "Snake Weed", "Negatives",
]
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
TOTAL_IMAGES = 17509
SRC_SIZE = 256


def load_split(labels_dir: str | Path, fold: int = 0):
    """Đọc train/val/test_subset{fold}.csv nguyên bản (S1). Không sửa, lọc hay chia lại."""
    labels_dir = Path(labels_dir)
    out = []
    for split in ("train", "val", "test"):
        df = pd.read_csv(labels_dir / f"{split}_subset{fold}.csv")
        assert {"Filename", "Label"} <= set(df.columns), f"{split}: thiếu cột Filename/Label"
        out.append(df)
    return tuple(out)


def check_split(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
                images_dir: str | Path, verbose: bool = True) -> dict:
    """Kiểm tra bắt buộc (README mục 2.1). Assert nếu vi phạm; trả về dict số liệu cho báo cáo."""
    sets = {"train": train_df, "val": val_df, "test": test_df}
    n = {k: int(len(v)) for k, v in sets.items()}
    total = sum(n.values())
    frac = {k: v / total for k, v in n.items()}
    per_class = {k: {CLASS_NAMES[c]: int((v["Label"] == c).sum()) for c in range(NUM_CLASSES)}
                 for k, v in sets.items()}
    names = {k: set(v["Filename"]) for k, v in sets.items()}
    for k, v in sets.items():
        assert v["Filename"].is_unique, f"{k}: có Filename trùng trong cùng một tập"
    overlap = {"train&val": len(names["train"] & names["val"]),
               "train&test": len(names["train"] & names["test"]),
               "val&test": len(names["val"] & names["test"])}
    union = len(names["train"] | names["val"] | names["test"])
    on_disk = set(os.listdir(images_dir))
    missing = sorted((names["train"] | names["val"] | names["test"]) - on_disk)

    assert all(v == 0 for v in overlap.values()), f"giao giữa các tập khác rỗng: {overlap}"
    assert union == TOTAL_IMAGES, f"hợp ba tập = {union}, kỳ vọng {TOTAL_IMAGES}"
    assert not missing, f"{len(missing)} file trong CSV không có trong {images_dir}: {missing[:5]}"
    for k, target in (("train", 0.6), ("val", 0.2), ("test", 0.2)):
        assert abs(frac[k] - target) < 0.01, f"tỉ lệ {k} = {frac[k]:.4f} lệch quá 1 điểm % khỏi {target}"

    info = {"n": n, "fraction": frac, "per_class": per_class, "overlap": overlap,
            "union": union, "missing_files": len(missing)}
    if verbose:
        print("Số ảnh:", n, "| tỉ lệ:", {k: round(v, 4) for k, v in frac.items()})
        print(pd.DataFrame(per_class).assign(total=lambda d: d.sum(1)).to_string())
        print("Giao:", overlap, "| hợp:", union, "| file thiếu:", len(missing))
    return info


def build_transforms(train: bool, img_size: int = 224, aug: str = "basic"):
    """Transform trên tensor uint8 CHW -> float chuẩn hoá.

    aug (chỉ khi train): "basic" = RandomResizedCrop + lật ngang;
      "color" = basic + ColorJitter(0.3, 0.3, 0.3); "trivial" = basic + TrivialAugmentWide;
      "randaug" = basic + RandAugment(2, 9); "basic_vflip" = basic + lật dọc.
    Eval: CenterCrop(img_size) từ ảnh 256 (nếu img_size > 256 thì resize lên img_size).
    """
    import torch
    from torchvision.transforms import v2

    tail = [v2.ToDtype(torch.float32, scale=True), v2.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    if not train:
        head = ([v2.CenterCrop(img_size)] if img_size <= SRC_SIZE
                else [v2.Resize(img_size, antialias=True)])
        return v2.Compose(head + tail)
    ops = [v2.RandomResizedCrop(img_size, antialias=True), v2.RandomHorizontalFlip()]
    if aug == "basic":
        pass
    elif aug == "color":
        ops.append(v2.ColorJitter(0.3, 0.3, 0.3))
    elif aug == "trivial":
        ops.append(v2.TrivialAugmentWide())
    elif aug == "randaug":
        ops.append(v2.RandAugment(num_ops=2, magnitude=9))
    elif aug == "basic_vflip":
        ops.append(v2.RandomVerticalFlip())
    else:
        raise ValueError(f"aug không hợp lệ: {aug}")
    return v2.Compose(ops + tail)


# --------------------------------------------------------------------------- #
# Cache ảnh uint8 trong RAM
# --------------------------------------------------------------------------- #
_CACHE: dict[str, tuple[np.ndarray, dict]] = {}


def _decode(path: Path) -> np.ndarray:
    from PIL import Image
    with Image.open(path) as im:
        im = im.convert("RGB")
        if im.size != (SRC_SIZE, SRC_SIZE):
            im = im.resize((SRC_SIZE, SRC_SIZE), Image.BILINEAR)
        return np.asarray(im, dtype=np.uint8)


def load_image_cache(images_dir: str | Path) -> tuple[np.ndarray, dict]:
    """Trả về (mảng uint8 [N, 256, 256, 3], {filename: index}). Tạo cache .npy ở lần đầu."""
    images_dir = Path(images_dir)
    key = str(images_dir.resolve())
    if key in _CACHE:
        return _CACHE[key]
    files = sorted(f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    cache_file = images_dir.parent / f"{images_dir.name}_uint8_{len(files)}.npy"
    if cache_file.exists():
        arr = np.load(cache_file, mmap_mode="r")
        arr = np.ascontiguousarray(arr)  # nạp hẳn vào RAM
    else:
        print(f"Giải mã {len(files)} ảnh vào cache {cache_file} (chỉ chạy một lần)...")
        arr = np.empty((len(files), SRC_SIZE, SRC_SIZE, 3), dtype=np.uint8)
        with ThreadPoolExecutor(max_workers=8) as ex:
            for i, a in enumerate(ex.map(_decode, (images_dir / f for f in files))):
                arr[i] = a
        tmp = cache_file.with_suffix(".tmp.npy")
        np.save(tmp, arr)
        tmp.rename(cache_file)
    index = {f: i for i, f in enumerate(files)}
    _CACHE[key] = (arr, index)
    return arr, index


try:
    from torch.utils.data import Dataset as _TorchDataset
except ImportError:  # để module import được khi không có torch
    _TorchDataset = object


class DeepWeedsDataset(_TorchDataset):
    """Dataset theo DataFrame (Filename, Label); __getitem__ -> (tensor đã transform, nhãn, tên file)."""

    def __init__(self, df: pd.DataFrame, images_dir: str | Path, transform=None, cache: bool = True):
        self.df = df.reset_index(drop=True)
        self.images_dir = Path(images_dir)
        self.transform = transform
        self.filenames = self.df["Filename"].tolist()
        self.labels = self.df["Label"].astype(int).to_numpy()
        self.cache = cache
        if cache:
            arr, index = load_image_cache(self.images_dir)
            self._arr = arr
            self._idx = np.array([index[f] for f in self.filenames], dtype=np.int64)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, i: int):
        import torch
        if self.cache:
            img = torch.from_numpy(np.array(self._arr[self._idx[i]])).permute(2, 0, 1)
        else:
            img = torch.from_numpy(_decode(self.images_dir / self.filenames[i]).copy()).permute(2, 0, 1)
        if self.transform is not None:
            img = self.transform(img)
        return img, int(self.labels[i]), self.filenames[i]


def seed_worker(worker_id: int) -> None:
    import torch
    s = torch.initial_seed() % 2**32
    np.random.seed(s)
    random.seed(s)


def make_loader(df: pd.DataFrame, images_dir: str | Path, transform, batch_size: int,
                train: bool, sampler: str | None = None, num_workers: int = 2, seed: int = 0):
    """DataLoader. train=False giữ đúng thứ tự df. sampler="balanced": WeightedRandomSampler 1/n_c."""
    import torch
    from torch.utils.data import DataLoader, WeightedRandomSampler

    ds = DeepWeedsDataset(df, images_dir, transform)
    g = torch.Generator()
    g.manual_seed(seed)
    smp = None
    if train and sampler == "balanced":
        counts = np.bincount(ds.labels, minlength=NUM_CLASSES).astype(np.float64)
        w = 1.0 / counts[ds.labels]
        smp = WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double), num_samples=len(ds),
                                    replacement=True, generator=g)
    elif sampler not in (None, "none", "balanced"):
        raise ValueError(f"sampler không hợp lệ: {sampler}")
    return DataLoader(
        ds, batch_size=batch_size, shuffle=(train and smp is None), sampler=smp,
        drop_last=train, num_workers=num_workers, pin_memory=torch.cuda.is_available(),
        worker_init_fn=seed_worker, generator=g, persistent_workers=num_workers > 0,
    )
