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


## Run 13: width 384 result and seed-stability follow-up (2026-10-19)

The controlled loopocr-local-split2201-48x384-strongaug-s42 run completed all 50 epochs. The checkpoint was selected by lowest model-dev CER at epoch 47: independently reconstructed exact match was 165/244 (67.62295%) and CER was 115/1,132 (10.1590%), with 54 substitutions, 40 deletions, 21 insertions, and 28 wrong same-length strings. Epoch 50 reached the run's maximum exact match, 166/244 (68.0328%), but had worse CER and was not selected. This is exploratory evidence from the previously exposed model-dev split.

Relative to strong augmentation at 48x320 (167/244 exact, CER 9.5406%), width384 produced two fewer exact strings and 0.62 percentage points higher CER. The resolution increase did not help on this split. The model has 1,008,268 parameters; runtime was 1,037.49 s; peak VRAM was 493,828,608 bytes. Independent reconstruction verified all 244 expected IDs and labels with no missing, duplicate, unexpected, or truth-mismatched rows. Config SHA-256 0bdc454fceda1f552f51405bcdad939fc94fbad795c59e04f435d967a955b823; checkpoint SHA-256 e4dde14489120cba214001d655a01f55f3fb713bdc3f671f9cf494a8f8d61afe; predictions SHA-256 677d8c3334aea2f0b646844fc6e147f32431946a8f05ed5ad2c5a50ec7b8f43e. Run bundle: https://drive.google.com/file/d/1jZsFdXeo04ORCx9nclxxQw4Scqg8YMBO/view; checkpoint: https://drive.google.com/file/d/1YJawFR0898SHfj74nC1FfYOb3PojiHZU/view.

### Next candidate

Run loopocr-local-split2201-48x320-strongaug-s1337 with the best current recipe, changing only seed 42 to 1337. This estimates seed sensitivity and continues the user-defined per-seed target check; it remains exploratory and is not confirmatory because the development IDs are exposed. Freeze 48x320, shared K4 width320/FF640, strong train-only augmentation, 50-epoch budget, batch32, optimizer/schedule, split and checkpoint-selection rule. Test/cross-data remain closed. The >90% exact-match target has not been met.

## Run 14: seed 1337 replication and next gate (2026-10-19)

Run 14/30 (`loopocr-local-split2201-48x320-strongaug-s1337`) completed at best epoch 47. Independent reconstruction verified all 244 IDs and runtime labels: 163/244 exact (66.8033%), CER 112/1,132=9.89399%, 57 substitutions, 41 deletions, 14 insertions, and 34 wrong same-length strings. The model has 1,003,148 parameters; runtime 1,004.16 s; peak VRAM 419,947,008 bytes. The seed42 strongaug 48×320 result was 167/244 exact and CER 9.5406%; this seed is four strings lower and CER is 0.35 pp higher. These results are exploratory on previously exposed development IDs.

The run bundle and checkpoint are synced to Drive: [bundle](https://drive.google.com/file/d/18y6S6OPJKTTo-ZvFt_27JB1a2xKCXKtx/view), [checkpoint](https://drive.google.com/file/d/1727SDlPkRk2iiHnhnaVNT_uj2jpcnx7Z/view). Config SHA256 `d0177cbfff0888c31950d5830bea4e6a13df1d390ba67244b2d1ced315b39d6a`; checkpoint SHA256 `8a66486946e42b007426546777a1829dd59d73a895d415a8bc368631f97f00de`; predictions SHA256 `a8d1caba2629206914728c1d8c5e42a3ff627b5627c8dde477cfbc0bbb060692`; bundle SHA256 `5e86179844f936201b6d298d48beb3f5dc829999f5d1399a0a33da91a7b8c359`.

Provenance audit: the run manifest omitted `source_commit`; its `train.py` content hash resolves to Git commit `4dc2fb5`, and `loopocr.py` matches. The candidate config's `label_source_sha256` (`fc5995…`) differs from the runtime loader's label-file SHA256 (`17a83f…`). The independent verifier used the runtime loader's file and matched all saved prediction truths. Correct this metadata for subsequent candidates and preserve the discrepancy in the record.

### Next candidate and limitations

Run the same predeclared best recipe once with frozen seed 2026, changing only the seed, after recording the runtime label-file SHA256 in the candidate metadata. This completes the requested three-seed exploratory check on the exposed IDs; it cannot serve as independent confirmation or support a >90% generalization claim. Current results for seeds 42 and 1337 are 167/244 (68.44%) and 163/244 (66.80%), respectively, far below the ≥220/244 threshold. Keep test/cross-data closed. After seed2026, reassess the architecture/training bottleneck rather than continuing seed repeats without a new hypothesis.
