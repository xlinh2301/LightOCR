# Design

The stem produces features shaped `[B,C,H,T]`. For attention pooling, permute to `[B,T,H,C]`, score each row with a shared `Linear(C,1)`, softmax over `H`, and compute the weighted sum. This retains the current sequence shape `[B,T,C]` and therefore does not change CTC length or the downstream refiner/head.

The scoring layer's weight and bias are initialized to zero. At initialization all row scores are equal, so softmax is uniform and the output is the existing mean. The scoring layer then learns image-conditioned row weights from the CTC loss. This is a single-factor architecture experiment; it does not guarantee better accuracy.

The run holds seed 2026, split, 48×320 preprocessing, shared K=4 width320/FF640, strong train-only augmentation, batch32, AdamW settings, 50-epoch cap, patience10 and lowest-CER selection fixed to the prior 50-epoch seed-2026 recipe. Parameter count increases by 321 (from 1,003,148 to 1,003,469 if all other source/config details match).

The model-dev split is exposed. Report all metrics as exploratory and do not use test/cross-data data for selection.
