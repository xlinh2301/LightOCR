# Tasks

- [x] Inspect remote instructions, Git state, active training jobs, GPU and output roots before launch.
- [x] Freeze the A10 seed-follow-up protocol and use distinct output roots for seeds 1337 and 2026.
- [x] Run seed 1337, then seed 2026, without loading test or cross-data.
- [x] Reconcile each run's result, history, predictions, checkpoint hash and data audit; retain the stale-running manifest/config status in a reconciliation sidecar.
- [x] Back up each artifact bundle and checkpoint to Drive; update the Experiment Tracker after each seed completes.
- [x] Compute descriptive three-seed mean and sample standard deviation; retain Preliminary status because seed42 was selected on the same exposed model-dev split.
- [x] Defer L03/L04 because the A10 gain did not repeat across the follow-up seeds.
