# Báo cáo tạm (bản cập nhật 2): Lab Day 2, DeepWeeds (Nguyễn Đăng Nam Khanh, 2A202602741)

> **Đây là báo cáo TẠM. Bài lab CHƯA hoàn thành.** Đã xong: Bước 0 (EDA, kiểm tra pipeline), Bước 1 (6 backbone), và **một phần Bước 2** (5 ablation T01–T05, chạy trên trục khởi tạo và trục augmentation). Chưa làm: ablation loss/sampler/LR/EMA (T06–T11; T06 bị ngắt giữa chừng và không có kết quả), Bước 3 (suy luận), Bước 4 (3 seed + test). **Tập test chưa được dùng lần nào**; mọi số trong báo cáo là **macro-F1/top-1 trên val, 1 seed (seed 0)**.

## 1. Tóm tắt

Trên DeepWeeds fold 0 (9 lớp), với công thức nền (AdamW, LR backbone 1e-4 / head 1e-3, cosine, 10 epoch, AMP, cross-entropy):

- **Backbone (Bước 1):** ConvNeXt-Tiny (trọng số `in12k_ft_in1k`) cho macro-F1 val cao nhất, **0,9676**, trước Swin-T (0,9575) và DeiT-S (0,9486). ResNet-50 (`a1_in1k`) chỉ 0,7841; EfficientNet-B0 và MobileNetV3-L 0,7241 và 0,6003.
- **Khởi tạo (trục A, trên ConvNeXt-T):** đây là yếu tố có tác động lớn nhất đã đo: huấn luyện từ đầu chỉ đạt **0,2999** (−0,668) và đóng băng backbone chỉ train head đạt **0,8433** (−0,124). Tinh chỉnh toàn bộ từ trọng số tiền huấn luyện vượt xa hai cách còn lại, và chênh lệch này lớn hơn mọi nhiễu hợp lý.
- **Augmentation (trục B):** ColorJitter −0,0045, TrivialAugment +0,0027, CutMix **+0,0054** (cao nhất, 0,9730) so với nền. Cả ba chênh lệch đều **nhỏ và chỉ từ 1 seed**, nên **chưa phân biệt được** với nền; chưa kết luận kỹ thuật nào giúp ích. Có một dấu hiệu đáng kiểm tra lại bằng nhiều seed: TrivialAugment và CutMix cùng nâng recall val của Chinee Apple từ 0,884 lên 0,933.

## 2. Dữ liệu và thiết lập

- **Dữ liệu:** DeepWeeds, 17.509 ảnh RGB 256×256 (mẫu 300 ảnh train đều 256×256), MD5 `images.zip` đúng (`b7b30f96…`). Dùng đúng `train/val/test_subset0.csv` của tác giả, không sửa.
- **Kiểm tra chia dữ liệu (README 2.1), đã chạy và đạt:** train 10.501 / val 3.501 / test 3.507 ảnh (59,97% / 20,00% / 20,03%); giao train∩val, train∩test, val∩test đều bằng 0; hợp ba tập đúng 17.509; mọi file trong CSV đều có trên đĩa (`eda/split_check.json`, `eda/class_counts.csv`).
- **EDA:** số ảnh theo lớp khớp Table 1 của bài báo, trừ lệch ±1 ở hai lớp (Chinee Apple 1.126 so với 1.125; Lantana 1.063 so với 1.064; chưa rõ nguyên nhân). `Negatives` chiếm 9.106 ảnh (52,0%); lớp lớn nhất gấp 9,0 lần lớp nhỏ nhất, nên top-1 bị lớp này kéo cao và macro-F1 được dùng làm chỉ số chính (`eda/class_distribution.png`, `eda/samples.png`).
- **Kiểm tra pipeline (GUIDE 1.3):** loss ban đầu với head mới = 2,180 (ln 9 = 2,197); overfit 16 ảnh: loss 2,218 → 0,00015 sau 60 bước; ảnh sau augmentation đã giải chuẩn hoá khớp nhãn (`eda/augment_check.png`, `eda/pipeline_check.json`). `model.eval()` dùng trong mọi lần đánh giá. 16 test tự viết đều đạt (focal γ=0 ≡ CE, label smoothing, CutMix/Mixup trộn cả nhãn và `lam` theo diện tích thực, nhóm tham số không weight decay cho norm/bias, gộp BN, temperature scaling, lịch LR, EMA) trong `code/test_code.py`.
- **Công thức nền `T00` (giống nhau cho mọi backbone và mọi ablation):** tinh chỉnh toàn bộ từ trọng số ImageNet; train `RandomResizedCrop(224)` + lật ngang; đánh giá `CenterCrop(224)` từ ảnh 256; chuẩn hoá mean/std ImageNet; AdamW, LR backbone 1e-4 và head 1e-3, weight decay 0,05 (0 cho norm/bias), warmup 1 epoch + cosine theo bước, batch 64, AMP, **10 epoch** (GUIDE gợi ý 10–15; chọn 10 vì ngân sách Colab miễn phí), seed 0; chọn checkpoint theo macro-F1 val cao nhất (hòa lấy epoch sớm hơn).
- **Môi trường:** Colab Free, Tesla T4, Python 3.13, torch 2.11.0+cu130, torchvision 0.26.0, timm 1.0.29. Các lần chạy dùng hai tài khoản Google khác nhau vì hạn mức GPU (B01–B06 và T00 trên các VM khác nhau; chi tiết trong `logs/`). `cudnn.benchmark` bật nên kết quả không lặp lại từng bit; tuy vậy `T00` chạy lại cho đúng cùng kết quả với `B02` (0,9676, epoch 9), còn một lần chạy lại `B03` cho 0,9486 thay vì 0,9503. Đây chỉ là độ lặp lại **cùng seed**, không phải nhiễu **giữa các seed**, mà bài này chưa đo.

## 3. So sánh backbone (Bước 1, 1 seed, val)

| Mã | Backbone (tag trọng số) | Tham số (M) | GMAC | Macro-F1 val | Top-1 val | Epoch tốt nhất | Train / epoch (s) | Độ trễ batch 1, FP32 p50 / p95 / p99 (ms) |
|---|---|---|---|---|---|---|---|---|
| B01 | resnet50 (`a1_in1k`) | 23,5 | 4,09 | 0,7841 | 0,8429 | 10 | 34 | 7,74 / 11,89 / 12,05 |
| **B02** | **convnext_tiny (`in12k_ft_in1k`)** | 27,8 | 4,45 | **0,9676** | **0,9760** | 9 | 47 | 5,70 / 8,00 / 8,04 |
| B03 | deit_small_patch16_224 (`fb_in1k`) | 21,7 | 4,24 | 0,9486 | 0,9643 | 9 | 31 | 5,01 / 5,38 / 6,22 |
| B04 | swin_tiny_patch4_window7_224 (`ms_in1k`) | 27,5 | 4,49 | 0,9575 | 0,9683 | 9 | 59 | 13,81 / 18,29 / 20,19 |
| B05 | efficientnet_b0 (`ra_in1k`) | 4,0 | 0,38 | 0,7241 | 0,8023 | 7 | 30 | 8,18 / 9,79 / 10,54 |
| B06 | mobilenetv3_large_100 (`ra_in1k`) | 4,2 | 0,22 | 0,6003 | 0,7238 | 10 | 24 | 6,59 / 9,43 / 12,03 |

Nguồn: `runs/B0x/seed0/summary.json`, `history.csv`; ảnh training: `curves/B0x_*.png`. Số tham số ResNet-50 là 23,5M vì head 9 lớp thay head 1000 lớp.

**Điều kiện đo độ trễ (sơ bộ):** Tesla T4, batch 1, 224×224, FP32, torch 2.11.0+cu130, warmup 10 lần, `torch.cuda.synchronize()` trước và sau mỗi lần đo, 50 lần đo, không tính tiền xử lý, dùng kiến trúc khởi tạo ngẫu nhiên (độ trễ không phụ thuộc giá trị trọng số). AMP **chậm hơn** FP32 ở batch 1 trên 5 trong 6 backbone (trừ ResNet-50: 6,92 so với 7,74 ms p50); số AMP nằm trong `results/backbone_latency.json`. Batch lớn chưa đo.

### Nhận xét

1. **ConvNeXt-T tốt nhất và nhanh (p95 8,0 ms)**, nên được chọn cho Bước 2 và 3. Đây là bộ trọng số ImageNet-12k fine-tune, được tiền huấn luyện trên nhiều dữ liệu hơn các tag còn lại, nên lợi thế có thể đến từ **trọng số chứ không chỉ kiến trúc**; chưa kiểm chứng vì mỗi kiến trúc mới thử một tag.
2. **B02, B04, B03 chưa phân biệt được:** chúng cách nhau 0,009 và 0,010 macro-F1 với 1 seed. Chênh lệch giữa nhóm này với B01, B05, B06 (hàng chục điểm) thì rõ.
3. **ResNet-50 thấp bất thường (0,7841).** Giả thuyết: tag `a1_in1k` được huấn luyện bằng công thức BCE (ResNet strikes back) nên không hợp với tinh chỉnh ngắn bằng cross-entropy và LR 1e-4. **Chưa kiểm chứng**; đường cong B01 vẫn đang tăng ở epoch 10.
4. **Hai mạng nhẹ kém rõ rệt (0,72 và 0,60) và có dấu hiệu chưa hội tụ hoặc quá khớp:** train loss 0,26 nhưng val loss 0,65 và 0,85, ECE 0,055 và 0,053 (khoảng 6 lần ConvNeXt-T), F1 val dao động giữa các epoch. Giả thuyết: LR backbone 1e-4 thấp với mạng nhỏ dùng BatchNorm; chưa kiểm chứng. Vì vậy **không kết luận "mạng nhẹ không dùng được"**, chỉ có thể nói "ở công thức nền này thì kém".
5. **FLOPs không dự đoán độ trễ:** MobileNetV3-L có ít GMAC nhất (0,22) nhưng p50 (6,59 ms) lớn hơn DeiT-S (5,01 ms, 4,24 GMAC). Swin-T chậm nhất (13,81 ms).

## 4. Công thức huấn luyện (Bước 2, mới làm 5 ablation, 1 seed, val)

Mỗi ablation chỉ khác `T00` đúng **một** yếu tố (cùng ConvNeXt-T, cùng seed 0, cùng 10 epoch); `T00` là nền, không có yếu tố nào được "thăng cấp" vào nền (không dùng cách tham lam).

| Mã | Trục | Khác `T00` ở điểm nào | Macro-F1 val | Δ vs `T00` | Top-1 val | Balanced acc | ECE val | Recall Chinee Apple | Recall Snake Weed | Epoch tốt nhất | Train / epoch (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T00 | nền | – | 0,9676 | – | 0,9760 | 0,9674 | 0,0092 | 0,884 | 0,931 | 9 | 49 |
| T01 | A khởi tạo | từ đầu (`scratch`, không trọng số tiền huấn luyện) | 0,2999 | −0,6677 | 0,5490 | 0,3152 | 0,0243 | 0,138 | 0,172 | 8 | 57 |
| T02 | A khởi tạo | đóng băng backbone, chỉ train head | 0,8433 | −0,1243 | 0,8772 | 0,8241 | 0,0350 | 0,782 | 0,734 | 10 | 21 |
| T03 | B augmentation | thêm `ColorJitter(0,3; 0,3; 0,3)` | 0,9631 | −0,0045 | 0,9706 | 0,9599 | 0,0134 | 0,862 | 0,941 | 7 | 55 |
| T04 | B augmentation | thay bằng `TrivialAugmentWide` (cộng crop + lật) | 0,9703 | +0,0027 | 0,9774 | 0,9658 | 0,0088 | 0,933 | 0,936 | 10 | 56 |
| T05 | B augmentation | thêm CutMix (α = 1) | **0,9730** | **+0,0054** | 0,9791 | 0,9762 | 0,0089 | 0,933 | 0,946 | 9 | 57 |

Nguồn: `runs/T0x/seed0/`; ảnh training: `curves/T0x_*.png`; số theo lớp tính lại từ `predictions/T0x_seed0_val.csv` bằng `eval.compute_metrics`.

### Nhận xét

1. **Trục A: kết luận chắc chắn dù mới 1 seed.** T01 gần như không học được: train loss còn 1,25 sau 10 epoch, F1 val chỉ tăng từ 0,115 lên 0,300, và có 144 ảnh Chinee Apple bị đoán thành `Negatives`. Điều này phù hợp với GUIDE (ít dữ liệu, 10 epoch, không có tiền huấn luyện thì không kịp học; đây là kết quả hợp lệ, không phải lỗi). T02 hội tụ nhanh và rẻ (21 giây/epoch, bằng khoảng 0,4 thời gian của `T00`), nhưng F1 val vẫn đang tăng chậm ở epoch 10 (0,843) và dừng ở mức thấp hơn nền 0,124; các đặc trưng ImageNet đóng băng chưa đủ cho bài toán này. Cả hai chênh lệch lớn hơn mọi nhiễu hợp lý.
2. **Trục B: chưa kết luận được.** Ba chênh lệch (−0,0045, +0,0027, +0,0054) đều nhỏ, mới 1 seed và chưa có std theo seed, nên theo quy tắc của bài lab chỉ được viết **"không phân biệt được với `T00`"**. Chúng ta cũng chưa biết nhiễu giữa các seed lớn cỡ nào (trên tập nhỏ như DeepWeeds có thể lớn hơn mức 0,1 điểm phần trăm trong slide). Không nên xếp hạng CutMix trên TrivialAugment trên nền.
3. **Dấu hiệu theo lớp (cần kiểm chứng):** so với `T00`, recall val của Chinee Apple là 0,884 → 0,933 ở cả T04 và T05 (khoảng 11 ảnh trong 225 ảnh val), số ảnh Chinee Apple bị đoán thành `Negatives` giảm từ 13 xuống 7, và balanced accuracy của T05 cao hơn (0,9762 so với 0,9674). Snake Weed ít đổi (0,931 → 0,936 và 0,946). T03 (ColorJitter) có recall Chinee Apple thấp hơn nền (0,862). Giả thuyết **chưa kiểm chứng**: màu sắc là dấu hiệu hữu ích để phân loại các loài này nên làm nhiễu màu không giúp, còn các phép biến đổi hình học/trộn mẫu giúp mô hình bớt phụ thuộc vào nền ảnh. Cần ≥ 3 seed và ảnh bị đoán sai để xác nhận.
4. **Hiệu chuẩn:** ECE val của T04, T05 (0,0088; 0,0089) xấp xỉ nền (0,0092); T03 hơi cao hơn (0,0134); T01 và T02 kém hiệu chuẩn (0,0243 và 0,0350), phù hợp với việc mô hình học kém.
5. **Đường cong:** CutMix có train loss cao hơn hẳn (0,491 ở epoch 10 so với 0,043 của nền) vì nhãn bị trộn, nên không so sánh được với train loss của các run khác; theo dõi bằng val (val loss 0,080 so với 0,095 của nền). F1 val của T05 dao động ở đầu run (0,912 → 0,879 → 0,946) rồi ổn định sau epoch 7.

## 5. Phân tích lỗi sơ bộ (nền ConvNeXt-T, val)

Từ `predictions/T00_seed0_val.csv` (hàng = nhãn thật; 225 ảnh Chinee Apple và 203 ảnh Snake Weed trong val):

- **F1 theo lớp:** Chinee Apple 0,932 và Snake Weed 0,926 là hai lớp thấp nhất; các lớp còn lại 0,965 đến 0,990.
- **Chinee Apple:** recall 0,884; 8 ảnh bị đoán thành Snake Weed, 13 thành `Negatives`, 4 thành Lantana. **Snake Weed:** recall 0,931; 3 ảnh bị đoán thành Chinee Apple, 5 thành `Negatives`.
- Cặp Chinee Apple ↔ Snake Weed (khó nhất theo bài báo) chỉ có 8 + 3 = 11 lỗi; nguồn lỗi lớn hơn của hai lớp này là bị gán nhầm sang `Negatives` (13 + 5 = 18). Giả thuyết **chưa kiểm chứng** (chưa xem trực tiếp ảnh bị đoán sai): nhiều ảnh có cây mục tiêu nhỏ, bị che hoặc trong bóng nên giống ảnh nền.
- Các số này **trên val, 1 seed, chỉ để tham khảo**, không so trực tiếp với mốc 88,5% và 88,8% của bài báo (mốc đó trên test và huấn luyện khác nhiều).

## 6. Việc chưa làm và hạn chế (nêu thẳng)

- **Chưa làm:**
  - Ablation trục C (loss: label smoothing, focal, trọng số lớp), D (sampler cân bằng), E (LR), F (EMA) tức T06–T11. T06 bị ngắt khi VM Colab bị cắt lúc run mới ở epoch 4 và **không dùng bất kỳ số nào của lần chạy dở đó**. Vì chỉ mới làm 2 trục (A và B) nên **chưa đạt yêu cầu ≥ 3 trục** của RUBRIC mục C. Cũng chưa thử kết hợp các yếu tố tốt.
  - Bước 3 (≥ 4 phương pháp suy luận, hiệu chuẩn T, độ trễ batch 1 và batch lớn, đường đánh đổi), Bước 4 (3 seed cho cấu hình cuối và mốc `T00`/`I00`, test một lần mỗi seed, `predictions/*_test.csv`, `eval.py score` và `grade`), `results.xlsx`, README riêng có link notebook.
  - Vì thiếu Bước 4, **phần I của RUBRIC (chất lượng model trên test) chưa có số nào**, và bài chưa đủ sản phẩm theo điều kiện P1, P4.
- **Chỉ 1 seed** cho mọi số; chưa có std theo seed nên mọi chênh lệch nhỏ (cả ba của trục B, và cả chênh lệch giữa B02/B03/B04) đều chưa kết luận được.
- **Chọn backbone và ablation chỉ dựa trên val** (đúng S2/S4); test chưa được mở.
- **Công bằng giữa backbone chưa trọn vẹn:** mỗi kiến trúc dùng tag trọng số mặc định của `timm`, cùng một LR cho tất cả.
- **Ngân sách tính toán:** Colab Free, VM bị ngắt nhiều lần (thường sau khoảng 1 giờ), có lúc bị từ chối cấp VM do hạn mức; epoch giảm xuống 10. Checkpoint không lưu về máy (chỉ giữ log, logit và dự đoán val, đường cong), nên Bước 3 sẽ phải huấn luyện lại mô hình được chọn.
- **Chia ngẫu nhiên không theo địa điểm** (bài báo gốc) nên điểm test sau này có thể lạc quan so với địa điểm mới; một fold duy nhất.

## 7. Kế hoạch hoàn thành

1. Chạy T06–T11 (loss, sampler, LR, EMA), mỗi lần chỉ đổi một yếu tố so với `T00`; thử một kết hợp các yếu tố tốt (ví dụ CutMix + label smoothing + EMA) và xem cộng dồn hay triệt tiêu.
2. Chạy lại `T00` và các ứng viên tốt nhất với ≥ 3 seed để có std trước khi kết luận về trục B.
3. Bước 3: TTA lật, 5 crop hoặc đa tỉ lệ, gộp xác suất so với logit, dò độ phân giải, ensemble, temperature scaling (T khớp trên val), gộp BN/FP16; đo độ trễ p50/p95/p99 ở batch 1 và 32.
4. Bước 4: chốt cấu hình trên val, chạy cấu hình cuối và mốc `T00`/`I00` với 3 seed, test một lần mỗi seed, rồi `eval.py score` và `grade`.
5. Hoàn thiện `results.xlsx`, ảnh curves cho mọi `exp_id`, báo cáo cuối, README riêng.

## Phụ lục: cấu trúc file đã có

- `code/`: `dataset.py`, `model.py`, `losses.py`, `train.py`, `inference.py`, `benchmark.py`, `experiments.py` (danh sách `exp_id` → cấu hình), `step0_prepare.py`, `step1_latency.py`, `step3_inference.py` (chưa chạy), `test_code.py`. `eval.py` gốc không sửa.
- `eda/`, `curves/` (B01–B06, T00–T05), `predictions/` (chỉ file **val** của B01–B06 và T00–T05), `runs/*/seed0/` (config, history, summary, logit val), `results/backbone_latency.json`, `logs/`.
- Không có checkpoint, dataset hay file test nào trong thư mục này.
