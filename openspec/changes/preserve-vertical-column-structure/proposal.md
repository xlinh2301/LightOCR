# Change: preserve vertical feature structure per OCR column

## Why

Run17/18 tested learned scalar attention over stem rows. Neither attention run improved over the matched mean-pooling model-dev comparator. The current pooling still reduces each column to one width-dimensional vector before the CTC Transformer. A per-column projection of the concatenated stem-row features is a controlled alternative that retains vertical glyph layout.

## What changes

- Add an explicit height_pooling: column_projection option to LoopOCR.
- For each horizontal frame, concatenate exactly two stem-row feature vectors and project the resulting 2 * width vector back to width.
- Keep mean pooling as the default and preserve existing mean/attention behavior and checkpoints.
- Run one seed42 candidate, holding the 48x320 input, shared K=4 width320/FF640, augmentation, optimizer, split, and schedule fixed against mean-pooling run11.
- Parameter budget is expected to add width * (2*width + 1) parameters (205,120 at width320), for about 1.208M total.

## Out of scope

- No data, label, vocabulary, CTC objective, optimizer, or augmentation changes.
- No test/cross-data access, checkpoint selection on test, or independent-generalization claims.
- No joint changes to Transformer depth/width or multiple GPUs.

## Acceptance criteria

- New mode returns finite [B,T,11] log probabilities for 48x320 input and leaves CTC sequence length unchanged.
- Projection weights receive finite gradients.
- Parameter-count delta matches the formula.
- Unexpected stem-row counts fail clearly rather than silently reshaping.
- Existing modes retain their behavior.
- Run only after local tests pass, clean remote checkout is fast-forwarded, and controller/GPU state is verified.
- Reconstruct and retain all 244 exposed model-dev predictions; mark results exploratory.
