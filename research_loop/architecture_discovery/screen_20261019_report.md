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
