# Next experiments

1. Keep the completed A01/A02/A06/A09/A10 screen and A10 seed-variation runs Preliminary; all used the exposed Pilot 007 model-dev split.
2. V03 is complete for A10 seeds 42, 1337 and 2026. Seed42 remains a selection screen; the follow-up seeds did not replicate its gain (2/244 and 1/244 exact matches, CER 64.49% and 70.05%).
3. Leave L03/L04 Deferred. The observed variation does not establish stable CTC convergence. Do not use test or cross-data results to reverse this gate.
4. Before starting any new loss experiment, predeclare an operational stability criterion and a clean, functioning baseline protocol; document that the current A10 follow-up is not independent confirmation because seed42 was selected on the same exposed development split.
5. Only after architecture, augmentation, loss choices and thresholds are frozen should an independent holdout or cross-data evaluation be authorized.

## Current gate decision

L03/L04 are deferred. A10 results across seeds 42/1337/2026 have mean CER 53.80% (sample SD 23.50 pp) and mean exact match 11.34% (sample SD 18.58 pp). Two follow-up seeds were near-zero exact match; stable CTC convergence is not established. Clean B02 seed42 remains weak (CER 71.38%, exact match 0/244). No test/cross-data samples were read.
## Architecture discovery loop (2026-10-19)

- The 2,201/244 local in-domain exploratory split fallback reached 152/244 exact (62.2951%), CER 11.7491% with mild augmentation.
- The controlled stronger-augmentation run reached 167/244 exact (68.4426%), CER 9.5406%, best epoch34; +15 exact samples and −2.21 CER points on the same previously exposed model-dev split. Both runs remain exploratory and below the ≥90% target.
- Controller: 11 of 30 remote run entries completed; the local fallback is an additional completed run outside controller state. No active GPU job at this update.
- Next screen: change only input height 48→64 while holding width320, shared K4 width320/FF640, strong augmentation, seed42, split, optimizer and budget fixed. Hypothesis: additional vertical detail may reduce character substitutions/deletions. Preserve all failures and do not use test/cross-data.
- Strong-augmentation artifacts: run bundle https://drive.google.com/file/d/1tUn6hXZdb_LzmasPVjtKhSfPrpN6OYD1/view; report https://drive.google.com/file/d/1GsTpKVf0UejxxXnzzxsQL0B3EgDhiVOg/view; checkpoint https://drive.google.com/file/d/1S79U10HUqE6VDRjcj1r_05G5YWfIpgns/view.

## Architecture discovery loop update (2026-10-19)

- Completed controller run 12/30: 64×320 strong augmentation, seed42, 2,201/244 exploratory split. Independently reconstructed 167/244 exact (68.4426%), CER 9.7173%, best epoch27. It matches the 48×320 run's exact count but has two more edits and CER +0.18 pp; no observed benefit from added height.
- Target ≥220/244 remains unmet. The exposed model-dev set supports exploratory tuning only; no test/cross-data access.
- Next one-factor screen: input 48×384, with `max_steps=96` to match T=96, and all other settings held fixed against the strongaug 48×320 run.
- Run bundle https://drive.google.com/file/d/11jtWOtWYKrCYpkyYzaMijKRbuRtX7sq5/view; report https://drive.google.com/file/d/1mLnlniTZqPRnj_axMaxybDx0JZW6xDMy/view; checkpoint https://drive.google.com/file/d/1h_WuOg_UeTYI1vL_Y6JSuMdODFho6Z6X/view.
