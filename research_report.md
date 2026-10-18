# LightOCR priority screens and A10 seed follow-up — 2026-10-18

## Scope and evidence

This report summarizes the 20-entry priority queue in `docs/research/experiment_matrix_45_user_provided.md` and the follow-up to V03. Priority screens use seed 42; the A10 follow-up includes seeds 1337 and 2026 on the same previously exposed Pilot 007 split (1,467 train / 244 model-dev), RGB 32×192, greedy CTC decoding, and dev CER with exact-match tie-break for checkpoint selection. All results are **preliminary exploratory measurements** on the exposed model-dev set; they do not support generalization, robustness, or research-novelty claims. Test and cross-data data were not read.

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
| A10 | 92,108 | 36 | 26.86% | 80/244 (32.79%) | Completed seed-42 screen; follow-up seeds vary substantially (see V03 below) |
| L03 | — | — | — | — | Deferred: stable three-seed CTC convergence gate not met |
| L04 | — | — | — | — | Deferred: stable three-seed CTC convergence gate not met |

## Interpretation

The A10 seed-42 screen achieved 80 exact matches and CER 26.86%, compared with A09's 4 exact matches and CER 63.25%. This apparent gain did not repeat: seed 1337 achieved 2/244 exact matches and CER 64.49%, while seed 2026 achieved 1/244 and CER 70.05%. Across the three predeclared seeds, mean CER is 53.80% (sample SD 23.50 percentage points) and mean exact match is 11.34% (sample SD 18.58 percentage points). The seed-42 result was used to select A10 for follow-up on the same exposed development split, so this is a repeatability screen with selection bias, not an independent confirmatory evaluation.

Stable CTC convergence was not established: two follow-up seeds were near-zero exact match and substantially worse than the selected screen. Keep L03/L04 deferred. Do not use test/cross-data to resolve this gate. Any later loss experiment needs a separately frozen protocol and a functioning baseline across seeds.

Other augmentation screens do not show a consistent benefit: A01/A02 improved CER relative to B02 in this one split, A06 did not, and A09 largely tracked A01. No ranking should be treated as confirmatory. The effects of seed, sample/source grouping, and this exposed split remain unmeasured here.

## Provenance and artifacts

- Runner: `experiments/a01_a02_a06_a09_a10_ctc_augmentation/train.py`; runner SHA-256 `49fbdfcd2b8fc463b18403fc59cc750cdd3001fe56c85b0ec3e415ee2edbb9d8`; run protocol and tasks: `openspec/changes/v03-a10-augmentation-seed-confirmation/`.
- Runner source revision: `6540e1e`; report, registry and V03 protocol are committed at `13745dd` (GitHub main).
- Seed-1337 archive/checkpoint: [artifact bundle](https://drive.google.com/file/d/1hygqiKPrrBLutTlVEt1B5FG5_gRGeQxI/view), [checkpoint](https://drive.google.com/file/d/1Foy7Oiw34KIOcdwOuRfCbyVbVzdBouiY/view); checkpoint SHA-256 `4275fbeb83ebd6b79896edffd42c1e5bb52e165691cda280b1432ae392cfc1f8`.
- Seed-2026 archive/checkpoint: [artifact bundle](https://drive.google.com/file/d/1oYYNvYtzzXtlT1brH_LVVEHZQAA1exYi/view), [checkpoint](https://drive.google.com/file/d/13Q4g75VlnyuC-FXOaNw0th1oTQErDMuh/view); checkpoint SHA-256 `0170343f6312fea07e62116dea796c0b80b3d47c444986d0f49ea1fcc494a971`.
- Run-specific artifact and checkpoint links, hashes, manifests, and output paths are recorded in the tracker `Experiments` and `Evaluations` tabs.
- N08/N09/N11 source revision: `9ecf752`; source snapshot: [LightOCR-source-9ecf752.zip](https://drive.google.com/file/d/1z8c6tWf4df7KC8rNYfYdTygQpSVSQjwM/view).
