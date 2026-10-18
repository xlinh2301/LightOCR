# Next architecture decision

**Current decision:** test higher input resolution on the 998,028-parameter shared K=4 model with mild train-only augmentation.

## Evidence

- The first seven-run seed-42 screen completed with best EM 18/244 (7.38%) and CER 48.59% on shared K=4.
- Scaling the same topology to 998,028 parameters improved to 45/244 EM (18.44%) and CER 39.05% on the same previously exposed Pilot 007 model-development split.
- The 1M model's training loss dropped below 0.003, while model-development CER worsened after its best epoch (31), consistent with strong overfitting.
- Mild train-only augmentation on the same architecture/protocol increased seed-42 model-dev exact strings from 45/244 to 98/244 (+21.72 percentage points) and reduced CER from 39.0459% to 23.0565% (−15.99 points). The augmented run's final training loss was 0.02972, and its best model-dev CER occurred at epoch 49.
- Independent reconstruction matched all 244 IDs and labels: 261 edits over 1,132 characters (155 substitutions, 78 deletions, 28 insertions); 55 outputs have the correct length but wrong digits.
- The 98/244 result remains far below the ≥220/244 needed for 90% exact match. It is exploratory evidence from the previously exposed model-development split, not independent validation.
- Data audit and CTC feasibility passed for all 1,467 train and 244 model-development samples. The tiny-set gate reached 15/16 exact strings. These checks do not establish generalization.
- Every completed prediction set has been independently reconstructed. Test/cross-data have not been read. All run bundles are in Drive and linked in the tracker.

## Next candidate

Run a 48×320 input-resolution follow-up on shared K=4 width320/FF640 with seed42 and the same split, optimizer, batch, epoch budget, and mild train-only augmentation. Only input height/width and positional capacity should change; keep parameters near 1M. This tests whether higher-resolution visual evidence reduces the remaining substitution-heavy errors. Do not augment model-development images.

The implementation is on branch `codex/architecture-discovery-loop`. Add configurable input dimensions with defaults preserving the 32×192 baseline; test 48×320 and ensure the model position capacity and CTC widths agree. Run the component suite locally and in `MLR_LinhNX`, then fast-forward the separate gmoe clone. Queue through the existing controller state, which has 9 completed runs and a maximum budget of 30. Use one GPU job at a time; preserve failures and do not auto-retry or terminate jobs.

If higher resolution fails to improve materially, inspect sample-level failures and image/label provenance before choosing another change. Continue to exclude test and cross-data from selection. Confirm any frozen candidate with seeds 42, 1337, and 2026 and report every seed. The existing Pilot 007 development split is exposed; any target result on it must be described as a development-target result, not independent validation.
