# Phase 1 — Semantic Scholar discovery and screened landscape

**As of:** 2026-10-17 (Asia/Saigon)  
**Scope:** General lightweight vision architectures published 2024–2026; target scale around 1M parameters, with larger models retained as comparison points. This is an exploratory discovery pass, not a systematic review.

## Retrieval record

Semantic Scholar Graph API was queried from the local WSL2 environment. Searches 2–7 succeeded and are saved in `research.db`; their query strings, dates, result counts, and records are in the `searches` and `sources` tables. Searches 6 and 7 each returned 40 records. A subsequent query for lightweight visual state-space models received HTTP 429 and returned no results. Earlier remote and local attempts on 2026-10-16 also returned 429. No retry loop was used.

Saved successful queries:

| Search ID | Query | API results |
|---:|---|---:|
| 2 | lightweight vision architecture | 100 |
| 3 | mobile vision backbone architecture | 50 |
| 4 | tiny vision transformer ImageNet | 50 |
| 5 | RepViT lightweight mobile CNN vision | 20 |
| 6 | efficient lightweight vision backbone ImageNet mobile | 40 |
| 7 | tiny vision model parameter efficient architecture mobile | 40 |

The 300 API result rows are a retrieved pool, not 300 eligible papers. Search 2 in particular was noisy, with many task-specific application papers and records whose year/venue metadata requires checking. Citation counts are time-varying discovery metadata and were not used as an evidence-quality score.

## Screened papers

| Paper | Verified venue/year | Architecture contribution and reported evidence | Relevance to ~1M text-recognition encoder | Evidence status |
|---|---|---|---|---|
| **An Efficient Hybrid Vision Transformer for TinyML Applications (TinyNeXt)** | ICCV 2025 | Proposes Lean Single-Head Self-Attention and stage-specific design; TinyNeXt-T reports 71.5% ImageNet-1K top-1 at 1.0M parameters. | Highest-priority exact-scale reference. Must still test high-resolution text crops and dense spatial feature retention; ImageNet classification accuracy does not imply OCR suitability. | Primary conference paper verified. |
| **RepViT: Revisiting Mobile CNN From ViT Perspective** | CVPR 2024 | Revisits mobile CNN macro/micro design using efficient ViT ideas; official model table reports RepViT-M0.9 at 5.1M parameters, 78.7% ImageNet top-1, and 0.9 ms on iPhone 12 under its reported setup. | Larger comparison point, not a ~1M model. Useful CNN-oriented mobile baseline and deployment reference. | Primary conference paper and official model table verified. |
| **SHViT: Single-Head Vision Transformer with Memory Efficient Macro Design** | CVPR 2024 | Reduces spatial redundancy with a larger-stride patch stem, uses convolution in early stages, and a single-head attention module later; reports speed/accuracy improvements over MobileViTv2 in its test setup. | Architectural comparator for single-head attention and early downsampling. Need to inspect feature-map stride and localization trade-off before OCR transfer. | Primary conference paper verified. |
| **MobileNetV4: Universal Models for the Mobile Ecosystem** | ECCV 2024 | Presents Universal Inverted Bottleneck (UIB), Mobile Multi-Query Attention (Mobile MQA), and hardware-aware NAS; smallest listed MNv4-Conv-S has 3.8M parameters and reports 73.8% ImageNet-1K top-1 plus 2.4 ms Pixel 6 CPU latency in the paper's setup. | Useful larger comparison and deployment baseline, but its smallest listed model is above the ~1M target. | ECCV paper/official TensorFlow model reference verified. |
| **MambaVision: A Hybrid Mamba-Transformer Vision Backbone** | CVPR 2025 | Hybrid hierarchical Mamba/attention backbone. Its reported variants begin around 31.8M parameters in the cited ImageNet table. | Not a ~1M candidate; retain as an over-scale architecture comparison for global-context/token-mixer ideas only. | Primary conference paper and official NVIDIA repository verified. |
| **Vision-LSTM: xLSTM as Generic Vision Backbone** | ICML 2024 Workshop (LCFM) | Adapts xLSTM blocks to a vision backbone, processing patch-token sequences in alternating directions. | Architecture-family reference, not assumed lightweight. Verify its smallest model size and deployment cost before considering it as a candidate. | Workshop record and official repository identified; detailed scale metrics remain to be screened. |

Primary sources: [TinyNeXt / ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Zeng_An_Efficient_Hybrid_Vision_Transformer_for_TinyML_Applications_ICCV_2025_paper.html), [RepViT / CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html) and [official model table](https://github.com/THU-MIG/RepViT/blob/main/README.md), [SHViT / CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Yun_SHViT_Single-Head_Vision_Transformer_with_Memory_Efficient_Macro_Design_CVPR_2024_paper.html), [MobileNetV4 / ECCV 2024 paper](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05647.pdf), [MambaVision / CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Hatamizadeh_MambaVision_A_Hybrid_Mamba-Transformer_Vision_Backbone_CVPR_2025_paper.pdf), [Vision-LSTM / ICMLW 2024 record](https://mlanthology.org/icmlw/2024/alkin2024icmlw-visionlstm/) and [official repository](https://github.com/NX-AI/vision-lstm).

## Initial synthesis

1. The best exact-budget anchor currently found is TinyNeXt-T at 1.0M parameters, while RepViT and SHViT provide efficient mobile CNN/ViT design comparisons. Treat ImageNet top-1 and latency as paper-specific classification evidence, not a fair cross-paper ranking: input resolution, hardware, runtime, and training recipes differ.
2. For OCR, parameter count is only one constraint. Preserve horizontal detail, avoid overly aggressive early spatial downsampling, expose multi-scale features, and measure throughput at the real text-crop aspect ratio. These are transfer hypotheses to validate, not claims established by the cited classification papers.
3. Include one or more larger baselines to quantify the accuracy/latency cost of the ~1M constraint. MambaVision is useful as an architectural reference but its reported model sizes are far outside the target budget.
4. No architecture should be selected from this exploratory scan alone. Phase 2 must separately identify text-recognition-specific encoders, pretraining, sequence modeling, decoding, datasets, and evaluation protocols; then lock train/development/calibration/holdout splits before experiments.

## Next screening actions

- Inspect official configurations/model tables for TinyNeXt, RepViT, SHViT, and MobileNetV4. Record exact parameters, FLOPs, feature strides, training data/recipe, license, and hardware/runtime protocol.
- Expand discovery with model-family searches and citation chasing for efficient CNNs, hybrid ViTs, and state-space vision models; screen conference proceedings and arXiv versions for duplicate records.
- Build an architecture matrix for OCR transfer: input aspect ratio, output feature stride, receptive field, multi-scale outputs, activation/weight memory, batch-1 latency on intended device, and recognizer accuracy/CER.
- Keep this table exploratory. Do not use a future independent holdout to choose an architecture, preprocessing, checkpoint, or threshold.
