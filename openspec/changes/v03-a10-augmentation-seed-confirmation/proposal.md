# V03 — A10 augmentation seed follow-up

## Goal

Assess whether the strong seed-42 A10 screen repeats across the predeclared seeds 1337 and 2026 before considering L03/L04. Keep the existing architecture, augmentation severity, optimizer, budget, data split, preprocessing and decoder fixed.

## Protocol

- Model: B02 depthwise-CNN + Conv1D + CTC, 92,108 parameters.
- Input: RGB 32×192; digits 0–9; CTC blank index 0; greedy decoding.
- Training only: A10 combined degradation plus mild synthetic glare.
- Data: frozen Pilot 007 base-fit train split (1,467) and model-dev split (244). Keep dev clean; do not read test or cross-data.
- Seeds: seed 42 is the already-completed screening run; run 1337 then 2026 in separate output roots.
- Budget: 50 maximum epochs, patience 10, batch size 32, four workers, AdamW lr 0.001 and weight decay 0.0001.
- Select checkpoints by lowest dev CER, exact-match tie-break. Mark all results Preliminary because seed42 informed selection on this same exposed split.

## Gate

V03 does not establish repeatable CTC convergence if follow-up seeds fail to reproduce the seed-42 nonblank/exact-match performance. Keep L03/L04 Deferred in that case. This follow-up estimates seed variability only; it is not an independent holdout evaluation.

## Outcome

Completed sequentially. Seed 1337: best epoch 29, CER 64.4876%, exact 2/244. Seed 2026: best epoch 16, CER 70.0530%, exact 1/244. Including the seed-42 screen, mean CER was 53.7986% (sample SD 23.4991 percentage points); mean exact-match was 11.3388% (sample SD 18.5757 percentage points). The follow-up seeds did not reproduce the seed-42 gain. L03/L04 remain Deferred.

Artifacts, checkpoint hashes and per-seed metrics are recorded in the Experiment Tracker and `experiments/run_registry_a10_seed_confirmation_20261018.csv`.
