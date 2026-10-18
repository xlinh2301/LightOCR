# Next experiments

1. Keep all A01/A02/A06/A09/A10 single-seed results marked Preliminary.
2. Before L03/L04, run the predeclared A10 confirmation seeds 1337 and 2026 (seed 42 is the current screen) with the same frozen split/config; compute mean and standard deviation from all three seeds. Preserve seed 42 as a screen, not a confirmation substitute if selection choices change.
3. If the confirmation stage shows repeatable, nonblank CTC recognition, implement L03 and L04 as separate, sequential changes. Keep the other training settings and initialization fixed and document any warm start before launch.
4. If three-seed stability is not established, leave L03/L04 deferred. Do not inspect test or cross-data results to decide whether the gate is satisfied.
5. Only after all architecture/augmentation/loss choices and thresholds are frozen should an independent holdout or cross-data evaluation be authorized.

## Current gate decision

L03/L04 are deferred. A10 seed 42 provides a promising screen (CER 26.86%, exact match 80/244, best epoch 36), but one seed cannot establish stability. Clean B02 seed 42 remains weak (CER 71.38%, exact match 0/244). The three predeclared seeds are 42, 1337, and 2026.
