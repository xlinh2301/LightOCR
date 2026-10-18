# Kiến trúc thị giác gọn nhẹ cho nhận dạng văn bản tổng quát: tổng quan bằng chứng 2024–2026

**Phiên bản:** 1.0, synthesis tạm thời · **Ngày chốt tìm kiếm:** 17-10-2026  
**Protocol:** [`PROTOCOL_v1.md`](PROTOCOL_v1.md), tác giả đã duyệt 17-10-2026  
**Tình trạng:** Tìm kiếm chính đã chạy; sàng lọc và trích xuất toàn văn chưa hoàn tất. Đây chưa phải systematic review hoàn chỉnh.

## Tóm tắt

Review xem xét hai lớp bằng chứng cho nhận dạng văn bản tổng quát trong điều kiện giới hạn tài nguyên: recognizer được đánh giá trực tiếp trên scene/document/handwritten text; và backbone vision gọn nhẹ chỉ được đánh giá trên tác vụ thị giác chung, có thể chuyển sang encoder OCR. Mốc đích là khoảng 1M tham số; mô hình lớn hơn chỉ làm comparator. Giai đoạn tìm kiếm là 2024-01-01 đến 2026-10-17.

Các truy vấn chính lấy 1.696 bản ghi (Semantic Scholar 100, OpenAlex direct text recognition 920, OpenAlex compact vision 678). Khử trùng lặp DOI và tiêu đề-năm còn 1.597. Semantic Scholar chạm giới hạn 100; tổng số hit không rõ. Truy vấn OpenAlex bổ sung nhạy với OCR báo tổng 2.993 nhưng chỉ lấy được 200 trước HTTP 429, vì vậy bị loại khỏi số đếm chính. Vòng sơ loại hiện loại 473 bản ghi, chuyển 19 bài sang tìm toàn văn, còn 1.105 cần đánh giá. Do đó, synthesis này là tạm thời, dựa trên bài đã đối chiếu nguồn sơ cấp; không đại diện kết quả cuối của toàn corpus.

Bằng chứng trực tiếp nổi bật giảm chi phí ở nhiều thành phần: CTC và sắp xếp đặc trưng, decoder autoregressive, chia sẻ trọng số/đệ quy cho HTR, mã hóa ký tự phân cấp và huấn luyện tương phản ở mức frame. Tuy vậy, bằng chứng được xác minh cho recognizer tổng quát gần 1M còn thiếu. TinyNeXt-T đạt 1.0M tham số và 71.5% ImageNet top-1, nhưng đây là bằng chứng gián tiếp, chưa có CER/WER OCR.

## Câu hỏi và phạm vi

**Chính:** Những kiến trúc/kỹ thuật hiệu quả nào công bố 2024–2026 đã được đánh giá trực tiếp trên nhận dạng văn bản tổng quát, và chúng báo cáo gì về chất lượng, tham số, compute, latency và triển khai?

**Phụ:** Backbone vision gọn nhẹ nào có đặc tính có thể hữu ích cho encoder OCR, và bằng chứng chuyển giao nào còn thiếu?

Tách rõ (A) bằng chứng OCR trực tiếp, (B) backbone vision gián tiếp, và (C) mô hình lớn làm comparator. Không gộp ImageNet accuracy với CER/WER. Không gộp latency khác phần cứng/runtime. Không thực hiện meta-analysis vì dữ liệu, ngôn ngữ, input shape, decoder và training recipe không đồng nhất.

## Phương pháp và luồng bản ghi

Semantic Scholar Graph API và OpenAlex Works API dùng để khám phá tài liệu; proceedings, publisher, arXiv và repo chính thức dùng để xác minh. Chuỗi truy vấn, thời gian, lỗi và snapshot nằm trong [`search_log.csv`](search_log.csv). Pilot Semantic Scholar trước khi protocol được duyệt không được tính vào luồng chính. OpenAlex cursor pagination trả 401; chuyển qua page pagination và lấy đủ các trang của hai truy vấn chính.

| Bước | n | Ghi chú |
|---|---:|---|
| Semantic Scholar STR/OCR | 100 | Chạm giới hạn; không có total hits |
| OpenAlex direct text recognition | 920 | 10 trang đã lấy |
| OpenAlex compact vision | 678 | 7 trang đã lấy |
| Tổng trước khử trùng | 1.696 | Các lượt chính sau duyệt protocol |
| Trùng DOI/tiêu đề-năm | 99 | Khử DOI trước, đối chiếu title + year |
| Bản ghi duy nhất | 1.597 | Corpus đang screening |
| Loại sơ bộ ở title/abstract | 473 | Survey, ứng dụng, detection-only, OCR-free, v.v. |
| Chuyển tìm toàn văn | 19 | Candidate, chưa phải bài được include cuối |
| Cần đánh giá tiếp | 1.105 | Screening chưa hoàn tất |

Truy vấn sensitivity OCR có total 2.993 nhưng mới lấy 200 bản ghi khi gặp 429; loại hoàn toàn khỏi các số trên. Screening một reviewer (Codex) có hỗ trợ từ khóa; không có sàng lọc độc lập, không có kappa và chưa đăng ký ngoài. Từng bản ghi và lý do hiện tại nằm trong [`screening_decisions.csv`](screening_decisions.csv). Các lý do sơ loại không thay thế quyết định toàn văn.

## Bằng chứng trực tiếp: text recognition

### CTC và biểu diễn thị giác

**SVTRv2** bổ sung multi-size resizing để giảm méo chữ, Feature Rearrangement Module hỗ trợ căn chỉnh CTC, và Semantic Guidance Module đưa ngữ cảnh ngôn ngữ vào lúc train rồi bỏ lúc inference. Paper đánh giá benchmark thông thường lẫn tình huống khó. SVTRv2-T được repo triển khai chính thức ghi khoảng 5.13M tham số; đây là comparator >2M, không phải ứng viên 1M. Quy trình huấn luyện lớn và đa dạng dataset cũng khiến so sánh paper-to-paper cần thận trọng.

**SVIPTR (CIKM 2024)** dùng visual-semantic extractor dạng pyramid, trộn local/global attention và hoán vị đặc trưng. Bài đánh giá tiếng Anh và tiếng Trung, nhấn mạnh tốc độ và độ ít nhạy theo độ dài. Có biến thể T/L, nhưng cần trích bảng toàn văn để xác nhận tham số chính xác; abstract không đủ chứng minh ngưỡng ≤2M.

**Free Lunch / FLCL (ACM MM 2024)** nhắm cải thiện recognizer nhẹ hiện hữu: Text Perceiver dựa trên Mamba hai chiều lọc đặc trưng liên quan đến chữ, còn contrastive loss áp dụng theo frame và phối hợp với CTC. Tác giả đánh giá chín mô hình nhẹ trên sáu benchmark và tập low-quality mới. Hướng này cho thấy có thể cải thiện biểu diễn/huấn luyện mà không thay backbone; cần xác minh overhead module và latency inference từ toàn văn trước khi kết luận triển khai miễn phí.

### Decoder, scaling và nhãn

**One2Seq (AAAI 2026)** mã hóa ngữ cảnh autoregressive vào một context token được cập nhật theo ký tự, với positional-aware hash embedding và dynamic global infusion. Mục tiêu là tránh query sequence tăng dần, giảm attention drift và tăng tốc decode. Trang AAAI xác nhận bài và mô tả hướng cải tiến, nhưng nguồn abstract chưa đủ số liệu tham số/latency để xếp vào ngưỡng 1M.

**Efficient Model Scaling and Cloze Self-Distillation (CVPR 2025)** phân tích encoder-vs-decoder scaling; tác giả báo decoder scaling đem lại gains hiệu quả hơn encoder scaling trong cấu hình họ thử. Cloze Self-Distillation khai thác soft prediction/pseudo-label để giảm tác động nhãn nhiễu trên dữ liệu thật. Bài báo cáo kết quả state-of-the-art trên 10/11 benchmark; biến thể CSD-S được nêu ở mức 40.8M tham số, nên kết quả là comparator về phân bổ compute và huấn luyện, không phải thiết kế 1M.

**Scaling Law for STR (CVPR 2024)** khảo sát scaling theo model/data/compute, công bố REBU-Syn gồm 6M mẫu thực và 18M mẫu tổng hợp, báo trung bình 97.42% word accuracy trên sáu benchmark. Đây là bằng chứng rằng quy mô dữ liệu và compute là biến gây nhiễu mạnh; không phải luận cứ rằng mô hình nhỏ hơn tốt hơn.

### Giảm footprint và HTR

**Recursive neural networks for compact HTR (IJDAR 2024)** chia sẻ trọng số qua các lớp liên tiếp để giảm footprint trong khi giữ độ sâu; đánh giá trên nhiều benchmark HTR và khảo sát kernel scaling. Đây là hướng phù hợp giới hạn bộ nhớ, nhưng weight sharing không đồng nghĩa giảm latency. Số tham số/độ trễ từng cấu hình phải được trích từ toàn văn trước khi kết luận gần 1M.

**HierCode** dùng codebook phân cấp và mã hóa multi-hot cho ký tự Trung văn, nhắm giảm chi phí biểu diễn từ vựng lớn, nhận dạng ký tự OOV và tăng tốc. Đây là cải tiến output representation, không phải backbone; kết quả với chữ Hán không tự động chuyển sang alphabet nhỏ/chữ số. Cần so cùng backbone và kích thước từ điển để đánh giá công bằng.

Các bài ngôn ngữ hoặc ứng dụng chuyên biệt như Farsi, Urdu, Bangla, Turkish, ID card có thể giúp đánh giá miền hẹp, nhưng không nên gộp thành kết luận general text recognition nếu chưa kiểm tra split, code, metric, preprocessing và số tham số. Trong bản này, phần lớn vẫn đang chờ screening toàn văn.

## Bằng chứng gián tiếp: backbone vision

| Backbone | Số liệu/thiết kế báo cáo | Liên quan đến OCR | Hạn chế |
|---|---|---|---|
| TinyNeXt-T, ICCV 2025 | 1.0M params; 71.5% ImageNet-1K top-1; thiết kế cho TinyML | Mốc backbone đúng khoảng 1M | Chưa đo CER/WER; cần kiểm tra stride và nét ký tự |
| SHViT, CVPR 2024 | Single-head attention, convolution giai đoạn đầu, macro design tiết kiệm | Gợi ý giảm overhead attention | Early downsampling có thể làm mất nét nhỏ |
| RepViT-M0.9, CVPR 2024 | 5.1M; 78.7% top-1; 0.9 ms iPhone 12 theo setup paper/repo | CNN/mobile baseline | Lớn hơn mục tiêu; latency phần cứng riêng |
| MobileNetV4, ECCV 2024 | UIB, Mobile MQA, hardware-aware NAS; Conv-S khoảng 3.8M | Baseline thực dụng cho mobile | >2M; không có OCR trực tiếp |
| SBCFormer, WACV 2024 | Hybrid cho CPU SBC; xấp xỉ 80% ImageNet top-1, 1 FPS Raspberry Pi 4 theo paper | Nhấn mạnh đo phần cứng đích | Tốc độ không realtime; chưa đo recognizer |
| CPUBone, CVPR Findings 2026 | Tối ưu MACs và throughput trên CPU, kiểm tra transfer detection/segmentation | Gợi ý đo MAC/s và runtime thực | Chưa thấy OCR; biến thể lớn hơn 1M |

> Những backbone trên là ứng viên chuyển giao. ImageNet top-1 không chứng minh khả năng nhận dạng chữ.

## Điều rút ra cho mục tiêu khoảng 1M

1. **Khoảng trống bằng chứng:** đã có backbone 1M có ImageNet result, nhưng chưa có bằng chứng đủ mạnh về recognizer tổng quát xấp xỉ 1M. Nhiều “lightweight” STR nằm ở vài triệu tham số trở lên.
2. **Tổng model quan trọng hơn encoder riêng:** decoder, output head, embedding, từ vựng và padding có thể chiếm đáng kể; phải báo cả tổng params và phân rã module.
3. **Bảo toàn chi tiết không gian:** stride/patch size có thể xóa nét, dấu hoặc ký tự gần nhau. Cần theo dõi feature width, height và receptive field ở đúng crop OCR.
4. **Dữ liệu và decoder là biến lớn:** scaling study/CSD cho thấy data, nhãn nhiễu và decoder có thể chi phối kết quả hơn việc thay backbone.
5. **Latency phải đo lại tại đích:** cố định thiết bị, runtime, precision, batch=1, kích thước crop và đo cả end-to-end latency/throughput/peak memory.

## Đề xuất thí nghiệm tiếp theo

Đây là đề xuất, chưa phải kết quả thực nghiệm.

1. Khóa baseline CTC, dữ liệu và split ảnh độc lập; ghi số tham số toàn recognizer.
2. So biến thể gần 1M với các mốc lớn hơn, giữ cố định decoder, charset, resolution, recipe, augmentation và số updates.
3. Thử CNN, hybrid attention và TinyNeXt-T làm sequence encoder; ablate feature stride để giữ nét ngang.
4. Tách ablation kiến trúc khỏi FLCL/distillation/decoder/output representation.
5. Báo CER, WER/word accuracy, exact match, params, MACs/FLOPs, checkpoint size, activation memory và latency trên thiết bị đích; dùng nhiều seed hoặc uncertainty khi có thể.
6. Chọn trên dev/calibration, giữ holdout độc lập đến khi protocol thí nghiệm khóa.

## Giới hạn và kết luận

1.105 bản ghi chưa được quyết định, 19 mới chuyển tìm toàn văn; do đó bài này không nhận là review cuối. Search Scholar bị cap, còn lượt OCR sensitivity bị 429 một phần. Screening một reviewer; chưa có dual screening, registration hoặc meta-analysis. Thông tin tham số/latency không xác minh được sẽ không được suy đoán.

Trong các công trình đã xác minh, hướng gọn nhẹ phát triển ở encoder/CTC, decoder, weight sharing, biểu diễn ký tự và huấn luyện. Chúng cung cấp ý tưởng phù hợp hơn backbone phân loại thuần túy vì trực tiếp xử lý căn chỉnh chuỗi và hình thái ký tự. Tuy nhiên, chưa đủ bằng chứng rằng recognizer tổng quát khoảng 1M giữ được độ chính xác cạnh tranh. Cần một benchmark có kiểm soát trên toàn recognizer, split độc lập và runtime đo trên phần cứng mục tiêu.

## Tài liệu sơ cấp đã dùng

1. Rang et al., [Scaling Law for STR, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Rang_An_Empirical_Study_of_Scaling_Law_for_Scene_Text_Recognition_CVPR_2024_paper.html).
2. Zhan et al., [Free Lunch / FLCL, ACM MM 2024](https://doi.org/10.1145/3664647.3681045); [repo tác giả](https://github.com/YChenL/FLCL).
3. Cheng et al., [SVIPTR, CIKM 2024](https://doi.org/10.1145/3627673.3679618); [arXiv](https://arxiv.org/abs/2401.10110).
4. Zhang et al., [HierCode](https://doi.org/10.1016/j.patcog.2024.110963); [arXiv](https://arxiv.org/abs/2403.13761).
5. Mas-Candela & Calvo-Zaragoza, [Compact HTR via recursive neural networks, IJDAR 2024](https://doi.org/10.1007/s10032-024-00481-y).
6. Du et al., [SVTRv2, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Du_SVTRv2_CTC_Beats_Encoder-Decoder_Models_in_Scene_Text_Recognition_ICCV_2025_paper.html); [model table](https://github.com/Topdu/OpenOCR/blob/main/configs/rec/svtrv2/readme.md).
7. Maracani et al., [Efficient Model Scaling and Cloze Self-Distillation, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Maracani_Accurate_Scene_Text_Recognition_with_Efficient_Model_Scaling_and_Cloze_CVPR_2025_paper.html).
8. Ma et al., [One2Seq, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/37732).
9. Xu et al., [Mamba-STR, Information Sciences 2026](https://doi.org/10.1016/j.ins.2026.123242).
10. Zeng et al., [TinyNeXt, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Zeng_An_Efficient_Hybrid_Vision_Transformer_for_TinyML_Applications_ICCV_2025_paper.html).
11. Yun et al., [SHViT, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Yun_SHViT_Single-Head_Vision_Transformer_with_Memory_Efficient_Macro_Design_CVPR_2024_paper.html).
12. Wang et al., [RepViT, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html); [repo](https://github.com/THU-MIG/RepViT).
13. Qin et al., [MobileNetV4, ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05647.pdf).
14. Lu et al., [SBCFormer, WACV 2024](https://openaccess.thecvf.com/content/WACV2024/html/Lu_SBCFormer_Lightweight_Network_Capable_of_Full-Size_ImageNet_Classification_at_1_FPS_on_Single_Board_Computers_WACV_2024_paper.html).
15. Nottebaum et al., [CPUBone, CVPR Findings 2026](https://arxiv.org/abs/2603.26425).
