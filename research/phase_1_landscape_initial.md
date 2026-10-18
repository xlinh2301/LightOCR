# Phase 1 — Initial landscape scan (2024–2026)

**Status:** exploratory starter scan, not a systematic review.  
**Search date:** 2026-10-16.  
**Discovery:** web search followed by checks of primary arXiv/CVF/PMLR pages. Semantic Scholar query was attempted from gmoe but returned HTTP 429, so it did not contribute records. No source list here is claimed to be exhaustive.

## Initial source set

| Work | Year / task | Evidence from primary source | Relation to ~1M target |
|---|---|---|---|
| [How Lightweight Can A Vision Transformer Be](https://arxiv.org/abs/2407.17783) | 2024, ImageNet vision classification | Proposes a shared-weight MoE feed-forward design with staged depth/width scaling; the abstract reports a competitive 0.67M-parameter model. This is an arXiv preprint; “competitive” needs table-level verification and independent reproduction. | Directly near target; high-priority source to inspect. |
| [An Efficient Hybrid Vision Transformer for TinyML Applications (TinyNeXt)](https://openaccess.thecvf.com/content/ICCV2025/html/Zeng_An_Efficient_Hybrid_Vision_Transformer_for_TinyML_Applications_ICCV_2025_paper.html) | 2025, ImageNet-1K | The ICCV page reports TinyNeXt-T at 1.0M parameters and 71.5% top-1 accuracy. This is the closest directly evidenced target-scale candidate in this starter set. Inspect the full paper for recipe, latency, and fair baseline protocol. | Exact target scale. |
| [RepViT: Revisiting Mobile CNN From ViT Perspective](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html) | 2024, classification and downstream vision | CVPR paper adapts mobile CNN design using ViT-inspired block/macro/micro choices; the authors report >80% ImageNet top-1 with 1.0 ms on iPhone 12 for a model in their family. The stated latency is device-specific and should not be compared directly with other hardware. | Useful larger/mobile baseline; exact parameter count for the cited configuration must be extracted from paper tables before comparison. |
| [MobileNetV4 — Universal Models for the Mobile Ecosystem](https://arxiv.org/abs/2404.10518) | 2024, mobile vision ecosystem | Introduces Universal Inverted Bottleneck variants, Mobile MQA, hardware-aware NAS and distillation; abstract reports 39% speedup for Mobile MQA and heterogeneous-device Pareto behavior. These are author-reported results and do not show a ~1M configuration in the abstract. | Design/measurement reference; extract per-variant parameter and latency tables. |
| [MobileMamba: Lightweight Multi-Receptive Visual Mamba Network](https://openaccess.thecvf.com/content/CVPR2025/html/He_MobileMamba_Lightweight_Multi-Receptive_Visual_Mamba_Network_CVPR_2025_paper.html) | 2025, classification and downstream vision | CVPR source reports MobileMamba-T2 at 8.8M parameters, 255M FLOPs, 73.6% ImageNet top-1 at 192 resolution. A separate table includes baselines around 1.3M, but those baselines predate the target window. | Larger comparison point, not a ~1M candidate. |

## Initial synthesis

1. **The 1M target is plausible, but evidence is sparse and protocol-sensitive.** The starter set contains a 0.67M preprint and a reported 1.0M TinyNeXt-T result. Their datasets, training recipes, and evidence strength differ. Do not rank them from abstract-level numbers.
2. **Hardware-aware design matters as much as parameter count.** RepViT and MobileNetV4 explicitly optimize mobile execution. Parameter count alone cannot establish latency, memory, or energy efficiency.
3. **Architecture families differ in maturity and evidence.** The mLiT report is a single arXiv preprint; TinyNeXt and RepViT have conference proceedings. This is a provenance distinction, not a judgment that a model is better.
4. **Transfer to text recognition remains unknown.** ImageNet classification accuracy does not establish performance on long, narrow text crops. Phase 2 must test sequence feature resolution, receptive field, width preservation, and recognition-specific training.
5. **The 2026 slice is missing.** This scan is incomplete for 2026 and must be extended before drawing year-over-year trends.

## Next screening actions

- Resolve Semantic Scholar HTTP 429/quota before relying on API retrieval.
- Search conference proceedings and arXiv systematically for 2024, 2025, and 2026, recording exact queries and screening decisions.
- Read full papers and supplements for TinyNeXt, mLiT, RepViT, MobileNetV4, and MobileMamba. Extract all model variants and exact metric protocols.
- Add code/checkpoint availability, licensing, FLOPs, latency hardware, memory, training data and limitations to the extraction table.
- Keep this scan exploratory. Do not select Phase 2 architecture or thresholds from holdout results.
