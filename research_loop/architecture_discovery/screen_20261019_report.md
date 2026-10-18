# LoopOCR-v1 first architecture screen

**Date:** 2026-10-19  
**Source:** initial seven-run screen at `21a442c`; 1M capacity follow-up at `75e2f7d`; augmentation implementation and component-test helper at `c775c50`
**Execution:** gmoe, `MLR_LinhNX`, Quadro RTX 5000 16 GB, Python 3.12.3, PyTorch 2.11.0+cu128  
**Purpose:** compare a compact CNN floor, shared recurrent Transformer refinements, an untied depth control, and a wider CNN control.

## Protocol

Seven configurations ran sequentially with seed 42, batch size 32, AdamW, learning rate 0.001, weight decay 0.0001, a maximum of 50 epochs, and early stopping patience 10. The model uses a 32×192 RGB aspect-preserving crop, a digit vocabulary 0–9 plus CTC blank index 0, and greedy CTC decoding. The fixed Pilot 007 split contains 1,467 train and 244 model-development examples. Model-development was used for checkpoint selection by lowest CER with exact-match tie-break, so all results below are exploratory. The test and cross-data sets were not accessed.

The data audit found 1,711/1,711 requested files present and unique, with no missing or ambiguous IDs. Label SHA-256: `17a83fb545c7fcf3a3d3d4ebf267018d94585d71a3445588c144195e865a3851`. Split manifest SHA-256: `639a03a7113e165e04b9c4dda9e0e2deb10849b13c2154d3679e0fdb93797474`. CTC feasibility checks found zero invalid train rows (1,467) and zero invalid model-development rows (244).

Before training, the deterministic 16-image train-only sanity check reached 15/16 exact strings (93.75%) after 200 optimizer steps; loss declined from 12.6554 to 0.0262. The gate passed. This tiny-set result validates the path can memorize a small subset; it is not a generalization result.

## Results

| Configuration | Parameters | Best epoch | CER (%) | Exact match (%) | Exact strings | Runtime (s) | Peak VRAM (MB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| CNN control | 51,276 | 20 | 67.3145 | 0.4098 | 1/244 | 40.894 | 79.59 |
| Shared K=1 | 184,140 | 10 | 59.0989 | 1.2295 | 3/244 | 33.364 | 94.85 |
| Shared K=2 | 184,268 | 32 | 55.8304 | 2.4590 | 6/244 | 67.135 | 104.66 |
| Shared K=4 | 184,524 | 23 | 48.5866 | 7.3770 | 18/244 | 62.823 | 125.77 |
| Shared K=6 | 184,780 | 21 | 50.9717 | 6.5574 | 16/244 | 67.269 | 146.88 |
| Untied depth 4 | 581,452 | 26 | 54.0636 | 2.4590 | 6/244 | 69.899 | 130.31 |
| CNN-wide control | 83,788 | 12 | 65.7244 | 0.0000 | 0/244 | 32.368 | 87.34 |

Every model-development prediction file was independently reconstructed against all 244 frozen IDs and labels. The reconstructed metrics matched the run summaries. All seven checkpoints, configs, manifests, histories, logs, predictions, and verification outputs have versioned Drive bundles in the tracker.

## Capacity follow-up

After the initial seven-run screen, the best-supported topology (shared K=4) was scaled from 184,524 to 998,028 parameters while holding the training protocol and seed fixed.

| Run | Parameters | Best epoch | CER (%) | Exact match (%) | Exact strings | Runtime (s) | Peak VRAM (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shared K=4, width 320 / FF 640 | 998,028 | 31 | 39.0459 | 18.4426 | 45/244 | 77.757 | 213.63 |

Independent reconstruction found 442 edits over 1,132 reference characters (253 substitutions, 141 deletions, 48 insertions), matching the saved metrics. The checkpoint SHA-256 is `3a2f52a3e6a1227e34fa77d87768b04ce9ae842f66477581e216f2503e73931a`; config SHA-256 is `60e13e58019a7d76326c4af18d1abc75ab63e0b7b322d71d39497c9d6f12a4ba`. Training loss fell below 0.003 by epoch 41 while model-dev CER worsened to 40.19%, consistent with strong overfitting. Test/cross-data remained untouched.

## Controlled augmentation follow-up

To address the train/dev overfit without changing model capacity, the same shared K=4 width-320 model was retrained with the same seed, split, optimizer, batch size, and epoch budget. Mild augmentation was applied only to training images: rotation ±2°, brightness/contrast ±12%, blur with probability 0.05 and radius ≤0.6, and normalized tensor noise σ=0.02. Model-development inputs remained unaugmented.

| Run | Parameters | Best epoch | CER (%) | Exact match (%) | Exact strings | Runtime (s) | Peak VRAM (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shared K=4, width 320 / FF 640, mild train-only augmentation | 998,028 | 49 | 23.0565 | 40.1639 | 98/244 | 153.802 | 213.63 |

Independent reconstruction against the frozen 244 model-development IDs and labels exactly matched the saved summary: 261 edits across 1,132 reference characters (155 substitutions, 78 deletions, 28 insertions), with 55 wrong same-length outputs. Compared with the same-seed unaugmented capacity run, exact strings increased from 45 to 98 (+53, +21.72 percentage points) and CER fell from 39.0459% to 23.0565% (−15.99 points). The augmented run's final-epoch training loss was 0.02972 rather than below 0.003 in the unaugmented run. Best model-dev CER was at epoch 49; epoch 50 was slightly worse (23.2332%).

The improvement is substantial for this exploratory run, but 98/244 remains far below the ≥220/244 needed for 90% exact match. It is one seed on the previously exposed Pilot 007 model-development split and is not independent validation. Test and cross-data were not accessed. The run manifest's source commit field was blank; the recorded `train.py` and `loopocr.py` SHA-256 values match commit `c775c50`. Config SHA-256: `c79b45b8f0175b6c36b24840a8d1cc6c5dbf7f5deae569f4b0ee01fba4f3c25f`. Checkpoint SHA-256: `42639e92c0a090b3fbc1e6d6180c1c1b7fcef21d66a6bd9ae798f3c547b17bdb`. Predictions SHA-256: `5db15db0e178d66b3a37ce263b322c684fee202630d36f4fc089e934b39ff4a8`. Independent metric file SHA-256: `9bea3bc399f04956e8d720400f3ebce65a0d3f941f7336b368ee4df859b808ad`.

## High-resolution augmentation follow-up (48×320)

The shared K=4 width-320 model with the same seed, split, optimizer, batch size, epoch budget, and train-only augmentation was retrained with input crops increased from 32×192 to 48×320. No model parameters were added for positional capacity; max sequence length was set to 80. This was a single-seed exploratory screen on the previously exposed Pilot 007 model-development split.

| Run | Parameters | Best epoch | CER (%) | Exact match (%) | Exact strings | Runtime (s) | Peak VRAM (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shared K=4, width 320 / FF 640, mild train-only augmentation, 48×320 input | 1,003,148 | 46 | 18.0212 | 46.3115 | 113/244 | 171.287 | 400.54 |

Independent reconstruction matched all 244 frozen model-development IDs and labels: 204 edits over 1,132 reference characters (91 substitutions, 68 deletions, 45 insertions); 40 outputs had the correct length but wrong digits. The best checkpoint was selected by lowest model-development CER, with exact match as tie-break. Train loss at the best epoch was 0.01411. The config SHA-256 is `f7d7a52fdb9d91830130c4155b3c58456b649d202c5c2bf15b9f5619f74b5c33`; checkpoint SHA-256 is `d40b1f4a226c6fb1604dfec38712cfd042d4e3992158a31bb8b42ee57388c495`; predictions SHA-256 is `67210d6f0e31c12592def58eecc92a098063c9259684ca1d8532aeafb1e2e66d`. The source manifest's commit field is blank; it records `train.py` SHA-256 `91bb9e677a9e9642ec350378b89d7f1a2ddf4c1823d57136176cafbd9daf1b5c` and `loopocr.py` SHA-256 `e7644b54ddc12e64b1a4ceef532170308e6c2a0250828dedfe872fb64ae7e1bd`.

Relative to the same-seed 32×192 augmented run, 48×320 gained 15 exact strings (+6.15 percentage points) and reduced CER from 23.0565% to 18.0212% (−5.04 points). This is useful exploratory progress, not a stable or independent gain: it is one seed, and the development set has already been exposed. The ≥220/244 exact target is still unmet by a wide margin. Test/cross-data remain unopened. The run directory and independent `metrics_reconstructed.json` / `failure_cases.jsonl` are on gmoe; a Drive run-bundle copy is still pending because the local OpenVPN tunnel repeatedly resets.

## Interpretation

Shared K=4 is the best of the first seven configurations, but 18/244 exact strings is far below the >90% target of at least 220/244. K=6 is slightly worse than K=4. Untied depth-4 has over three times the parameters of shared K=4 and is also worse. The CNN controls fail to provide a useful floor. Scaling shared K=4 to 998,028 parameters raises EM to 45/244; mild train-only augmentation improves this to 98/244 and lowers CER by 15.99 points. Increasing input resolution to 48×320 raises the preliminary single-seed result to 113/244 and CER 18.0212%, while keeping parameter count near 1M. The target remains unmet. The tiny-set check and clean data audit make a basic CTC feasibility or total pipeline failure less likely, but do not rule out preprocessing, label noise, or representation problems. The remaining errors include many substitutions, deletions, and insertions, so sample-level failure review is the next evidence needed before selecting another architecture/training change.

This is a one-seed screen on an already exposed model-development split. It cannot establish a stable architecture ranking, generalization, or an OCR claim. Latency and FLOPs were not measured. No test or cross-data result was used.

## Next experiment

Before choosing a new model variant, review the 131 sample-level errors from the 48×320 run against the saved images and per-length/error categories. The independent result improved from 98/244 to 113/244 exact, but remains exploratory on the exposed development split. Compare its histories and failure modes with the 32×192 run to determine whether errors are image-resolution limited, overfit, or label/image ambiguity. Then predeclare one controlled seed-42 follow-up (e.g., stronger train-only augmentation or a higher-resolution screen) and record the hypothesis before queueing. Use the existing controller and one GPU job at a time. Preserve all failures, keep model-development images unaugmented, and continue excluding test/cross-data. Do not begin the three-seed confirmation protocol until a candidate recipe is frozen and supported by these exploratory diagnostics.

## Artifact references

- Sanity gate bundle: [Drive archive](https://drive.google.com/file/d/1ioa8r_XvFi7uD-01Qd9l2gECzUckTKEj/view)
- CNN control: [Drive archive](https://drive.google.com/file/d/1PJxP5RAauseQ6YKo8Yo8Mti0sRDWqbkL/view)
- Shared K=1: [Drive archive](https://drive.google.com/file/d/11699eMJXGgeifc4ZNVHUY_6HlGe6HsuI/view)
- Shared K=2: [Drive archive](https://drive.google.com/file/d/1JcN-SFCGovSmapn5mcYGiVEhrn4mJ02i/view)
- Shared K=4: [Drive archive](https://drive.google.com/file/d/1a1qeGz_idvFmbz5dKIIj19-YqqQfYGbr/view)
- Shared K=6: [Drive archive](https://drive.google.com/file/d/1dNkP_6K8UveilDWnlnU3mIedCn0fatrI/view)
- Untied depth-4: [Drive archive](https://drive.google.com/file/d/1YPlsDLvr_dbreUqqFuk1wg9r6EnJO6D6/view)
- CNN-wide control: [Drive archive](https://drive.google.com/file/d/1sYiMKKwNsWuDn9lmmHPv3EumXGPBsVQd/view)
- Source snapshot: [Drive archive](https://drive.google.com/file/d/1PCWhwIMlMd8xvk9zWCBQUEgFZe0nSrq8/view)
- 998k capacity follow-up: [Drive archive](https://drive.google.com/file/d/1pn4xAu6v2-jiQQbknOQ_0MBi-i4Ns48n/view)
- 998k mild-augmentation follow-up and independent reconstruction: [Drive archive](https://drive.google.com/file/d/1SbBb4IV5vgQw1Ng6AM6NQz0xXgCPoYay/view)


## Local split-size fallback (2201/244, seed 42)

Because the long-running WSL2 ssh-client had retained a stale Docker network namespace after gluetun was restarted, a separate helper container was attached to the current VPN namespace. The original ssh-client and its established SSH process were left untouched. To keep work moving, one local Windows CUDA run used the in-domain archive already extracted from Drive. The reconstructed split has 2,201 train IDs and the same 244 previously exposed Pilot 007 model-development IDs, with zero overlap, zero missing/ambiguous images, and zero invalid labels. The training path read only the physical train folder; test/cross-data were not extracted or read. Since this differs from the historical 1,467/244 split, results are not directly comparable.

| Run | Parameters | Best epoch | Exact match | CER | Edits | Runtime | Peak VRAM |
|---|---:|---:|---:|---:|---:|---:|---:|
| Local shared K=4 width320/FF640, mild augmentation, 48×320; 2,201/244 | 1,003,148 | 40 | 152/244 (62.2951%) | 133/1,132 (11.7491%) | 64 sub / 58 del / 11 ins | 696.919 s | 418,898,432 bytes |

The independent verifier matched all 244 model-development IDs and labels. There were 31 wrong strings with the correct length. Exact match by reference length was 67/103 for four digits, 83/123 for five digits, and 1/17 for six digits; the six-digit sample is small. Most frequent aligned substitutions included 1->7 (8 cases), 0->6 (4), 9->0 (4), and 1->0 (4). Two inspected examples included one visibly blurred crop and one high-contrast crop with several CTC errors; this inspection is diagnostic only and does not establish label error or causation. Best checkpoint selection followed the predeclared lowest-CER rule, not maximum exact match. Train loss reached 0.00619 by epoch 46 while dev CER plateaued around 11.75%, consistent with continued generalization error.

The run achieved 62.30% exact match, still below the 90% target (at least 220/244). It is exploratory, uses a different train count, local RTX 2050 / PyTorch 2.6.0+cu118, and the already exposed dev set. Do not describe it as independent validation. Config SHA-256 78f49938a661f0a3f10b978c5698e3cd15eca302e205a31c0c0b700ba019a9e6; checkpoint SHA-256 be5711a364e795a1c9e78fd51cba252e1f04da8d5c63944f6c547af73e9d5b8e; predictions SHA-256 68a272d6ab79830ce099226c45fd56118c6d511efba440614418dd2453578ba5; split manifest SHA-256 a6355e23ebf1d5300929784412db440858138a8295254fa7cb029c0c1be7f6f4; labels SHA-256 bd6472f8caee5728b63c6d01452a64b5c85437851ddde92442ba93ecfc3056ff. Artifact path: D:/workspace/lightocr_data/runs/loopocr-local-split2201-48x320-s42. Drive bundle: https://drive.google.com/file/d/1hOai1z3kH_76fcJPzKBjFgNH5jmgk-3q/view; checkpoint: https://drive.google.com/file/d/1sJyO6dHIz5K66L4B4KhQsWzCZrc4m88n/view.

## Next controlled follow-up

Run the same seed, 2,201/244 split, 48×320 input, shared K=4 model, optimizer, batch size, schedule, and 50-epoch budget with stronger train-only augmentation (rotation ±4°, brightness/contrast ±20%, blur probability 0.10/radius ≤1.0, Gaussian noise σ=0.04). The single changed factor is augmentation strength; model-development images remain unaugmented. The hypothesis is that stronger visual perturbations will reduce the observed train/dev generalization gap and improve the 62.30% exploratory exact-match result. If it degrades, preserve the failure and return to error/data diagnosis; do not increase model size without evidence.


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
