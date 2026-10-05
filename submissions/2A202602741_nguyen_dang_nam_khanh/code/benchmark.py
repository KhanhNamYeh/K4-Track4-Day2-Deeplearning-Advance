"""benchmark.py - đo độ trễ suy luận đúng cách (slide trang 73, 75; GUIDE.md mục 4.1).

Quy tắc: warmup >= 10 lần bỏ đi; torch.cuda.synchronize() trước và sau mỗi lần đo; >= 50 lần;
báo cáo p50/p95/p99. KHÔNG tính tiền xử lý (đầu vào là tensor ngẫu nhiên đã nằm sẵn trên GPU),
chỉ đo forward của model.
"""
from __future__ import annotations

import time

import numpy as np


def bench(fn, warmup: int = 10, iters: int = 100, sync=None) -> dict:
    """Đo `fn()` (mili-giây): warmup rồi `iters` lần, mỗi lần sync trước/sau."""
    for _ in range(warmup):
        fn()
    if sync:
        sync()
    times = []
    for _ in range(iters):
        if sync:
            sync()
        t0 = time.perf_counter()
        fn()
        if sync:
            sync()
        times.append((time.perf_counter() - t0) * 1000.0)
    t = np.asarray(times)
    return {"p50": float(np.percentile(t, 50)), "p95": float(np.percentile(t, 95)),
            "p99": float(np.percentile(t, 99)), "mean": float(t.mean()), "n": iters}


def latency_report(model, batch_size: int, img_size: int, dtype: str = "fp32", device: str = "cuda",
                   warmup: int = 10, iters: int = 100, fused_bn: bool = False, views: int = 1) -> dict:
    """Độ trễ forward với đầu vào (batch_size, 3, img_size, img_size). dtype: fp32 | amp | fp16.
    `views` > 1 mô phỏng TTA: chạy K lượt forward nối tiếp trong một lần đo."""
    import copy

    import torch
    dev = torch.device(device if (device != "cuda" or torch.cuda.is_available()) else "cpu")
    m = copy.deepcopy(model).to(dev).eval()
    x = torch.randn(batch_size, 3, img_size, img_size, device=dev)
    if dtype == "fp16":
        m = m.half()
        x = x.half()
    m = m.to(memory_format=torch.channels_last)
    x = x.contiguous(memory_format=torch.channels_last)

    def fn():
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16,
                                                     enabled=(dtype == "amp" and dev.type == "cuda")):
            for _ in range(views):
                m(x)

    sync = torch.cuda.synchronize if dev.type == "cuda" else None
    r = bench(fn, warmup, iters, sync)
    del m
    return {"gpu": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu", "dtype": dtype,
            "batch": batch_size, "img_size": img_size, "fused_bn": fused_bn, "views": views,
            "p50": r["p50"], "p95": r["p95"], "p99": r["p99"], "mean": r["mean"], "n": r["n"],
            "images_per_s": batch_size / (r["p50"] / 1000.0), "torch": torch.__version__}


def tta_latency(model, k_views: int, **kw) -> dict:
    """Độ trễ TTA K view (đo thật) kèm tỉ lệ so với K x p50 của một lượt."""
    one = latency_report(model, views=1, **kw)
    k = latency_report(model, views=k_views, **kw)
    k["ratio_vs_k_times_single"] = k["p50"] / (k_views * one["p50"])
    return k
