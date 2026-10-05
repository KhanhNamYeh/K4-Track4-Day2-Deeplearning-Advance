"""Bước 1: độ trễ sơ bộ của từng backbone (batch 1, 224, FP32 và AMP; warmup 10, synchronize, 50 lần).

    python code/step1_latency.py        -> results/backbone_latency.json
Độ trễ không phụ thuộc giá trị trọng số nên dùng kiến trúc khởi tạo ngẫu nhiên (cùng head 9 lớp).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import latency_report  # noqa: E402
from experiments import BACKBONES  # noqa: E402
from model import build_model  # noqa: E402

out = []
for eid, (name, _) in BACKBONES.items():
    m = build_model(name, pretrained=False, init="scratch")
    for dtype in ("fp32", "amp"):
        r = latency_report(m, 1, 224, dtype, warmup=10, iters=50)
        out.append({"exp_id": eid, "backbone": name, **r})
        print(eid, name, dtype, f"p50 {r['p50']:.2f} ms p95 {r['p95']:.2f} ms", flush=True)
Path("results").mkdir(exist_ok=True)
Path("results/backbone_latency.json").write_text(json.dumps(out, indent=2))
