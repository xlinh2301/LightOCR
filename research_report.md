# LightOCR priority screen — 2026-10-18

## Scope and evidence

This report summarizes the 20-entry priority queue in `docs/research/experiment_matrix_45_user_provided.md`. Screens use seed 42 and the previously exposed Pilot 007 split (1,467 train / 244 model-dev), RGB 32×192, greedy CTC decoding, and dev CER with exact-match tie-break for checkpoint selection. Results are **preliminary, single-seed exploratory measurements** on the exposed model-dev set; they do not support generalization, robustness, or research-novelty claims. Test and cross-data data were not read for these runs.

The experiment tracker is the authoritative row-level registry: [LightOCR Experiment Tracker](https://docs.google.com/spreadsheets/d/1AKPO5ShSrpTZHIKB_-FIsTlURNehGYYtu2bzNRyNwDo/edit). Every run's manifest, history, predictions, result, checkpoint and data audit are retained under its gmoe artifact path and backed up in Drive where a Drive link is recorded there.

## Priority queue results

| Queue item | Params | Best epoch | Dev CER | Exact match | Status / note |
|---|---:|---:|---:|---:|---|
| B00 | 872,043 | 26 | 49.20% | 8/244 (3.28%) | Completed; retry03 |
| B01 | 42,828 | 14 | 69.08% | 0/244 | Completed; retry02 |
| B02 | 92,108 | 11 | 71.38% | 0/244 | Completed; retry02; clean CTC baseline did not converge to useful dev recognition |
| B03 | 117,324 | 19 | 70.67% | 0/244 | Completed |
| I02 | — | — | — | — | Covered by B01 (same RGB 32×192 reference configuration); no duplicate run |
| I03 | 42,828 | 20 | 70.41% | 0/244 | Completed; RGB 32×256 |
| I05 | 42,742 | 17 | 64.84% | 2/244 (0.82%) | Completed; grayscale |
| N02 | 92,237 | 12 | 70.76% | 0/244 | Corrected run completed; initial layout failure retained |
| N04 | 174,156 | 14 | 67.23% | 0/244 | Corrected run completed; initial layout failure retained |
| N07 | 117,847 | 16 | 65.37% | 3/244 (1.23%) | Completed; Sobel concatenation |
| N08 | 134,359 | 18 | 72.35% | 0/244 | Completed; Sobel gated fusion |
| N09 | 134,413 | 12 | 70.67% | 1/244 (0.41%) | Completed; learned structural gated fusion |
| N11 | 141,452 | 15 | 68.37% | 0/244 | Completed; wider temporal control, near but not exact parameter match |
| A01 | 92,108 | 29 | 63.25% | 0/244 | Completed; brightness/contrast |
| A02 | 92,108 | 13 | 64.58% | 3/244 (1.23%) | Completed; Gaussian blur |
| A06 | 92,108 | 10 | 70.67% | 0/244 | Completed; synthetic glare |
| A09 | 92,108 | 26 | 63.25% | 4/244 (1.64%) | Completed; combined degradation |
| A10 | 92,108 | 36 | 26.86% | 80/244 (32.79%) | Completed; A09 plus glare; strongest screen result, requires independent confirmation |
| L03 | — | — | — | — | Deferred: stable three-seed CTC convergence gate not met |
| L04 | — | — | — | — | Deferred: stable three-seed CTC convergence gate not met |

## Interpretation

The clearest observation is the A10 single-seed result (80 exact matches and CER 26.86% on model-dev) compared with A09 (4 exact matches and CER 63.25%). A10's training was numerically finite, produced nonblank outputs, and early-stopped after ten epochs without improving beyond epoch 36. This is evidence that the model can learn CTC alignments under the A10 training distribution; it is not evidence that the improvement is stable across seeds or datasets.

L03/L04 remain gated. The clean B02 reference screen achieved CER 71.38% with zero exact matches, and A10 has only one screening seed. The protocol's confirmation seeds (42, 1337, 2026) have not been run for A10. Therefore the campaign has not established stable CTC performance across seeds. Do not use test/cross-data to resolve this gate. Resume L03/L04 only after an authorized, predeclared confirmation stage establishes repeatable nonblank CTC performance.

Other augmentation screens do not show a consistent benefit: A01/A02 improved CER relative to B02 in this one split, A06 did not, and A09 largely tracked A01. No ranking should be treated as confirmatory. The effects of seed, sample/source grouping, and this exposed split remain unmeasured here.

## Provenance and artifacts

- Runner and OpenSpec: `experiments/a01_a02_a06_a09_a10_ctc_augmentation/train.py`, `openspec/changes/a01-a02-a06-a09-a10-ctc-augmentation-screen/`.
- Source revision: `6540e1e` (GitHub main); source snapshot: [LightOCR-source-6540e1e.zip](https://drive.google.com/file/d/1MUBBF0pJ8dJM6Pp-rDotWzZb_j31FEzV/view).
- Run-specific artifact and checkpoint links, hashes, manifests, and output paths are recorded in the tracker `Experiments` and `Evaluations` tabs.
- N08/N09/N11 source revision: `9ecf752`; source snapshot: [LightOCR-source-9ecf752.zip](https://drive.google.com/file/d/1z8c6tWf4df7KC8rNYfYdTygQpSVSQjwM/view).
