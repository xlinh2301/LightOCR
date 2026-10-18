# Next experiments

1. Keep the completed A01/A02/A06/A09/A10 screen and A10 seed-variation runs Preliminary; all used the exposed Pilot 007 model-dev split.
2. V03 is complete for A10 seeds 42, 1337 and 2026. Seed42 remains a selection screen; the follow-up seeds did not replicate its gain (2/244 and 1/244 exact matches, CER 64.49% and 70.05%).
3. Leave L03/L04 Deferred. The observed variation does not establish stable CTC convergence. Do not use test or cross-data results to reverse this gate.
4. Before starting any new loss experiment, predeclare an operational stability criterion and a clean, functioning baseline protocol; document that the current A10 follow-up is not independent confirmation because seed42 was selected on the same exposed development split.
5. Only after architecture, augmentation, loss choices and thresholds are frozen should an independent holdout or cross-data evaluation be authorized.

## Current gate decision

L03/L04 are deferred. A10 results across seeds 42/1337/2026 have mean CER 53.80% (sample SD 23.50 pp) and mean exact match 11.34% (sample SD 18.58 pp). Two follow-up seeds were near-zero exact match; stable CTC convergence is not established. Clean B02 seed42 remains weak (CER 71.38%, exact match 0/244). No test/cross-data samples were read.
