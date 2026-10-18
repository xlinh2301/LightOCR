# A01, A02, A06, A09 and A10 augmentation screen

Run the next queued augmentation hypotheses sequentially on the B02 depthwise-CNN + Conv1D + CTC baseline, using seed 42, the frozen Pilot 007 train/dev IDs, and the same optimization budget as prior screens. Apply stochastic corruption to training images only. Keep model-dev images clean and do not load test or cross-data samples.

Use conservative, label-preserving severity levels frozen before training:

- A01: brightness and contrast factors sampled independently from [0.80, 1.20].
- A02: Gaussian blur radius sampled from [0.20, 1.00] pixels.
- A06: soft white elliptical glare with alpha [0.10, 0.25], blurred mask and area limited to 20% of the crop.
- A09: brightness/contrast [0.85, 1.15], optional blur radius [0.20, 0.80], Gaussian pixel noise sigma [3, 10]/255 scale, and JPEG quality [45, 85].
- A10: A09 plus the same mild glare as A06.

Document these as screen-level operational definitions, not a claim that the corruption benchmark covers real-world distribution shifts. Save config, manifest, data and CTC audits, history, clean-dev predictions, result and checkpoint. Back up each run and update the experiment tracker before starting the next one.

## Acceptance criteria

- B02 architecture and training settings are identical across the five runs; only train-time augmentation differs.
- No augmentation is applied to dev/test/cross-data.
- All 1,467 train and 244 dev records are retained; invalid CTC lengths fail loudly.
- Record exact parameter counts and all observed dev metrics as preliminary single-seed exploratory evidence.
- L03/L04 remain gated on stable CTC convergence as required by the project protocol.
