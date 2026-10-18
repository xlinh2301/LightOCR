Tôi đề xuất cho bạn một ma trận 45 thực nghiệm OCR dành riêng cho ảnh crop chứa chữ số đồng hồ, trong đó có khoảng 20 thực nghiệm ưu tiên cao nhất để chạy trước, phần còn lại triển khai theo kết quả sàng lọc.

Mục tiêu hôm nay, 18/10/2026, không phải chạy càng nhiều mô hình càng tốt, mà là tìm được:

1. Backbone tốt nhất trong ngân sách khoảng 1M parameters.
2. Neck tốt nhất để chuyển feature map thành chuỗi đặc trưng cho CTC.
3. Phương pháp cải thiện lỗi sai chữ số nhưng đúng độ dài.
4. Phương pháp chống chịu blur, glare, noise và biến đổi ánh sáng.
5. Một hoặc hai giả thuyết đủ triển vọng để phát triển thành đóng góp khoa học trong paper.

Tôi sẽ ưu tiên ba hướng nghiên cứu song song:

Hướng A — Architectural Efficiency

Thiết kế CNN và neck nhỏ nhưng giữ được thông tin chữ số.

Ưu tiên 1

Hướng B — Structural Digit Recognition

Giảm nhầm lẫn giữa các chữ số có hình dạng gần giống nhau.

Ưu tiên 1

Hướng C — Degradation Robustness

Đánh giá và cải thiện khả năng hoạt động trên ảnh thực tế chất lượng kém.

Ưu tiên 2

## 1. Đóng băng protocol trước khi chạy

Các quy tắc này áp dụng cho toàn bộ ma trận. Nếu bỏ qua, rất khó dùng kết quả để viết paper.

| Thành phần      | Quy định                                     |
| --------------- | -------------------------------------------- |
| Task            | Cropped image → digit sequence               |
| Vocabulary      | `0–9` và `CTC blank`                         |
| Dataset         | Self-crawl + Kaggle                          |
| Split           | Theo thiết bị/nguồn hoặc nhóm ảnh gần trùng  |
| Model selection | Chỉ dùng validation thuộc miền huấn luyện    |
| Test            | Khóa, không dùng để chọn cấu hình            |
| Primary metric  | Exact Match Accuracy                         |
| Secondary       | CER, same-length errors, latency, parameters |
| Seed sàng lọc   | 42                                           |
| Seed xác nhận   | 42, 1337, 2026                               |

Tất cả thí nghiệm thuộc cùng nhóm phải sử dụng cùng training schedule, preprocessing mặc định, seed, ngân sách bước cập nhật và dữ liệu. Chỉ thay đổi biến mà thí nghiệm muốn kiểm định.

Lưu ý CTC đặc biệt quan trọng: Không được giảm chiều rộng feature map quá mạnh. Với nhãn dài \\(L\\) và \\(R\\) cặp ký tự giống nhau đứng cạnh nhau, số timestep \\(T\\) ít nhất phải thỏa mãn:

\\[ T \ge L+R \\]

Ví dụ `001188` có 6 chữ số và 3 cặp lặp liền kề, nên cần tối thiểu 9 timestep để tồn tại một alignment hợp lệ. CTC loss có thể xuất hiện giá trị vô hạn khi chuỗi đầu vào quá ngắn; không được lặng lẽ bỏ qua các mẫu này trong kết quả nghiên cứu.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.pytorch.org\&sz=32)

PyTorch 2.14 documentation



Chiến lược sử dụng hai bộ dữ liệu: Trong hôm nay, bạn có thể huấn luyện và chọn mô hình dựa trên training/dev của self-crawl. Kaggle giữ làm external test nếu nguồn đó chưa được dùng để điều chỉnh kiến trúc hoặc ngưỡng. Có thể làm thêm chiều Kaggle → self-crawl, nhưng phải xác định protocol và phần dữ liệu bị khóa trước khi bắt đầu.

## 2. Nhóm A — Baseline và Backbone (6 thực nghiệm)

Mục đích: Tìm hiểu xem việc tăng độ phức tạp của mô hình có thực sự mang lại lợi ích cho một bài toán chỉ có 10 chữ số hay không.

| ID  | Kiến trúc                      | Giả thuyết                                 |
| --- | ------------------------------ | ------------------------------------------ |
| B00 | CNN + BiLSTM + CTC (CRNN)      | Baseline truyền thống                      |
| B01 | Depthwise CNN + CTC            | CNN nhỏ đã đủ trích xuất đặc trưng?        |
| B02 | Depthwise CNN + Conv1D + CTC   | Temporal convolution cải thiện nhận dạng?  |
| B03 | Depthwise CNN + BiGRU + CTC    | Recurrent modeling có cần thiết?           |
| B04 | Standard CNN + CTC             | Depthwise CNN có mất thông tin quan trọng? |
| B05 | CNN + positional CE classifier | Nếu độ dài/vị trí cố định, có cần CTC?     |

B05 chỉ áp dụng nếu vị trí các chữ số được chuẩn hóa và chiều dài cố định. Nếu dữ liệu có chiều dài biến thiên, thay bằng CNN + BiLSTM một lớp để so sánh với BiGRU.

Đầu ra quan trọng: Vẽ biểu đồ `Accuracy vs Parameters`, `Accuracy vs FLOPs` và `Accuracy vs Latency`.

Tôi đặc biệt quan tâm đến B01, B02 và B03. Nếu B02 gần bằng B03 nhưng nhanh hơn rõ rệt, chúng ta có cơ sở để tập trung nghiên cứu neck dựa trên convolution thay vì recurrent modeling.

## 3. Nhóm B — Input Representation (7 thực nghiệm)

Giữ B01 cố định. Cấu hình tham chiếu là RGB, cao 32, rộng tối đa 192, giữ tỷ lệ rồi padding.

| ID  | Thay đổi                       | Điều cần kiểm định                     |
| --- | ------------------------------ | -------------------------------------- |
| I01 | Input 32×128                   | Độ phân giải thấp có đủ không?         |
| I02 | Input 32×192                   | Cấu hình tham chiếu                    |
| I03 | Input 32×256                   | Thêm resolution có giảm nhầm chữ số?   |
| I04 | Input 48×192                   | Tăng thông tin chiều cao               |
| I05 | Grayscale                      | Màu sắc có cần thiết?                  |
| I06 | Grayscale + CLAHE              | Cải thiện độ tương phản có giúp không? |
| I07 | Aspect-ratio-aware multi-width | Giảm biến dạng và padding lãng phí?    |

Đối với I07, có thể dùng bucket chiều rộng 128/192/256, giữ chiều cao cố định, padding theo từng bucket và tính chính xác output lengths cho CTC.

SVTRv2 đã cho thấy resizing phù hợp với hình dạng text có thể cải thiện recognition. Vì vậy, đây là một baseline preprocessing đáng kiểm chứng, dù không nên xem multi-size resizing đơn thuần là novelty mới.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://openaccess.thecvf.com\&sz=32)

Open Access CVF



Kết quả cần tìm: Liệu chữ số đồng hồ cần thêm độ phân giải, hay CNN có thể học đủ thông tin từ ảnh nhỏ?

## 4. Nhóm C — Neck Architecture (11 thực nghiệm)

Đây là nhóm tôi đánh giá có tiềm năng tạo ra kiến trúc chính cho paper.

Giữ backbone của B02 và chỉ thay đổi neck. B02 sử dụng height mean pooling và một Conv1D kernel 3 làm cấu hình tham chiếu.

| ID  | Neck                                       | Giả thuyết                                        |
| --- | ------------------------------------------ | ------------------------------------------------- |
| N01 | Max pooling theo chiều cao                 | Nét chữ nổi bật quan trọng hơn trung bình?        |
| N02 | Learnable attention pooling theo chiều cao | Học tập trung vào hàng chứa nét chữ hữu ích       |
| N03 | Conv1D kernel 5                            | Receptive field lớn hơn có giúp?                  |
| N04 | Multi-scale Conv1D (kernel 3, 5)           | Kết hợp đặc trưng cục bộ và ngữ cảnh              |
| N05 | SE attention                               | Channel recalibration cải thiện phân biệt chữ số? |
| N06 | ECA attention                              | Attention nhẹ có đủ?                              |
| N07 | Sobel feature concatenation                | Edge information có lợi trực tiếp?                |
| N08 | Sobel branch + gated fusion                | Có thể học khi nào nên tin vào edge?              |
| N09 | Learnable structural branch + gate         | Feature cấu trúc học được có tốt hơn Sobel?       |
| N10 | Multi-scale Conv1D + structural gate       | Hai cơ chế có bổ trợ nhau?                        |
| N11 | Wider Conv1D không có structural branch    | Loại trừ lợi ích chỉ do tăng parameters           |

Trong các thực nghiệm này, N08 và N09 là hai ứng viên tôi muốn đầu tư nhất.

### Minh họa cơ chế N08

Một cách fusion có thể thử là:

\\[ F\_{\mathrm{out}}=g\odot F\_{\mathrm{rgb}}+(1-g)\odot F\_{\mathrm{edge}} \\]

Trong đó \\(g\\) là gate sinh từ đặc trưng của hai nhánh, và hai tensor phải được chiếu về cùng kích thước.

Điều kiện quan trọng: N08 phải tốt hơn N07 và N11 mới có bằng chứng rằng adaptive fusion mang lại giá trị ngoài việc cộng edge features hoặc tăng capacity.

## 5. Nhóm D — Robustness & Augmentation (11 thực nghiệm)

Giữ backbone, neck và mọi tham số huấn luyện cố định. Thực hiện trên B02 trước.

| ID  | Augmentation                      | Mục đích                          |
| --- | --------------------------------- | --------------------------------- |
| A01 | Brightness + Contrast             | Chống thay đổi ánh sáng           |
| A02 | Gaussian blur                     | Chống mất chi tiết nét            |
| A03 | Motion blur                       | Chống rung camera                 |
| A04 | Gaussian/Poisson noise            | Chống nhiễu ảnh                   |
| A05 | JPEG compression                  | Chống artifact nén                |
| A06 | Synthetic glare/reflection        | Chống phản chiếu màn hình         |
| A07 | Mild perspective transform        | Chống góc chụp nghiêng            |
| A08 | Small random occlusion            | Chống che khuất một phần          |
| A09 | Photometric + blur + noise + JPEG | Kết hợp suy giảm chất lượng       |
| A10 | A09 + glare                       | Kiểm tra vai trò của glare        |
| A11 | A10 + mild perspective            | Kiểm tra khả năng robust tổng hợp |

Glare đáng ưu tiên vì nghiên cứu về seven-segment recognition đã ghi nhận glare và LED bleeding là những vấn đề thực tế.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.itm-conferences.org\&sz=32)

ITM Conferences



Không dùng augmentation làm biến đổi nhãn. Ví dụ, che mất toàn bộ một nét khiến `8` trở thành `3` rõ ràng đối với con người thì ảnh đó không còn là một training sample đáng tin cậy với nhãn cũ.

Ngoài ra, cần tạo một synthetic corruption benchmark cố định với các severity levels đã định nghĩa trước. Benchmark này phục vụ phân tích độ bền vững; nếu dùng kết quả để chọn mô hình thì nó là validation, không còn là test độc lập.

## 6. Nhóm E — Training & Loss (6 thực nghiệm)

Đây là nhóm thăm dò sau khi có baseline ổn định. Không chạy đồng thời nhiều thay đổi loss.

| ID  | Thực nghiệm                         | Mục đích                                        |
| --- | ----------------------------------- | ----------------------------------------------- |
| L01 | Exponential Moving Average weights  | Kiểm tra ổn định dự đoán                        |
| L02 | Dropout 0.1 ở sequence features     | Giảm overfitting                                |
| L03 | Two-view photometric consistency    | Giữ đầu ra ổn định khi đổi ánh sáng             |
| L04 | Hard-negative sequence margin + CTC | Nhắm trực tiếp vào sai chữ số nhưng đúng độ dài |
| L05 | Hard-example reweighting            | Tăng tập trung vào mẫu khó                      |
| L06 | Learning rate warmup ablation       | Kiểm tra ảnh hưởng hội tụ                       |

### L04 — Thực nghiệm có tiềm năng nghiên cứu riêng

Giả sử ground truth là `0836`, mô hình dự đoán `0886`. Độ dài không thay đổi, nhưng có một chữ số bị nhầm.

Ta tạo một negative sequence \\(y^-\\) có độ dài bằng ground truth bằng cách thay một chữ số bằng chữ số dễ nhầm (dựa trên confusion statistics của training data).

Thử một loss:

\\[ \mathcal L = \mathcal L\_{\mathrm{CTC}}+ \lambda\max\left(0,\\, m-\log P\_{\mathrm{CTC}}(y|x) +\log P\_{\mathrm{CTC}}(y^-|x) \right) \\]

Mục đích là khuyến khích xác suất CTC của chuỗi đúng cao hơn chuỗi sai dễ nhầm một margin \\(m\\).

Đây là một giả thuyết cần thăm dò, không thể tuyên bố mới trước khi rà soát các nghiên cứu sequence discriminative training và contrastive CTC. Nó cũng cần kiểm tra ổn định gradient và chi phí tính thêm xác suất CTC của negative sequences.

Nếu L04 thật sự giảm same-length substitutions mà không làm tăng deletion/insertion errors, đây có thể là hướng mở rộng đáng nghiên cứu.

Đối với L03, chỉ dùng các phép biến đổi photometric không thay đổi căn chỉnh không gian khi so sánh phân phối timestep của hai view.

## 7. Nhóm F — Xác nhận khoa học (4 thực nghiệm)

Những bước này không được bỏ qua vì chúng phân biệt kết quả sàng lọc với bằng chứng đủ tin cậy để đưa vào paper.

| ID  | Thực nghiệm                                                        | Kết quả cần có                                     |
| --- | ------------------------------------------------------------------ | -------------------------------------------------- |
| V01 | Baseline B01 với 3 seeds                                           | Mean ± standard deviation                          |
| V02 | Best neck với 3 seeds                                              | Cải thiện ổn định?                                 |
| V03 | Best augmentation với 3 seeds                                      | Robustness tăng ổn định?                           |
| V04 | Best combined model, matched-capacity control và frozen evaluation | Clean, cross-domain, latency, confidence intervals |

Tổng cộng: 45 cấu hình/thực nghiệm và bước xác nhận, không có nghĩa là cần huấn luyện 45 mô hình đến hội tụ ngay hôm nay.

## 8. Chọn 20 thực nghiệm chạy đầu tiên

Tôi đề xuất chạy theo thứ tự sau. Đây là danh sách ưu tiên, không phải ranking hiệu quả đã được xác minh.

Priority experiment queue

Đánh dấu khi hoàn thành mỗi thực nghiệm

## 0/20

Completed

AllBaselineInputNeckAugmentationTraining

B00

CRNN baseline

B01

Depthwise CNN + CTC

B02

CNN + Conv1D + CTC

B03

CNN + BiGRU + CTC

I02

Input 32×192

I03

Input 32×256

I05

Grayscale input

N02

Attention height pooling

N04

Multi-scale Conv1D

N07

Sobel concatenation

N08

Sobel gated fusion

N09

Learnable structural gate

N11

Matched-capacity Conv1D

A01

Photometric augmentation

A02

Gaussian blur

A06

Synthetic glare

A09

Combined degradation

A10

Combined + glare

L03

Photometric consistency

L04

Hard-negative CTC margin

&#x20;Copy checklistReset

## 9. Làm sao chạy nhiều thực nghiệm mà không lãng phí GPU?

Chia thành hai tầng:

Tầng 1 — Screening

Huấn luyện các ứng viên với khoảng 30% ngân sách optimizer steps của một full run, sau khi xác nhận baseline đã thoát khỏi trạng thái dự đoán blank. Mỗi nhóm chỉ giữ lại 1–2 ứng viên tốt nhất theo development metrics. Không loại mô hình chỉ vì loss ở vài bước đầu cao.

Tầng 2 — Full confirmation

Huấn luyện đầy đủ baseline và các ứng viên được chọn. Sau đó chạy 3 seeds cho những so sánh chính. Không so sánh checkpoint chưa hội tụ với checkpoint đã hội tụ như một kết luận khoa học.

Tôi muốn bạn đặc biệt lưu lại từng sample bị dự đoán sai, gồm ground truth, prediction, độ dài, source và dạng suy giảm (nếu có).

Nên phân loại thành:

- S: Sai chuỗi, độ dài vẫn đúng.
- D: Thiếu ký tự.
- I: Thừa ký tự.
- R: Lỗi liên quan đến ký tự lặp, ví dụ `11`, `00`, `88`.
- C: Đúng toàn bộ chuỗi.

Trong đó, báo cáo riêng tỷ lệ wrong but same-length trên tổng mẫu, không gộp tất cả thành CER.

## 10. Full ablation quan trọng nhất cho paper

Khi tìm được best neck và best augmentation từ development set, hãy làm ma trận factorial 2×2 sau:

|               | No robust augmentation | Robust augmentation |
| ------------- | ---------------------- | ------------------- |
| Baseline neck | F00                    | F01                 |
| Proposed neck | F10                    | F11                 |

Chỉ thay đổi hai yếu tố này, giữ mọi yếu tố còn lại giống nhau.

Đánh giá hiệu ứng tương tác:

\\[ \Delta\_{\mathrm{interaction}} =(Acc\_{11}-Acc\_{10})-(Acc\_{01}-Acc\_{00}) \\]

Nếu F11 tốt hơn cả F01 và F10, bạn có bằng chứng phương pháp kết hợp tốt hơn từng thành phần. Nếu hiệu ứng tương tác dương và ổn định qua seeds, bạn còn có thể lập luận rằng neck và augmentation hỗ trợ nhau.

Cần lưu ý: F11 tốt hơn không tự động có nghĩa là tương tác dương. Hai nhận định này khác nhau về mặt khoa học.

## 11. Mỗi thực nghiệm phải xuất ra gì?

Tôi đề xuất cấu trúc kết quả:

```
experiments/
├── manifest/
│   ├── train.csv
│   ├── dev.csv
│   └── frozen_test.csv
├── configs/
│   ├── B00.yaml
│   ├── B01.yaml
│   └── ...
├── runs/
│   ├── B00_seed42/
│   │   ├── config.yaml
│   │   ├── metrics.json
│   │   ├── history.csv
│   │   ├── predictions_dev.csv
│   │   ├── best.pth
│   │   └── run_metadata.json
│   └── ...
├── comparisons/
│   ├── baseline_results.csv
│   ├── neck_ablation.csv
│   ├── augmentation_ablation.csv
│   ├── confusion_analysis.csv
│   └── efficiency_results.csv
└── figures/
    ├── accuracy_params.png
    ├── accuracy_latency.png
    ├── confusion_matrix.png
    └── robustness_by_severity.png
```

Một dòng kết quả tổng hợp cần tối thiểu:

`run_id, seed, split_hash, config_hash, params, FLOPs, latency, exact_match, CER, same_length_error_rate, deletion_rate, insertion_rate, best_step, total_steps`.

Với kết quả thống kê cuối cùng, tính confidence intervals bằng bootstrap theo nhóm thiết bị hoặc nguồn ảnh nếu các ảnh trong nhóm phụ thuộc nhau.

## 12. Tôi muốn nhấn mạnh 3 thí nghiệm đáng giá nhất

## 01

N08 — Adaptive Structural Feature Fusion

Kiểm tra liệu kết hợp CNN features với edge features có giúp phân biệt chữ số tốt hơn hay không. Đây là ứng viên chính cho cải tiến kiến trúc.

## 02

L04 — Hard-Negative CTC

Tấn công trực tiếp lỗi sai ký tự nhưng đúng độ dài. Đây là hướng thăm dò có rủi ro cao hơn nhưng có thể mở ra câu hỏi nghiên cứu sâu.

## 03

N08 × A10 — Structural Robustness

Kiểm tra xem feature cấu trúc và robust augmentation có bổ trợ nhau trên ảnh bị glare, blur và thay đổi ánh sáng không.

Lộ trình tôi chọn: Bắt đầu B00–B03 để xác lập baseline, chạy I02–I05 để hiểu vai trò của input, sau đó ưu tiên N07–N09 và A06–A10. Chỉ khi hệ thống CTC đã hội tụ ổn định mới thực hiện L03–L04.

Điều quan trọng nhất tối nay là có một bảng so sánh khoa học có thể giải thích được, thay vì 45 checkpoint không biết vì sao tốt hay xấu. Từ bảng đó, bạn có thể chọn hướng nghiên cứu cho 6 ngày còn lại mà không phải đoán mò.