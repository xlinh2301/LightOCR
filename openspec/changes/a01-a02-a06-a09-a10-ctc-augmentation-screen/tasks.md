# Tasks

- [x] Inspect remote instructions, Git state, active jobs and GPU before transfer or launch.
- [x] Implement train-only A01/A02/A06/A09/A10 transforms on the unchanged B02 model; syntax and shape-check.
- [x] Transfer runner to gmoe and verify SHA256.
- [x] Run A01, A02, A06, A09 and A10 sequentially on seed 42, preserving failures.
- [x] Reconcile every run's manifest, history, predictions, metrics, checkpoint and data audit.
- [x] Update tracker and back up each run's artifacts/checkpoint to Drive before starting the next run.
- [x] Commit/push source and OpenSpec; upload a versioned source archive.
- [x] Record the L03/L04 gate decision: defer pending three-seed confirmation; A10 seed42 alone does not establish stable CTC convergence.
