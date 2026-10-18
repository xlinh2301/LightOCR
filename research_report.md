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


## Local split-size fallback (2201/244, seed 42)

Because the long-running WSL2 ssh-client had retained a stale Docker network namespace after gluetun was restarted, a separate helper container was attached to the current VPN namespace. The original ssh-client and its established SSH process were left untouched. To keep work moving, one local Windows CUDA run used the in-domain archive already extracted from Drive. The reconstructed split has 2,201 train IDs and the same 244 previously exposed Pilot 007 model-development IDs, with zero overlap, zero missing/ambiguous images, and zero invalid labels. The training path read only the physical train folder; test/cross-data were not extracted or read. Since this differs from the historical 1,467/244 split, results are not directly comparable.

| Run | Parameters | Best epoch | Exact match | CER | Edits | Runtime | Peak VRAM |
|---|---:|---:|---:|---:|---:|---:|---:|
| Local shared K=4 width320/FF640, mild augmentation, 48×320; 2,201/244 | 1,003,148 | 40 | 152/244 (62.2951%) | 133/1,132 (11.7491%) | 64 sub / 58 del / 11 ins | 696.919 s | 418,898,432 bytes |

The independent verifier matched all 244 model-development IDs and labels. There were 31 wrong strings with the correct length. Exact match by reference length was 67/103 for four digits, 83/123 for five digits, and 1/17 for six digits; the six-digit sample is small. Most frequent aligned substitutions included 1->7 (8 cases), 0->6 (4), 9->0 (4), and 1->0 (4). Two inspected examples included one visibly blurred crop and one high-contrast crop with several CTC errors; this inspection is diagnostic only and does not establish label error or causation. Best checkpoint selection followed the predeclared lowest-CER rule, not maximum exact match. Train loss reached 0.00619 by epoch 46 while dev CER plateaued around 11.75%, consistent with continued generalization error.

The run achieved 62.30% exact match, still below the 90% target (at least 220/244). It is exploratory, uses a different train count, local RTX 2050 / PyTorch 2.6.0+cu118, and the already exposed dev set. Do not describe it as independent validation. Config SHA-256 78f49938a661f0a3f10b978c5698e3cd15eca302e205a31c0c0b700ba019a9e6; checkpoint SHA-256 be5711a364e795a1c9e78fd51cba252e1f04da8d5c63944f6c547af73e9d5b8e; predictions SHA-256 68a272d6ab79830ce099226c45fd56118c6d511efba440614418dd2453578ba5; split manifest SHA-256 a6355e23ebf1d5300929784412db440858138a8295254fa7cb029c0c1be7f6f4; labels SHA-256 bd6472f8caee5728b63c6d01452a64b5c85437851ddde92442ba93ecfc3056ff. Artifact path: D:/workspace/lightocr_data/runs/loopocr-local-split2201-48x320-s42. Drive bundle: https://drive.google.com/file/d/1hOai1z3kH_76fcJPzKBjFgNH5jmgk-3q/view; checkpoint: https://drive.google.com/file/d/1sJyO6dHIz5K66L4B4KhQsWzCZrc4m88n/view.

## Controlled stronger-augmentation follow-up

The stronger train-only augmentation run used the same seed, 2,201/244 split, 48×320 input, shared K=4 model, optimizer, batch size, schedule, and stopping rule. Augmentation was rotation ±4°, brightness/contrast ±20%, blur probability 0.10/radius ≤1.0, and Gaussian noise σ=0.04. It completed 44 epochs; best epoch34. Independent reconstruction matched all 244 IDs and labels: 167/244 exact (68.4426%), CER 108/1,132=9.5406%, with 46 substitutions, 49 deletions, 13 insertions, and 23 wrong same-length strings. Compared with the local mild-augmentation run on the same exposed dev split and seed, exact match increased from 62.2951% to 68.4426% (+15 samples; +6.15 percentage points), and CER declined from 11.7491% to 9.5406% (−2.21 percentage points). This paired comparison is exploratory and does not validate generalization. The result remains 21.56 percentage points below the 90% target. Six-character references account for 19 of 108 edits, but the subgroup contains only 17 samples and should not be overinterpreted.

The run used 1,003,148 parameters, runtime 884.849 s, peak VRAM 419,947,008 bytes on a Quadro RTX 5000. Its audit retained all 2,201 train and 244 model-dev IDs, found zero overlap, zero missing or ambiguous IDs and zero CTC-infeasible rows; no test or cross-data data were read. The previously exposed model-dev split and exploratory reconstructed train split preclude confirmatory claims. Manifest source commit was blank; post-run inspection verified the clean clone at `aedd852` and matched trainer/model file hashes recorded in the manifest. Resolved config SHA-256 `b2436497837c8d58d70eb4c64a7b468db4a76812ab972d43cc6b471eea7b5956`; checkpoint SHA-256 `4703a1d3f23723f1151c84b8d869554955afa05323902b12a9e17999495b097a`; predictions SHA-256 `922f20497436480ea93c4fe631ceeb25f629a93621bc20cda778fbb3d122c5a7`. Run bundle: https://drive.google.com/file/d/1tUn6hXZdb_LzmasPVjtKhSfPrpN6OYD1/view; report: https://drive.google.com/file/d/1GsTpKVf0UejxxXnzzxsQL0B3EgDhiVOg/view; checkpoint: https://drive.google.com/file/d/1S79U10HUqE6VDRjcj1r_05G5YWfIpgns/view.

## Next one-factor screen

Increase input height from 48 to 64 pixels while holding width320, shared K=4/width320/FF640, seed42, strong augmentation, split, optimizer, batch size, 50-epoch maximum, and patience fixed. The hypothesis is that retaining more vertical image detail reduces substitutions/deletions without changing the model's parameter count. Use this only as an exploratory model-dev screen; do not freeze a recipe or access test/cross-data from this exposed development set.
