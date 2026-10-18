# Next architecture decision

**Current decision:** inspect sample-level failures from the completed 48×320 run before selecting the next architecture or training change.

## Evidence

- The first seven-run seed-42 screen completed with best EM 18/244 (7.38%) and CER 48.59% on shared K=4.
- Scaling the same topology to 998,028 parameters improved to 45/244 EM (18.44%) and CER 39.05% on the previously exposed Pilot 007 model-development split.
- Mild train-only augmentation on the same architecture/protocol increased seed-42 model-dev exact strings from 45/244 to 98/244 (+21.72 percentage points) and reduced CER from 39.0459% to 23.0565% (−15.99 points).
- A controlled 48×320 follow-up, holding seed42, split, K=4 width320/FF640 model, optimizer, batch size, epoch budget, and train-only augmentation fixed, completed at 113/244 exact (46.31%) and CER 18.0212%. Independent reconstruction matched all 244 IDs and labels: 204/1,132 edits (91 substitutions, 68 deletions, 45 insertions), with 40 wrong same-length outputs. This is +15 exact strings and −5.04 CER points versus the 32×192 augmented run, but remains single-seed exploratory evidence on the previously exposed development split.
- The 48×320 run's best epoch was 46 (train loss 0.01411); final epoch 50 had 45.08% exact and 18.64% CER. Parameter count was 1,003,148; peak VRAM was 419,947,008 bytes and runtime 171.287 s.
- The 113/244 result remains far below the ≥220/244 needed for 90% exact match. It is not independent validation. Test and cross-data remain unopened.
- Data audit and CTC feasibility passed for all 1,467 train and 244 model-development samples. The 48×320 audit found no missing or ambiguous IDs.

## Next decision gate

Review the 131 failed model-development samples from the 48×320 run and compare them with the 32×192 predictions. Summarize failures by reference length and edit type, then inspect corresponding model-development images for low resolution, crop/resize artifacts, label ambiguity, and repeated digits. Use only this exploratory model-development data for diagnosis; never use test/cross-data. Predeclare one controlled follow-up after this review, with a written hypothesis and frozen config.

The configurable-dimension implementation is on branch `codex/architecture-discovery-loop`; 48×320 passed local and MLR component tests before launch. The controller now records 10 completed runs out of its 30-run budget and no active job. Any subsequent run must use the existing controller and one GPU at a time. Preserve failures and do not auto-retry or terminate jobs.

The Drive artifact bundle for the 48×320 run is pending upload because the local VPN tunnel is intermittently resetting. The run directory and independently reconstructed metrics are preserved on gmoe. The Pilot 007 development split is exposed; any result on it must be described as an exploratory development result, not independent validation. Do not start confirmation seeds until a recipe is frozen and an independent holdout protocol is documented.


## 2026-10-19 local fallback result and next gate

The local 48x320 run used a new 2,201/244 exploratory split because the gmoe SSH path initially failed. It completed at 152/244 exact (62.2951%), CER 11.7491%, best epoch 40; independent reconstruction matched all IDs/labels. This is 49 more exact strings than the prior remote 48x320 run, but the train count and hardware/software differ, so this is not a controlled comparison. The largest observed weakness is six-digit exact match (1/17); this estimate is imprecise. The frozen best checkpoint was selected by lowest CER (epoch 40), not best exact-match epoch. The target at least 220/244 remains unmet.

Next: compare the same split and training setup with the predeclared stronger train-only augmentation variant in the report. Keep the model, data, seed, resolution, optimizer, and training budget fixed. Do not use the exposed model-dev set to claim independent confirmation. No test/cross-data has been read.
The independently verified run bundle is backed up at https://drive.google.com/file/d/1hOai1z3kH_76fcJPzKBjFgNH5jmgk-3q/view; checkpoint at https://drive.google.com/file/d/1sJyO6dHIz5K66L4B4KhQsWzCZrc4m88n/view.

## 2026-10-19 stronger-augmentation result and next gate

The controlled strong-augmentation run `loopocr-local-split2201-48x320-strongaug-s42` completed 44 epochs, selecting epoch 34 by lowest model-dev CER. On the same reconstructed 2,201/244 split and seed as the mild-augmentation fallback, independent reconstruction verified 167/244 exact (68.4426%), CER 108/1,132=9.5406%, with 46 substitutions, 49 deletions, 13 insertions, and 23 wrong same-length strings. This is +15 exact samples (+6.15 percentage points) and −2.21 CER points versus mild augmentation on this same exploratory development split. It remains 21.56 percentage points below the ≥90% target and is not independent validation. The model has 1,003,148 parameters; runtime 884.849s; peak VRAM 419,947,008 bytes. Preflight retained all rows, found zero CTC-infeasible samples, and did not read test/cross-data. Checkpoint SHA-256 `4703a1d3f23723f1151c84b8d869554955afa05323902b12a9e17999495b097a`; resolved config SHA-256 `b2436497837c8d58d70eb4c64a7b468db4a76812ab972d43cc6b471eea7b5956`; predictions SHA-256 `922f20497436480ea93c4fe631ceeb25f629a93621bc20cda778fbb3d122c5a7`. The manifest's source commit field was blank, but post-run inspection verified the clean clone at `aedd852` and exact trainer/model file hashes in the manifest.

Artifact bundle: https://drive.google.com/file/d/1tUn6hXZdb_LzmasPVjtKhSfPrpN6OYD1/view; report: https://drive.google.com/file/d/1GsTpKVf0UejxxXnzzxsQL0B3EgDhiVOg/view; checkpoint: https://drive.google.com/file/d/1S79U10HUqE6VDRjcj1r_05G5YWfIpgns/view.

Next one-factor screen: run shared K4 width320/FF640, seed42, strong augmentation, and the same split/training protocol at 64×320, changing only input height from 48 to 64. Hypothesis: retaining more vertical glyph detail improves substitutions/deletions without increasing model parameters. Record the model-dev metric as exploratory only. Freeze no recipe and do not access test/cross-data.

## 2026-10-19 height64 result and next gate

The controlled `loopocr-local-split2201-64x320-strongaug-s42` run completed 37 epochs; best epoch27. Independent reconstruction verified all 244 IDs/labels and measured 167/244 exact (68.4426%), CER 110/1,132=9.7173%, with 52 substitutions, 53 deletions, 5 insertions and 29 wrong same-length strings. Compared with strong augmentation at 48×320 on the same seed and exposed split, exact match was unchanged (167/244) and CER worsened by 0.18 percentage points (110 vs 108 edits). Thus the tested height increase showed no benefit. Params remained 1,003,148; runtime 788.673s; peak VRAM 470,999,552 bytes. Test/cross-data were not read.

Resolved config SHA-256 `ea15c162f6c909bae3767ae696d923dfb83eb1334b0875180bb7be26817a93bf`; checkpoint SHA-256 `381578da58a043d7d0fbaffd7977e00f645420b806524fd426441cad46e5e489`; predictions SHA-256 `ee4290764cc4e83df1c4d1e18c4c63f4d797a78723d1fae263a13b889c3c1381`. Bundle: https://drive.google.com/file/d/11jtWOtWYKrCYpkyYzaMijKRbuRtX7sq5/view; report: https://drive.google.com/file/d/1mLnlniTZqPRnj_axMaxybDx0JZW6xDMy/view; checkpoint: https://drive.google.com/file/d/1h_WuOg_UeTYI1vL_Y6JSuMdODFho6Z6X/view.

Next controlled screen: use 48×384 with strong augmentation and the same seed42/split/model width320/FF640/optimizer/batch/schedule. Increase positional capacity from 80 to 96 to match T=96 at width384. Hypothesis: added horizontal resolution may preserve narrow strokes and reduce substitutions/deletions. This is a one-factor input-width/resolution screen; compare only on this exploratory, previously exposed model-dev split. Target remains ≥220/244; do not freeze or claim confirmation.
