# Architecture hypotheses and experiment rationale

Status: seven-run architecture screen and one capacity follow-up completed on 2026-10-19. Neither meets the OCR target. See `screen_20261019_report.md` for measured results and limitations.

## Evidence boundary

- The existing Pilot 007 model-development set has been repeatedly exposed. All scores from it are exploratory and must not be described as independent validation.
- The controller and trainer accessed the fixed train/model-dev IDs only. The test and cross-data sets were not read.
- The gmoe run manifests have blank `source_commit` fields because Git metadata was unavailable inside `MLR_LinhNX`; `train.py` and `loopocr.py` hashes were checked against commit `75e2f7d` in the clean host clone.
- Each screen is seed 42. No screen result establishes reproducibility or stable improvement.
- The 16-image sanity gate showed that the training path can memorize a tiny subset. It does not demonstrate generalization.

## Current measured evidence

| Run | Parameters | Best epoch | Model-dev CER | Model-dev EM |
|---|---:|---:|---:|---:|
| CNN control | 51,276 | 20 | 67.3145% | 0.41% |
| Shared K=1 | 184,140 | 10 | 59.0989% | 1.23% |
| Shared K=2 | 184,268 | 32 | 55.8304% | 2.46% |
| Shared K=4 | 184,524 | 23 | 48.5866% | 7.38% |
| Shared K=6 | 184,780 | 21 | 50.9717% | 6.56% |
| Untied depth 4 | 581,452 | 26 | 54.0636% | 2.46% |
| CNN-wide control | 83,788 | 12 | 65.7244% | 0.00% |

K=4 is the best configuration in this one-seed screen, with 18/244 exact strings. This remains far below the target of more than 90% EM (at least 220/244). Increasing recurrence beyond four steps reduced screen performance. The untied depth-4 control used over three times as many parameters as shared K=4 and performed worse. This screen supports testing more representational capacity while keeping the best-supported shared K=4 topology fixed; it does not yet show that capacity alone is the cause.

The shared K=4 model scaled to 998,028 parameters reached 45/244 EM (18.44%) and CER 39.05% at best epoch 31. Its training loss fell below 0.003 while model-dev CER worsened after epoch 31. The capacity increase helped on this exposed development set, but substantial overfitting remains. The next controlled test keeps this model and optimizer fixed while adding mild train-only augmentation.

## Hypotheses and next test

| ID | Observation | Hypothesis | Next test | Interpretation rule |
|---|---|---|---|---|
| H0 | The tiny-set sanity run reaches 15/16 EM and all 1,711 training/model-dev samples pass the CTC feasibility audit. Shared K=4 at 998,028 parameters reaches only 45/244 EM and overfits. | The basic CTC/data path can learn; limited data and overfitting now appear to constrain generalization. | Keep the 998,028-parameter K=4 model fixed and add mild train-only augmentation. | Improvement supports augmentation as a useful data regularizer; no improvement redirects work to initialization, preprocessing, labels, and visual feature extraction. |
| H1 | Shared K=4 outperforms K=1/2/6 in the same single-seed screen. | Four recurrent refinements are a useful starting topology. | Keep K=4 fixed during the next capacity test. | Do not generalize the ranking until confirmation seeds are run. |
| H2 | Untied depth-4 has 581,452 parameters and EM 2.46%, below shared K=4 at 7.38%. | Parameter sharing and iterative refinement may be more effective per parameter than untied depth. | Preserve as an exploratory comparison; do not spend more budget on untied depth unless later error analysis motivates it. | A one-seed model-dev delta is hypothesis-generating only. |
| H3 | CNN controls remain below 1% EM. | The present depthwise-separable CNN stem alone is not a sufficient feature extractor under the current scratch training protocol. | If augmentation does not materially improve the 1M model, test a stronger or pretrained stem and a controlled label/image audit. | Keep the CTC head, split, seed, and training budget fixed when isolating the stem. |

## Confirmation gate

Do not use the existing model-dev results for independent claims. A promoted architecture requires a frozen configuration, three seeds (42, 1337, 2026), complete prediction reconstruction, and all-seed reporting. On 244 examples, >90% EM requires at least 220 exact strings per seed. Test/cross-data remain excluded from tuning and selection. If a genuinely untouched confirmation set cannot be established, label the result as a development-target result, not independent validation.
