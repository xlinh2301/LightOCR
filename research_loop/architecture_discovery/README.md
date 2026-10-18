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
- `train.py`: single-config trainer; writes a manifest, all-row CTC audit, training history, best checkpoint, dev predictions and run summary.
- `verify_predictions.py`: reconstructs EM/CER and error cases from saved predictions and cross-checks expected development IDs and labels.
- `controller.py`: initializes a hashed campaign, launches one queued run, records events atomically, reconciles after restart, and refuses launches until `sanity_results.json` is marked passed.
- `sanity.py`: audits both fixed splits for CTC feasibility and performs a deterministic tiny-set memorization run through the actual crop loader; writes `sanity_results.json` only with explicit evidence and a pass/fail decision.
- `campaign.json`: predeclared seven-run first-family comparison.
- `test_loopocr.py`, `test_controller.py`, `test_sanity.py`: component, recovery, and feasibility tests.
- `architecture_hypotheses.md`, `architecture_registry.csv`, `experiment_registry.csv`, `literature_landscape.md`: rationale and evidence trail.

## Intended remote flow

1. Use a clean isolated checkout/worktree of this committed branch. Do not alter the current remote untracked checkout.
2. Local syntax/model/controller/metric/feasibility tests pass 14/14; the deployed revision's model/controller suite passed 12/12 inside `MLR_LinhNX`. Run the updated `sanity.py` there to audit both fixed splits and demonstrate tiny-set learning before accepting the gate.
3. Write `research_loop/sanity_results.json` with status `passed` only when all predeclared gates have actual evidence.
4. Initialize the remote output root using `controller.py init --campaign campaign.json --repo-path <isolated-checkout> --workdir /media/gmo/linhnx/workspace/workdir_Research --max-runs 30`.
5. Run `controller.py run --state <output-root>/research_loop/search_state.json` from the training environment. Keep the controller under a durable process manager on gmoe. It will sequence the seven runs and stop on the first failure or after the queue ends.
6. Reconstruct every completed run with `verify_predictions.py`; reconcile against manifests, history, checkpoint hashes and the Experiment Tracker before deciding the next hypothesis.

Do not initialize or launch against the current remote folder until its untracked state has been preserved and a separate checkout has been verified.
