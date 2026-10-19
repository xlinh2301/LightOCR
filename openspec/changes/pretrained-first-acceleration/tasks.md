# Tasks

- [x] Record Run19 final metrics, rejection and verified artifact hashes/links in the tracker.
- [x] Pivot tracker guidance/plan from scratch architecture search to pretrained teacher screening.
- [x] Audit MLR_LinhNX runtime: Paddle 2.6.2 with CUDA, PaddleOCR/PaddleX and PyTorch present.
- [x] Preserve the first PP-OCRv5 zero-shot failure: PaddleX3.7 requires a Paddle 3 API missing in the shared Paddle2.6.2 runtime; no forward pass or metric occurred.
- [x] Isolate Paddle3 GPU setup in a campaign-local venv so the shared environment stays unchanged.
- [x] Select official numeric-capable PP-OCRv5 Mobile Latin and English SVTR-T CTC model sources.
- [x] Implement a PaddleX zero-shot evaluator preserving raw decoded strings and model file hashes.
- [ ] Run zero-shot teacher screening on frozen exposed model-dev only and reconstruct metrics independently.
- [ ] Fine-tune promising teacher(s) on the existing train split: frozen, partial and full tuning.
- [ ] Build PretrainedLoopOCR only after confirming a suitable sequence-preserving backbone and teacher evidence.
- [ ] Evaluate KD only if a teacher demonstrably outperforms the matched LoopOCR control.
- [ ] Reconcile all run records and update source/docs/Drive/Sheet without touching test/cross-data.
