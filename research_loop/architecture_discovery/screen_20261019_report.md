# LoopOCR-v1 first architecture screen

**Date:** 2026-10-19  
**Source:** `codex/architecture-discovery-loop` @ `21a442c`  
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

## Interpretation

Shared K=4 is the best observed configuration, but 18/244 exact strings is far below the >90% target of at least 220/244. K=6 is slightly worse than K=4. Untied depth-4 has over three times the parameters of shared K=4 and is also worse. The CNN controls fail to provide a useful floor. The tiny-set check and clean data audit make a basic CTC feasibility or total pipeline failure less likely, but do not rule out preprocessing, optimization, label noise, or representation problems.

This is a one-seed screen on an already exposed model-development split. It cannot establish a stable architecture ranking, generalization, or an OCR claim. Latency and FLOPs were not measured. No test or cross-data result was used.

## Next experiment

Run `loopocr-shared-k4-width320-s42` with the same split, preprocessing, optimizer, batch, seed, and epoch budget. Set width 320, 4 attention heads, FF width 640, shared K=4, and iteration conditioning. The model has 998,028 trainable parameters by local code count. This isolates capacity scaling within the best-performing topology and brings the model to the approximately 1M target. The candidate config is `next_candidate_1m.json`. Keep the existing controller and single-GPU sequential execution; stop for review on any failed/interrupted run.

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
