# Next architecture decision

**Current decision:** test mild training-only augmentation on the 998,028-parameter shared K=4 model.

## Evidence

- The first seven-run seed-42 screen completed with best EM 18/244 (7.38%) and CER 48.59% on shared K=4.
- Scaling the same topology to 998,028 parameters improved to 45/244 EM (18.44%) and CER 39.05% on the same previously exposed Pilot 007 model-development split.
- The 1M model's training loss dropped below 0.003, while model-development CER worsened after its best epoch (31), consistent with strong overfitting.
- Data audit and CTC feasibility passed for all 1,467 train and 244 model-development samples. The tiny-set gate reached 15/16 exact strings. These checks do not establish generalization.
- Every completed prediction set has been independently reconstructed. Test/cross-data have not been read. All run bundles are in Drive and linked in the tracker.

## Next candidate

Run `loopocr-shared-k4-width320-aug-s42` from `next_candidate_1m_aug.json`. Hold architecture, seed, split, optimizer, batch, and epoch budget fixed; apply mild rotation, brightness/contrast variation, occasional blur, and small tensor noise to training images only. Do not augment model-development images. This tests whether the observed overfitting responds to regularized visual variation.

The implementation is on branch `codex/architecture-discovery-loop`. Run the component suite locally and in `MLR_LinhNX`, then fast-forward the separate gmoe clone. Queue through the existing controller state, which has 8 completed runs and a maximum budget of 30. Use one GPU job at a time; preserve failures and do not auto-retry or terminate jobs.

If augmentation fails to improve materially, review sample-level error patterns and label/image provenance before choosing a different initialization or architecture. Continue to exclude test and cross-data from selection. Confirm any frozen candidate with seeds 42, 1337, and 2026 and report every seed. The existing Pilot 007 development split is exposed; any target result on it must be described as a development-target result, not independent validation.
