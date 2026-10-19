# Design

## Phase 1: teacher evaluation

Use the official PaddleOCR model APIs/checkpoint distributions where feasible. Start with the lowest-cost zero-shot run. Treat each recognition package as an adapter behind a common evaluator that accepts image IDs and paths and emits the untouched decoded text, optional confidence, frame/sequence metadata, and provenance. Keep raw model decoding as the primary result; any digit-restricted decoding is a separately named diagnostic, never a silent transformation.

Before inference, audit image color order, resize/normalization/padding, input tensor dimensions, recognition dictionary ordering, CTC blank index and exact string decoding. For each model, record official config and checkpoint URL, checkpoint SHA-256, package/runtime versions, parameter count if available, input and output tensor shapes, model-dev prediction file hash, and independently reconstructed metrics. Do not alter the split or inspect test/cross-data.

## Fine-tuning

Freeze data IDs and preprocessing. First screen a reduced, declared training budget, then compare frozen-backbone/head-only, partial unfreezing and full fine-tuning for the promising teacher. Use separate learning rates for backbone and recognition head. Select checkpoints only on model-dev and retain all attempts.

## PretrainedLoopOCR

Wrap a verified pretrained recognition backbone that exposes a horizontal feature sequence. Preserve or explicitly project the horizontal axis; do not collapse it into a pooled vector. Attach the existing weight-tied K4 Transformer neck and CTC head. Record pretrained backbone source/hash and initialize only compatible tensors, reporting unmatched keys. Compare K1/K4 and scratch/pretrained controls. Begin with a frozen backbone, then progressive unfreezing with distinct optimizer groups and learning rates.

## Distillation and data

Only after a teacher beats the matched LoopOCR control, compare no-KD against CTC posterior/logit KD, feature KD and intermediate-loop supervision. Report student parameters, FLOPs and measured latency. If pretrained transfer remains inadequate, characterize errors and data coverage before training-only synthetic data or sourcing additional authorized data. Keep source/device groups disjoint and detect near-duplicates.

## Operational safety

Serialize GPU jobs. Use existing run roots without overwriting. Record failures, resolved configs, source dirty state, split and label hashes, checkpoints, predictions, histories, metrics and artifact links. Update the existing Experiment Tracker at each completed run. No model-dev success is described as independent validation.
