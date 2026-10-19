# Change: learned vertical pooling for LoopOCR

## Why

The strongest current in-domain screen uses a 48×320 image input, shared K=4 Transformer refinement and train-only strong augmentation. The mean-height-pooling model has about 1.003M parameters and remains far below the >90% exact-match objective. Raising input height to 64 did not improve exact match, while the seed-2026 100-epoch follow-up stopped at epoch 37 and did not improve selected CER. Run16 errors include many deletions (45) and substitutions (54), so fixed uniform averaging across feature rows is a specific, testable representation bottleneck.

## What changes

- Add an optional, parameter-light learned attention distribution over vertical feature rows for each horizontal frame.
- Initialize its scoring layer to zero so the attention pooling starts exactly as uniform mean pooling.
- Keep mean pooling as the default and preserve all existing model behavior unless the config explicitly selects `height_pooling: attention`.
- Run one controlled seed-2026 candidate with the same 48×320 strongaug recipe and 50-epoch budget, changing only vertical pooling.
- Record the result as exploratory because the model-development IDs have been exposed.

## Out of scope

- No input-size, stem, Transformer, optimizer, augmentation, split, or checkpoint-selection changes.
- No test/cross-data access or claims of independent validation.
- No simultaneous architecture changes or multi-GPU training.

## Acceptance criteria

- Both pooling modes return finite `[B,T,11]` log probabilities and keep CTC sequence lengths unchanged.
- Zero-initialized attention pooling matches mean pooling within numerical tolerance before training.
- The learned scoring layer receives finite gradients and adds only `width + 1` parameters.
- Existing defaults and CNN-only/mean-pooling baselines remain compatible.
- The candidate is queued through the existing sequential controller only after the remote repo state, controller status, and GPU-idle state are verified.
- Reconstruct all 244 development predictions and preserve the complete run evidence. Do not inspect test/cross-data.
