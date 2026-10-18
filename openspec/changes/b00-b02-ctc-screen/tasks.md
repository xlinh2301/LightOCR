# Tasks

- [x] Implement the shared B00–B02 training runner and artifact schema.
- [x] Add preflight split and CTC feasibility audits; do not drop invalid rows.
- [x] Compile-check runner syntax.
- [x] Keep the original remote runner unchanged; the split-aware resolver is verified at SHA-256 9c7cbd649979b98e9c85e00d773bebd8d70c166bae86957d1e8aeb7903ac21f6.
- [x] Verify CUDA and run the B00–B02 configs; each terminal result and CTC/data audit is recorded.
- [x] Run B00 seed 42 (retry03) and B01/B02 seed 42 (retry02; parallel by explicit user request).
- [x] Preserve the first B00 failure: `KeyError: '0438'` in the repeated-target feasibility check before the first optimizer step; `config.json`, `manifest.json`, and `train.log` retained, with no checkpoint or dev metrics.
- [x] Correct the target-length check to use batch target strings and syntax-check the revised runner locally and in MLR_LinhNX.
- [x] Resolve Pilot 007 IDs by unique basename in the physical source train/valid folders without changing frozen train/dev membership; save a preflight audit and source mapping. Test/cross-data folders are not searched.
- [x] Preserve the failed `retry01` output and the interrupted `retry02` B00 output; use a fresh `retry03` root for the completed B00 rerun.
- [x] Reconcile terminal outputs and incrementally update the LightOCR tracker and Drive backups.
