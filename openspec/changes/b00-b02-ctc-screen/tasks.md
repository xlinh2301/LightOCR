# Tasks

- [x] Implement the shared B00–B02 training runner and artifact schema.
- [x] Add preflight split and CTC feasibility audits; do not drop invalid rows.
- [x] Compile-check runner syntax.
- [ ] Transfer source to gmoe without overwriting existing files.
- [ ] Smoke-check imports, CUDA, model forward/backward, and CTC lengths in MLR_LinhNX.
- [ ] Run B00, B01, and B02 sequentially with seed 42.
- [x] Preserve the first B00 failure: `KeyError: '0438'` in the repeated-target feasibility check before the first optimizer step; `config.json`, `manifest.json`, and `train.log` retained, with no checkpoint or dev metrics.
- [x] Correct the target-length check to use batch target strings and syntax-check the revised runner locally and in MLR_LinhNX.
- [x] Resolve Pilot 007 IDs by unique basename in the physical source train/valid folders without changing frozen train/dev membership; save a preflight audit and source mapping. Test/cross-data folders are not searched.
- [ ] Preserve the failed `retry01` output; use a fresh `retry02` output root after the resolver fix.
- [ ] Run B00; run B01 and B02 sequentially only after each preceding run completes successfully.
- [ ] Reconcile run artifacts and incrementally update the LightOCR tracker.
