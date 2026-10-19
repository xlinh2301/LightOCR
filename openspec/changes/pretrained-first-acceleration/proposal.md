# Change: prioritize pretrained OCR teachers before architecture search

## Why

LoopOCR-v1 has reached only about 67–69% exact match on the exposed model-development split across seeds. Runs 17–19 found no useful gain from learned vertical pooling; Run19 column projection scored 156/244 exact (63.9344%) and CER 12.1025%, worse than the matched mean-pooling comparator. Further scratch architecture variants have low expected information value relative to transfer from pretrained OCR representations.

## Strategy

1. Evaluate the cheapest suitable pretrained recognition teachers first: PP-OCRv5 Mobile Recognition and an English/numeric SVTR or RepSVTR CTC model. Record official source, exact checkpoint provenance/hash, preprocessing, dictionary, output head and decoder.
2. Run zero-shot inference on the existing frozen model-development IDs only. Preserve raw predictions, then independently reconstruct exact match and CER. Ensure numeric strings preserve leading zeros and do not use labels or alignments during inference.
3. Fine-tune promising teachers only on the existing training split, comparing frozen backbone, partial unfreezing and full fine-tuning with separately logged learning rates. Preserve original teacher checkpoints and zero-shot predictions.
4. If justified by teacher results, build PretrainedLoopOCR using a verified lightweight pretrained backbone, preserved horizontal sequence resolution and the existing weight-tied K4 neck. Compare K1/K4 and scratch/pretrained initialization, beginning frozen and progressively unfreezing.
5. Attempt teacher-to-student CTC/posterior, feature and intermediate-loop distillation only if a teacher demonstrably outperforms LoopOCR. Keep the full inference student near 1M parameters where possible and report parameters, FLOPs, latency and accuracy.
6. If teachers remain below target, audit residual errors and assess authorized train-only synthetic data or additional authorized data with device/source duplicate controls.

## Evidence boundary and success

The development IDs have been exposed by prior model selection. Results on them are exploratory and cannot establish independent generalization. Never inspect, rank, tune on, or select using test/cross-data. Screen one/few candidates before three-seed confirmation. The performance target is strictly >90% exact match on each of seeds 42, 1337 and 2026 and mean >90% on development; any such result remains distinct from independent holdout validation.

## Acceptance

- Run19 is reconciled and marked complete/rejected in the registry.
- Teacher inference records source/checkpoint hashes, preprocessing, dictionary, decoder, sample-level predictions, exact match and CER.
- Fine-tuning uses only the frozen training split; every completed or failed run is preserved and synchronized.
- The next action follows the pretrained-first sequence above. No image-size/height-pooling variants are launched until pretrained transfer is assessed.
