"""Kiểm tra tự viết cho các phần dễ sai (RUBRIC mục H). Chạy trên CPU:
    cd code && python test_code.py -v
(không dùng `python -m unittest code/...` vì tên thư mục `code` trùng module chuẩn của Python)
"""
import sys
import unittest
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parent))

import inference as I  # noqa: E402
import losses as L  # noqa: E402
import model as M  # noqa: E402
import train as T  # noqa: E402


class TestLosses(unittest.TestCase):
    def setUp(self):
        g = torch.Generator().manual_seed(0)
        self.logits = torch.randn(64, 9, generator=g) * 3
        self.y = torch.randint(0, 9, (64,), generator=g)

    def test_focal_gamma0_equals_ce(self):
        ce = nn.CrossEntropyLoss()(self.logits, self.y)
        fl = L.FocalLoss(gamma=0.0)(self.logits, self.y)
        self.assertLess(abs(ce.item() - fl.item()), 1e-6)

    def test_focal_downweights_easy(self):
        self.assertLess(L.FocalLoss(2.0)(self.logits, self.y).item(),
                        nn.CrossEntropyLoss()(self.logits, self.y).item())

    def test_label_smoothing(self):
        ce = nn.CrossEntropyLoss()(self.logits, self.y)
        self.assertLess(abs(L.LabelSmoothingCE(0.0)(self.logits, self.y).item() - ce.item()), 1e-6)
        ref = nn.CrossEntropyLoss(label_smoothing=0.1)(self.logits, self.y)
        self.assertLess(abs(L.LabelSmoothingCE(0.1)(self.logits, self.y).item() - ref.item()), 1e-5)

    def test_class_weights(self):
        w = L.class_weights([100, 10, 10], beta=0.0)
        self.assertAlmostEqual(w.mean().item(), 1.0, places=5)
        self.assertAlmostEqual(w[1].item() / w[0].item(), 10.0, places=4)
        wb = L.class_weights([100, 10, 10], beta=0.999)
        self.assertAlmostEqual(wb.sum().item(), 3.0, places=5)
        self.assertGreater(wb[1].item(), wb[0].item())

    def test_cutmix_lam_matches_area(self):
        x = torch.zeros(8, 3, 32, 32)
        x[4:] = 1.0
        y = torch.arange(8)
        for s in range(20):
            xm, (ya, yb, lam) = L.mix_batch(x, y, 1.0, "cutmix", rng=np.random.default_rng(s))
            # pixel đến từ ảnh khác chiếm đúng (1 - lam) diện tích
            changed = (xm != x).float().mean(dim=(1, 2, 3))
            differs = (x[yb] != x).flatten(1).any(1)
            for i in torch.nonzero(differs).flatten():
                self.assertAlmostEqual(changed[i].item(), 1 - lam, places=5)
            self.assertTrue(torch.equal(ya, y))

    def test_mixup_and_mixed_loss(self):
        x = torch.randn(8, 3, 4, 4)
        y = torch.arange(8) % 9
        xm, (ya, yb, lam) = L.mix_batch(x, y, 0.4, "mixup", rng=np.random.default_rng(1))
        perm_x = (xm - lam * x) / (1 - lam)
        # perm_x phải là hoán vị của x
        self.assertTrue(any(torch.allclose(perm_x[0], x[j], atol=1e-5) for j in range(8)))
        ce = nn.CrossEntropyLoss()
        lg = torch.randn(8, 9)
        v = L.mixed_loss(ce, lg, (ya, yb, lam)).item()
        self.assertAlmostEqual(v, lam * ce(lg, ya).item() + (1 - lam) * ce(lg, yb).item(), places=5)


class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = M.build_model("resnet18", pretrained=False, init="scratch")

    def test_param_groups_no_decay_on_norm_bias(self):
        groups = M.param_groups(self.m, 1e-4, 1e-3, 0.05)
        by = {g["name"]: g for g in groups}
        self.assertTrue(all(p.ndim <= 1 for p in by["backbone_no_decay"]["params"]))
        self.assertEqual(by["backbone_no_decay"]["weight_decay"], 0.0)
        self.assertEqual(by["head_decay"]["lr"], 1e-3)
        n = sum(p.numel() for g in groups for p in g["params"])
        self.assertEqual(n, sum(p.numel() for p in self.m.parameters()))

    def test_freeze_keeps_bn_eval(self):
        m = M.build_model("resnet18", pretrained=False, init="frozen")
        trainable = [p for p in m.parameters() if p.requires_grad]
        self.assertEqual(sum(p.numel() for p in trainable), 512 * 9 + 9)
        M.set_train_mode(m)
        self.assertFalse(m.bn1.training)
        self.assertTrue(m.get_classifier().training)

    def test_gmacs(self):
        g = M.count_gmacs(self.m, 224)
        self.assertTrue(1.7 < g < 1.9, g)  # resnet18 ~1.8 GMAC

    def test_fuse_conv_bn_exact(self):
        m = M.build_model("resnet18", pretrained=False, init="scratch").eval()
        # thống kê BN khác mặc định để phép gộp có ý nghĩa
        for mod in m.modules():
            if isinstance(mod, nn.BatchNorm2d):
                mod.running_mean.uniform_(-0.5, 0.5)
                mod.running_var.uniform_(0.5, 2.0)
                mod.weight.data.uniform_(0.5, 1.5)
        fused = I.fuse_conv_bn(m)
        self.assertGreater(fused.n_fused, 15)
        self.assertFalse(any(isinstance(x, nn.BatchNorm2d) for x in fused.modules()))
        self.assertLess(I.check_fusion(m, fused, 64), 1e-4)


class TestInference(unittest.TestCase):
    def test_temperature_recovers_scale(self):
        rng = np.random.default_rng(0)
        true = rng.normal(size=(4000, 9)) * 2
        y = np.array([rng.choice(9, p=p) for p in I._softmax(true)])
        T = I.fit_temperature(true * 3.0, y)  # logit bị phóng đại 3 lần -> T ≈ 3
        self.assertAlmostEqual(T, 3.0, delta=0.25)
        p = I.apply_temperature(true, 1.0)
        np.testing.assert_allclose(p.sum(1), 1.0)

    def test_aggregate(self):
        a, b = np.random.randn(5, 9), np.random.randn(5, 9)
        for s in ("prob", "logit"):
            np.testing.assert_allclose(I.aggregate_views([a, b], s).sum(1), 1.0)
        np.testing.assert_allclose(I.aggregate_views([a, a], "logit"), I._softmax(a))

    def test_views(self):
        x = torch.randn(2, 3, 256, 256)
        v = I.views_multicrop(x, 224)
        self.assertEqual(len(v), 5)
        self.assertEqual(v[0].shape[-1], 224)
        self.assertTrue(torch.equal(I.view_hflip(I.view_hflip(x)), x))


class TestTrainHelpers(unittest.TestCase):
    def test_parse_overrides(self):
        d = T.parse_overrides(["seed=1", "loss=focal", "ema_decay=none", "lr_head=3e-3",
                               "save_test_predictions=true", "sampler=balanced"])
        self.assertEqual(d, {"seed": 1, "loss": "focal", "ema_decay": None, "lr_head": 3e-3,
                             "save_test_predictions": True, "sampler": "balanced"})
        with self.assertRaises(KeyError):
            T.parse_overrides(["nope=1"])

    def test_scheduler_shape(self):
        p = nn.Parameter(torch.zeros(1))
        opt = torch.optim.AdamW([{"params": [p], "lr": 1e-3}])
        cfg = T.Config(epochs=4, warmup_epochs=1)
        sch = T.build_scheduler(opt, cfg, 10)
        lrs = []
        for _ in range(40):
            lrs.append(opt.param_groups[0]["lr"])
            opt.step()
            sch.step()
        self.assertAlmostEqual(max(lrs), 1e-3, places=8)
        self.assertEqual(int(np.argmax(lrs)), 9)       # đỉnh ở cuối warmup
        self.assertLess(lrs[-1], 1e-5)                  # cosine về gần 0

    def test_ema(self):
        m = nn.Linear(2, 2)
        ema = T.EMA(m, 0.5)
        with torch.no_grad():
            m.weight.add_(1.0)
        ema.update(m)  # decay hiệu dụng min(0.5, 2/11)
        d = 2 / 11
        self.assertTrue(torch.allclose(ema.module.weight, m.weight - d * 1.0))


if __name__ == "__main__":
    unittest.main()
