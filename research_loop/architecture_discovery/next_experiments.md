
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
