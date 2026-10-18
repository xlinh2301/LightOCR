Với mục tiêu của bạn là chạy nhiều thực nghiệm OCR trong hôm nay và sử dụng kết quả để viết paper Q1–Q3, tôi đề xuất output phải gồm 3 cấp độ: Model Output → Experiment Output → Research Report.

Không nên để agent chỉ trả về Accuracy hoặc Loss. Cần đủ dữ liệu để phân tích, so sánh mô hình và xác định đóng góp khoa học.

## 1. Model Output — Kết quả nhận dạng

Với ảnh crop đồng hồ, output cuối cùng của mô hình là chuỗi ký tự, không phải số nguyên, để giữ được số `0` ở đầu.

Ví dụ:

Input

## 0836

Cropped display

CTC Prediction

## 0836

String output

Ở mức tensor, CTC classifier trả về logits có shape `[B, T, 11]` (10 chữ số và 1 blank). Sau CTC decoding, nhận chuỗi ký tự có độ dài biến thiên.

Output inference tối thiểu:

```
{
  "sample_id": "img_001",
  "prediction": "0836",
  "length": 4,
  "decode_method": "ctc_greedy"
}
```

## 2. Experiment Output — Mỗi run phải có những gì?

Mỗi thực nghiệm cần xuất một bản ghi kết quả thống nhất.

Ví dụ thực nghiệm N08:

```
{
  "run_id": "N08_seed42",
  "architecture": "CNN_Sobel_Gated_CTC",
  "seed": 42,
  "parameters": 850000,
  "metrics": {
    "exact_match_accuracy": null,
    "cer": null,
    "same_length_error_rate": null,
    "deletion_rate": null,
    "insertion_rate": null
  },
  "efficiency": {
    "flops": null,
    "latency_ms": null
  },
  "checkpoint": "best.pth"
}
```

Các giá trị `null` phải được thay bằng số đo thực tế sau huấn luyện, không được tự suy đoán.

Ngoài metrics tổng hợp, phải lưu file `predictions_dev.csv` gồm:

| sample_id | GT   | Prediction | Error type        |
| --------- | ---- | ---------- | ----------------- |
| 001       | 0836 | 0836       | Correct           |
| 002       | 0836 | 0886       | Same-length error |
| 003       | 1128 | 128        | Deletion          |
| 004       | 459  | 4559       | Insertion         |

Đối với những dự đoán vừa có substitution vừa có insertion/deletion, cần lưu đầy đủ số lượng thao tác edit thay vì ép chúng vào một loại lỗi duy nhất.

## 3. Research Output — Quan trọng nhất cho paper

Đến cuối ngày, tôi muốn agent tổng hợp một Research Experiment Report, tối thiểu gồm 6 thành phần.

| Output                      | Nội dung                                     |
| --------------------------- | -------------------------------------------- |
| `experiment_summary.csv`    | Toàn bộ run, metric, Params, FLOPs, latency  |
| `architecture_ablation.csv` | So sánh backbone và neck                     |
| `robustness_analysis.csv`   | Accuracy theo blur, glare, noise và severity |
| `error_analysis.csv`        | CER, confusion, same-length errors           |
| `research_report.md`        | Phân tích giả thuyết, kết luận, hạn chế      |
| `next_experiments.md`       | Thực nghiệm nên tiếp tục và lý do            |

Các kết quả chính cần minh họa bằng 4 biểu đồ:

9092.59597.51000.30.50.811.3

Minh họa giả lập, không phải kết quả thực nghiệm

Accuracy vs Parameters

0255075100BaselineNew neckCombined

Minh họa giả lập

Architecture comparison

BaselineRobust model

60708090100CleanLowMedHigh

Minh họa giả lập

Robustness by severity

020406080Subst.DeleteInsertMixed

Minh họa giả lập

Error distribution

Tất cả giá trị trong biểu đồ trên chỉ là ví dụ minh họa, chưa phải dữ liệu của bạn.

## 4. Phần kết luận agent bắt buộc phải trả về

Đây là phần trực tiếp phục vụ quyết định hướng paper.

Mỗi nhóm thực nghiệm phải trả lời:

1. Best candidate: Mô hình nào có kết quả development tốt nhất theo metric đã định trước?
2. Scientific finding: Chúng ta học được điều gì? Ví dụ, structural features có thực sự giảm lỗi sai chữ số không?
3. Evidence: Kết quả so sánh cụ thể, đối chứng matched-capacity và độ ổn định qua seeds.
4. Failure analysis: Những loại ảnh hoặc chữ số nào vẫn nhận dạng sai?
5. Next hypothesis: Giả thuyết nào nên tiếp tục kiểm định?
6. Paper potential: Kết quả hỗ trợ đóng góp phương pháp mới, cải thiện robustness, hay chỉ là tối ưu kỹ thuật?

Nên phân biệt rõ kết quả quan sát được, giả thuyết và kết luận đã được xác nhận. Nếu screening chỉ dùng một seed, không được viết rằng phương pháp tốt hơn một cách ổn định.

## 5. Cấu trúc output cuối ngày tôi khuyên dùng

```
phase1_day1/
│
├── 01_experiment_registry.csv
├── 02_model_comparison.csv
├── 03_neck_ablation.csv
├── 04_augmentation_ablation.csv
├── 05_loss_ablation.csv
├── 06_error_analysis.csv
├── 07_efficiency_analysis.csv
│
├── plots/
│   ├── accuracy_vs_parameters.png
│   ├── accuracy_vs_latency.png
│   ├── error_distribution.png
│   └── robustness_curves.png
│
├── runs/
│   └── <run_id>/
│       ├── config.yaml
│       ├── metrics.json
│       ├── predictions_dev.csv
│       ├── training_history.csv
│       ├── best.pth
│       └── metadata.json
│
├── research_report.md
└── next_phase_plan.md
```

Mỗi run cần lưu manifest hash, config, seed và training budget để bảo đảm tái lập. Các external test đã đóng băng chỉ được dùng trong giai đoạn đánh giá cuối, không đưa vào bảng xếp hạng dùng để chọn mô hình.

Điều tôi mong muốn nhất sau hôm nay: Agent đưa ra 3 kết luận có bằng chứng:

- Backbone nào mang lại accuracy/efficiency trade-off tốt nhất?
- Neck hoặc loss nào có khả năng tạo đóng góp khoa học thực sự?
- Hướng nào xứng đáng đầu tư tiếp trong 6 ngày còn lại?

Nếu phải ưu tiên, hãy bảo đảm agent làm tốt `research_report.md` và `next_phase_plan.md`. Hai file này phải tổng hợp bằng chứng từ toàn bộ thực nghiệm, chỉ ra cả kết quả âm tính và đề xuất quyết định go/no-go. Đây mới là đầu ra giúp bạn chuyển từ việc chạy nhiều mô hình sang làm nghiên cứu để viết paper.