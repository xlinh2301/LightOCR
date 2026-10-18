# N08, N09 and N11 CTC neck screen

Run the next three neck hypotheses from the LightOCR experiment matrix sequentially with the same frozen Pilot 007 train/dev split, image preprocessing, seed 42, optimizer, batch size, and early-stopping rule as the previous neck screen. These are exploratory runs on an already exposed development set.

- N08: Sobel edge branch projected to the common sequence width and fused with RGB features through a learned sigmoid gate.
- N09: learned lightweight structural branch from RGB, projected and fused with RGB features through the same gate form.
- N11: RGB backbone with a wider temporal Conv1D control and no structural branch.

Save full provenance, data/CTC audits, history, development predictions, checkpoint and metrics per run. Do not load test or cross-data samples.

## Acceptance criteria

- All three runs execute one at a time on seed 42 using the same 1467/244 frozen split and no dropped samples.
- Tensor layouts are explicit: feature maps `[B,C,H,W]`; temporal sequences `[B,W,C]`; Conv1D inputs `[B,C,W]`.
- Report exact parameter counts and treat N11 as a capacity control, not a perfectly parameter-matched control unless measured counts support that description.
- Preserve failures and any earlier artifacts. Upload run artifacts/checkpoints to the existing Drive folders and update the existing experiment tracker after each completed run.
- Results remain preliminary and exploratory; do not select models using test or cross-data results.
