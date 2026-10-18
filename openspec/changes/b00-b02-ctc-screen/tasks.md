# Tasks

- [x] Implement the shared B00–B02 training runner and artifact schema.
- [x] Add preflight split and CTC feasibility audits; do not drop invalid rows.
- [x] Compile-check runner syntax.
- [ ] Transfer source to gmoe without overwriting existing files.
- [ ] Smoke-check imports, CUDA, model forward/backward, and CTC lengths in MLR_LinhNX.
- [ ] Run B00, B01, and B02 sequentially with seed 42.
- [x] Preserve the first B00 failure: `KeyError: '0438'` in the repeated-target feasibility check before the first optimizer step; `config.json`, `manifest.json`, and `train.log` retained, with no checkpoint or dev metrics.
- [x] Correct the target-length check to use batch target strings and syntax-check the revised runner locally and in MLR_LinhNX.
- [ ] After user decision, resume from B00 with the corrected runner; do not start B01/B02 before B00 succeeds.
- [ ] Reconcile run artifacts and incrementally update the LightOCR tracker.
