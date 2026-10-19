
## LightOCR-1M LoopOCR follow-up (2026-10-19)

- A separate local split (2,201 train / 244 previously exposed model-dev) allowed one 48×320 K4 seed-42 run after a stale Docker network namespace blocked SSH. It reached 152/244 exact (62.30%) and 11.75% CER at best epoch 40. It is exploratory and not comparable to remote 1,467/244 results.
- The failure analysis found a very weak small sample for six-digit strings (1/17 exact), 58 deletions, and 64 substitutions. The inspected examples suggest both blur and high-contrast failure cases; no causal claim is established.
- Next controlled screen: same split, model, seed, resolution, optimizer, schedule and epoch budget; change only train-only augmentation to rotation ±4°, brightness/contrast ±20%, blur p=0.10/radius≤1.0 and Gaussian noise σ=0.04. Use only the exposed model-dev split for exploratory selection; do not touch test/cross-data.
- gmoe access failure was traced to ssh-client staying attached to a stale network namespace after gluetun restart. A separate ssh-client-repaired helper now reaches gmoe intermittently; the original active SSH process was preserved. The remote controller remains 10/30 runs complete.


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
## Run 17: learned vertical attention pooling (2026-10-19)

Run17 completed all 50 epochs at seed2026; checkpoint selection chose epoch46. The independent verifier matched all 244 expected model-dev IDs and runtime labels. Reconstructed exact match was 168/244 (68.85246%), CER 112/1,132=9.89399%, with 53 substitutions, 47 deletions, 12 insertions, 23 wrong-but-same-length strings, and 76 failed strings. Failed strings by reference length: 1/3-digit, 28/4-digit, 32/5-digit, 15/6-digit. Parameter count was 1,003,469; runtime 1,038.16s; peak VRAM 426,199,552 bytes.

The same-seed 48x320 strong-augmentation mean-pooling run15 achieved 169/244 exact with the same 9.89399% CER. Thus attention pooling did not improve selected CER and yielded one fewer exact string than mean pooling. Compared with run16 (100-epoch cap, early stopped), it was eight exact samples higher at identical CER, but that is a secondary exploratory comparison. The exposed model-dev split cannot establish generalization.

Hashes: resolved config ccca88a5c51e76fe23ad690226e62cb0c594c22efc36da44c114cb957db56613; history b4328f42a68b7de19a382da77b4c5f77a6b97844cf6b73ec05e92270dce69264; predictions 2bfd01d506d278263c53bf5ceca6ef654b28a546e67afd3151d0842987de70e3; checkpoint 4c5a94169a9f36379cc46f17ee128f849984cdbdeb7ad29e892d4a66a3e7943e. Split manifest SHA a6355e23ebf1d5300929784412db440858138a8295254fa7cb029c0c1be7f6f4; runtime label SHA 17a83fb545c7fcf3a3d3d4ebf267018d94585d71a3445588c144195e865a3851. The independent verifier report and failure table are in the Drive run bundle. Bundle: https://drive.google.com/file/d/1BYYe28YCXgZnsQVDbrYLiDND5V99UbpO/view; separate checkpoint archive: https://drive.google.com/file/d/1frsyur0WX9eonF97YycSiCQr3zmpKaWX/view.

Manifest source_commit is blank; the recorded train.py SHA resolves to the clean a4376cf source after normalizing Windows line endings, and the raw loopocr.py SHA matches. Training used Quadro RTX 5000 / PyTorch 2.11.0+cu128. Test/cross-data were not accessed.

### Next candidate

Run18 will repeat attention pooling at seed42 with all other settings fixed, comparing against the matched seed42 mean-pooling run13. The run17 single-seed result does not support promoting attention pooling; run18 checks whether any effect is seed-stable. If it again fails to improve, stop spending runs on this pooling variant and move to another predeclared image-structure hypothesis. Keep one GPU job at a time and test/cross-data closed.

## Run18 result and next test

Run18 (seed42 attention pooling) completed at best epoch37/50: 158/244 exact, CER10.86572%; independent reconstruction matched all IDs/labels. It underperformed the matched run11 mean-pooling result (167/244 exact, CER9.5406%), so do not promote attention pooling. Run17 seed2026 also showed no attention-pooling improvement. Next hypothesis: preserve stem-row structure with a learned column projection; write OpenSpec, test shape/parameter invariants, then run one controlled seed42 screen. No test/cross-data access.
