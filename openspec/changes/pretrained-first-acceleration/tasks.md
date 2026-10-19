# Tasks

- [x] Record Run19 final metrics, rejection and verified artifact hashes/links in the tracker.
- [x] Pivot tracker guidance/plan from scratch architecture search to pretrained teacher screening.
- [ ] Audit the MLR_LinhNX runtime for Paddle inference/training support and available GPU libraries.
- [ ] Select official PP-OCRv5 Mobile and English/numeric SVTR/RepSVTR checkpoints; record source URLs and hashes.
- [ ] Implement a common zero-shot evaluator preserving raw decoded strings and checkpoint provenance.
- [ ] Run zero-shot teacher screening on frozen exposed model-dev only and reconstruct metrics independently.
- [ ] Fine-tune promising teacher(s) on the existing train split: frozen, partial and full tuning.
- [ ] Build PretrainedLoopOCR only after confirming a suitable sequence-preserving backbone and teacher evidence.
- [ ] Evaluate KD only if a teacher demonstrably outperforms the matched LoopOCR control.
- [ ] Reconcile all run records and update source/docs/Drive/Sheet without touching test/cross-data.
