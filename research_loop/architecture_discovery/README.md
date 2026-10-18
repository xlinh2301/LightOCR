# LoopOCR-v1 architecture-discovery loop

This directory contains the first bounded architecture screen and a restartable sequential runner. It is source code only; training is not authorized by a controller state until the remote repository, active jobs, split/data provenance and sanity diagnostics have been verified.

## Evidence boundary

- The existing Pilot 007 model-development set has been repeatedly exposed. Scores are exploratory/model-dev only.
- The controller does not read test or cross-data. The trainer resolves only the fixed train/model-dev IDs against the train/valid image folders and writes an explicit audit.
- The controller runs one GPU training process at a time. It never kills or automatically retries a failed/interrupted run.
- A failed run halts the queue as `paused_on_failure`. The user/research agent must inspect the failure and record an evidence-backed decision before a new run is queued.
- Three-seed confirmation is a separate frozen phase. The first screen is one seed and is not evidence of reproducibility.

## Artifacts

- `loopocr.py`: model, CTC length calculation, feasibility helper, and greedy CTC collapse.
- `train.py`: single-config trainer; writes a manifest, all-row CTC audit, training history, best checkpoint, dev predictions and run summary. Optional mild augmentation is applied only to the training loader.
- `verify_predictions.py`: reconstructs EM/CER and error cases from saved predictions and cross-checks expected development IDs and labels.
- `controller.py`: initializes a hashed campaign, launches one queued run, records events atomically, reconciles after restart, and refuses launches until `sanity_results.json` is marked passed.
- `sanity.py`: audits both fixed splits for CTC feasibility and performs a deterministic tiny-set memorization run through the actual crop loader; writes `sanity_results.json` only with explicit evidence and a pass/fail decision.
- `campaign.json`: predeclared seven-run first-family comparison.
- `test_loopocr.py`, `test_controller.py`, `test_sanity.py`, `test_train.py`: component, recovery, feasibility, and train-only augmentation tests.
- `architecture_hypotheses.md`, `architecture_registry.csv`, `experiment_registry.csv`, `literature_landscape.md`: rationale and evidence trail.

## Intended remote flow

1. Use a clean isolated checkout/worktree of this committed branch. Do not alter the current remote untracked checkout.
2. The deployed pre-augmentation revision passed 14/14 tests inside `MLR_LinhNX`; the current augmentation implementation passes 16/16 locally and is awaiting the same MLR check. The both-split CTC feasibility and 16-image train-only memorization gate passed. The first eight runs completed sequentially and every set of 244 model-dev predictions was independently reconstructed; see `screen_20261019_report.md` and the Experiment Tracker.
3. The first screen reached only 18/244 EM at best (shared K=4), far below the >90% development target. It is exploratory because Pilot 007 model-dev has been exposed.
4. Queue evidence-backed follow-ups using `controller.py queue --state <output-root>/research_loop/search_state.json --config <candidate.json> --evidence <relative report path>`. The total budget is 30 runs, including the first seven; preserve sequential single-GPU execution and halt for review after any failure/interruption.
5. The 998,028-parameter shared K=4 follow-up improved to 45/244 EM (18.44%) and CER 39.05%; train loss fell below 0.003 while model-dev CER deteriorated after its best epoch, consistent with strong overfit. The next candidate `next_candidate_1m_aug.json` holds architecture and training settings fixed while adding mild augmentation to training images only.
6. Reconstruct each prediction set independently and reconcile manifest, history, checkpoint hash, logs, and artifacts before the next decision. Keep all test and cross-data data out of selection. Freeze any promoted architecture before the three-seed run; report each seed and summary uncertainty. A result on previously exposed model-dev must be labeled as a development-target result, not independent validation.

Do not initialize or launch against the current remote folder until its untracked state has been preserved and a separate checkout has been verified.
