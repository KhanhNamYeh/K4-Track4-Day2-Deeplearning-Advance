# Báo cáo tạm: Lab Day 2, DeepWeeds (Nguyễn Đăng Nam Khanh, 2A202602741)

> **Đây là báo cáo TẠM, nộp sớm theo tiến độ hiện có. Bài lab CHƯA hoàn thành.** Mới xong Bước 0 (EDA, kiểm tra pipeline) và Bước 1 (so sánh 6 backbone). Chưa làm Bước 2 (công thức huấn luyện), Bước 3 (suy luận), Bước 4 (chung kết 3 seed và test). **Tập test chưa được dùng lần nào**; không có số nào trong báo cáo này đến từ test.

## 1. Tóm tắt

Trên DeepWeeds fold 0 (9 lớp), với cùng một công thức nền (AdamW, LR backbone 1e-4 / head 1e-3, cosine, 10 epoch, AMP, cross-entropy, 1 seed), **ConvNeXt-Tiny (trọng số `in12k_ft_in1k`) cho macro-F1 val cao nhất: 0,9676** (top-1 val 0,9760), tiếp theo là Swin-T (0,9575) và DeiT-S (0,9486). ResNet-50 (tag `a1_in1k`) chỉ đạt 0,7841, hai mạng nhẹ EfficientNet-B0 và MobileNetV3-L đạt 0,7241 và 0,6003. Lớp khó nhất vẫn là Chinee Apple (recall val 0,884 ở ConvNeXt-T) và Snake Weed (0,931). Chênh lệch giữa ba mô hình đầu (cách nhau 0,009 đến 0,019) **chưa đủ bằng chứng để xếp hạng** vì mới có 1 seed.

## 2. Dữ liệu và thiết lập

- **Dữ liệu:** DeepWeeds, 17.509 ảnh RGB 256×256 (mẫu 300 ảnh train đều có kích thước 256×256), MD5 `images.zip` đúng (`b7b30f96…`). Dùng đúng `train/val/test_subset0.csv` của tác giả, không sửa.
- **Kiểm tra chia dữ liệu (README 2.1), đã chạy và đạt:** train 10.501 / val 3.501 / test 3.507 ảnh (59,97% / 20,00% / 20,03%); giao train∩val, train∩test, val∩test đều bằng 0; hợp ba tập đúng 17.509; mọi file trong CSV đều có trên đĩa. Chi tiết: `eda/split_check.json`, `eda/class_counts.csv`.
- **EDA:** số ảnh theo lớp khớp Table 1 của bài báo, trừ lệch ±1 ảnh ở hai lớp (Chinee Apple 1.126 so với 1.125; Lantana 1.063 so với 1.064; chưa rõ nguyên nhân, có thể do cách bài báo làm tròn hoặc làm sạch). `Negatives` chiếm 9.106 ảnh (52,0%), lớp lớn nhất gấp 9,0 lần lớp nhỏ nhất, nên top-1 bị lớp này kéo cao, vì vậy macro-F1 là chỉ số chính. Biểu đồ: `eda/class_distribution.png`; ảnh mẫu 4 ảnh mỗi lớp: `eda/samples.png`.
- **Kiểm tra pipeline (GUIDE 1.3):** loss ban đầu với head mới = 2,180 (ln 9 = 2,197); overfit 16 ảnh: loss 2,218 → 0,00015 sau 60 bước; ảnh sau augmentation đã giải chuẩn hoá khớp nhãn (`eda/augment_check.png`). Kết quả: `eda/pipeline_check.json`. `model.eval()` được dùng trong mọi lần đánh giá; test unit của focal γ=0 ≡ CE, label smoothing, CutMix/Mixup, nhóm tham số không weight decay cho norm/bias, gộp BN, temperature scaling, lịch LR, EMA: 16 test đều đạt (`code/test_code.py`).
- **Công thức nền (giống nhau cho 6 backbone):** tinh chỉnh toàn bộ từ trọng số ImageNet, `RandomResizedCrop(224)` + lật ngang; đánh giá: `CenterCrop(224)` từ ảnh 256; chuẩn hoá mean/std ImageNet; AdamW, LR backbone 1e-4 và head 1e-3, weight decay 0,05 (0 cho norm/bias), warmup 1 epoch + cosine theo bước, batch 64, AMP, **10 epoch** (GUIDE gợi ý 10–15; chọn 10 vì ngân sách Colab miễn phí), seed 0; chọn checkpoint theo macro-F1 val cao nhất.
- **Môi trường:** Colab Free, Tesla T4, Python 3.13, torch 2.11.0+cu130, torchvision 0.26.0, timm 1.0.29. `cudnn.benchmark` bật nên kết quả không lặp lại từng bit (một lần chạy lại B03 cho 0,9486 thay vì 0,9503).

## 3. So sánh backbone (Bước 1, 1 seed, val)

| Mã | Backbone (tag trọng số) | Tham số (M) | GMAC | Macro-F1 val | Top-1 val | Epoch tốt nhất | Thời gian train / epoch (s) | Độ trễ batch 1, FP32 p50 / p95 / p99 (ms) |
|---|---|---|---|---|---|---|---|---|
| B01 | resnet50 (`a1_in1k`) | 23,5 | 4,09 | 0,7841 | 0,8429 | 10 | 34 | 7,74 / 11,89 / 12,05 |
| **B02** | **convnext_tiny (`in12k_ft_in1k`)** | 27,8 | 4,45 | **0,9676** | **0,9760** | 9 | 47 | 5,70 / 8,00 / 8,04 |
| B03 | deit_small_patch16_224 (`fb_in1k`) | 21,7 | 4,24 | 0,9486 | 0,9643 | 9 | 31 | 5,01 / 5,38 / 6,22 |
| B04 | swin_tiny_patch4_window7_224 (`ms_in1k`) | 27,5 | 4,49 | 0,9575 | 0,9683 | 9 | 59 | 13,81 / 18,29 / 20,19 |
| B05 | efficientnet_b0 (`ra_in1k`) | 4,0 | 0,38 | 0,7241 | 0,8023 | 7 | 30 | 8,18 / 9,79 / 10,54 |
| B06 | mobilenetv3_large_100 (`ra_in1k`) | 4,2 | 0,22 | 0,6003 | 0,7238 | 10 | 24 | 6,59 / 9,43 / 12,03 |

Nguồn: `runs/B0x/seed0/summary.json`, `history.csv`; ảnh training: `curves/B0x_*.png`. Số tham số ResNet-50 là 23,5M vì head 9 lớp thay head 1000 lớp.

**Điều kiện đo độ trễ (sơ bộ):** Tesla T4, batch 1, 224×224, FP32, torch 2.11.0+cu130, warmup 10 lần, `torch.cuda.synchronize()` trước và sau mỗi lần đo, 50 lần đo, không tính tiền xử lý, dùng kiến trúc khởi tạo ngẫu nhiên (độ trễ không phụ thuộc giá trị trọng số). Ở batch 1, AMP **chậm hơn** FP32 trên cả 6 backbone trừ ResNet-50 (B01: 6,92 so với 7,74 ms p50); số AMP nằm trong `results/backbone_latency.json`. Batch lớn chưa đo.

### Nhận xét

1. **ConvNeXt-T tốt nhất và nhanh (p95 8,0 ms)**, nên được chọn để đi tiếp. Lưu ý đây là bộ trọng số ImageNet-12k fine-tune, được tiền huấn luyện trên nhiều dữ liệu hơn các tag còn lại, nên lợi thế có thể đến từ **trọng số chứ không chỉ kiến trúc** (GUIDE câu hỏi 9.1). Chưa kiểm chứng được vì mỗi kiến trúc mới thử một tag.
2. **Ba mô hình đầu chưa phân biệt được.** B02, B04, B03 cách nhau 0,009 và 0,010 điểm macro-F1, mà slide ước độ lệch chuẩn theo seed khoảng 0,1 điểm phần trăm cho ResNet-50 trên tập lớn hơn, còn DeepWeeds nhỏ hơn nên nhiễu có thể lớn hơn. Chưa có std của riêng bài này (cần ≥ 3 seed). Có thể nói chắc hơn ở chênh lệch lớn: B02/B03/B04 vượt B01, B05, B06 hàng chục điểm.
3. **ResNet-50 thấp bất thường (0,7841).** Một giả thuyết là tag `a1_in1k` được huấn luyện bằng công thức BCE (ResNet strikes back), có thể không hợp với tinh chỉnh ngắn 10 epoch bằng cross-entropy và LR 1e-4. **Chưa kiểm chứng**; cần thử tag khác (ví dụ `tv_in1k`) hoặc LR khác trước khi kết luận về kiến trúc ResNet. Đường cong B01 vẫn đang tăng chậm ở epoch 10, nên 10 epoch chưa đủ cho mô hình này.
4. **Hai mạng nhẹ kém rõ rệt (0,72 và 0,60) và có dấu hiệu chưa hội tụ/quá khớp:** train loss 0,26 nhưng val loss 0,65 và 0,85, ECE 0,055 và 0,053 (gấp khoảng 6 lần ConvNeXt-T), F1 val dao động giữa các epoch (xem `curves/B05`, `B06`). Giả thuyết: LR backbone 1e-4 thấp so với nhu cầu của các mạng nhỏ dùng BatchNorm và tag `ra_in1k`; chưa kiểm chứng. Vì vậy **không nên kết luận "mạng nhẹ không dùng được cho DeepWeeds"**, chỉ có thể nói "ở công thức nền này thì kém".
5. **FLOPs không dự đoán độ trễ:** MobileNetV3-L có ít GMAC nhất (0,22) nhưng độ trễ p50 (6,59 ms) lớn hơn DeiT-S (5,01 ms, 4,24 GMAC). Swin-T chậm nhất (13,81 ms) do attention cửa sổ và các thao tác dịch/xếp lại. Điều này khớp với ý của slide (FLOPs không phải độ trễ).
6. **Quá khớp:** ConvNeXt-T, DeiT-S, Swin-T có train loss 0,04 đến 0,07 và val loss 0,10 đến 0,13 ở epoch 10, khoảng cách vừa phải; val F1 ổn định từ epoch 7 trở đi.

## 4. Phân tích lỗi sơ bộ (ConvNeXt-T, B02, val)

Ma trận nhầm lẫn trên val (`predictions/B02_seed0_val.csv`, hàng = nhãn thật):

- **F1 theo lớp:** Chinee Apple 0,932, Snake Weed 0,926 (hai lớp thấp nhất), các lớp còn lại 0,965 đến 0,990.
- **Chinee Apple (225 ảnh val):** recall 0,884; 8 ảnh bị đoán thành Snake Weed, 13 thành Negatives, 4 thành Lantana.
- **Snake Weed (203 ảnh val):** recall 0,931; 3 ảnh bị đoán thành Chinee Apple, 5 thành Negatives.
- **Cặp Chinee Apple ↔ Snake Weed** (khó nhất theo bài báo gốc) có 8 + 3 = 11 lỗi, không phải nguồn lỗi lớn nhất của Chinee Apple: lỗi chính là bị gán nhầm sang `Negatives` (13 ảnh). Giả thuyết: nhiều ảnh cỏ dại có cây mục tiêu nhỏ, bị che hoặc nằm trong bóng nên giống ảnh nền; **chưa xem trực tiếp các ảnh bị đoán sai** nên đây mới là giả thuyết.
- Recall val của B02 là 0,884 (Chinee Apple) và 0,931 (Snake Weed). Các số này **trên val, 1 seed, chỉ để tham khảo**, không so sánh trực tiếp với mốc 88,5% và 88,8% của bài báo (mốc đó tính theo định nghĩa khác, trên test, và huấn luyện khác nhiều).
- **Hiệu chuẩn:** ECE val của B02 là 0,0092 (chưa temperature scaling; 15 bin).

## 5. Việc chưa làm và hạn chế (nêu thẳng)

- **Chưa làm:** Bước 2 (≥ 3 trục công thức huấn luyện), Bước 3 (≥ 4 phương pháp suy luận, hiệu chuẩn T, độ trễ đầy đủ batch 1 và batch lớn, đường đánh đổi), Bước 4 (3 seed cho cấu hình cuối và mốc `T00`/`I00`, chạy test một lần mỗi seed, `predictions/*_test.csv`, `eval.py score/grade`), `results.xlsx`, README riêng có link notebook chạy lại. Vì thiếu Bước 4, **phần I của RUBRIC (chất lượng model trên test) chưa có số nào**, và theo điều kiện tiên quyết P1, P4 thì bài chưa đủ sản phẩm để chấm.
- **Chỉ 1 seed** cho mọi số trong báo cáo; chưa có std, nên mọi chênh lệch nhỏ đều không kết luận được.
- **Chọn backbone chỉ dựa trên val** (đúng S2/S4); test chưa được mở. `T00` (nền trên ConvNeXt-T) chưa chạy nên chưa có mốc cho phần so sánh cải thiện.
- **Công bằng giữa backbone chưa trọn vẹn:** mỗi kiến trúc dùng tag trọng số mặc định của `timm` (khác công thức và dữ liệu tiền huấn luyện), cùng một LR cho tất cả; kết quả B01, B05, B06 có thể thấp do LR và tag chứ không phải do kiến trúc.
- **Ngân sách tính toán:** dùng Colab miễn phí, VM bị ngắt nhiều lần (khoảng sau 1 giờ, lần cuối chỉ ~13 phút), mất khoảng 40 phút GPU và chưa chạy được `T00`. Epoch giảm xuống 10. Checkpoint không lưu về máy (chỉ giữ log, logit val, dự đoán val, đường cong), nên Bước 3 sẽ phải huấn luyện lại mô hình được chọn.
- **Chia ngẫu nhiên không theo địa điểm** (bài báo gốc) nên điểm test sau này có thể lạc quan so với địa điểm mới; một fold duy nhất.

## 6. Kế hoạch hoàn thành

1. Tạo lại VM (Colab khi hạn mức hồi, hoặc Kaggle) và chạy `T00` rồi các ablation trên ConvNeXt-T: khởi tạo (scratch, frozen), augmentation (color, TrivialAugment, CutMix), loss (label smoothing, focal, trọng số lớp), sampler cân bằng, LR đồng nhất, EMA, mỗi lần chỉ đổi một yếu tố so với `T00`.
2. Bước 3: TTA lật, 5 crop/đa tỉ lệ, gộp xác suất so với logit, dò độ phân giải, ensemble, temperature scaling (T khớp trên val), gộp BN/FP16; đo độ trễ p50/p95/p99 ở batch 1 và batch 32.
3. Bước 4: chốt cấu hình trên val, chạy cấu hình cuối và mốc `T00`/`I00` với 3 seed, test một lần mỗi seed, rồi `eval.py score` và `grade`.
4. Hoàn thiện `results.xlsx`, ảnh curves cho mọi `exp_id`, báo cáo cuối, README riêng.

## Phụ lục: cấu trúc file đã có

- `code/`: `dataset.py`, `model.py`, `losses.py`, `train.py`, `inference.py`, `benchmark.py`, `experiments.py`, `step0_prepare.py`, `step1_latency.py`, `step3_inference.py` (chưa chạy), `test_code.py`. `eval.py` gốc không sửa.
- `eda/`, `curves/B01…B06`, `predictions/B0x_seed0_val.csv` (chỉ val), `runs/B0x/seed0/`, `results/backbone_latency.json`, `logs/`.
- Không có checkpoint, dataset hay file test nào trong thư mục này.
