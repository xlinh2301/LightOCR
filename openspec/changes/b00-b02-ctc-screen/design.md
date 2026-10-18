# Design: B00–B02 CTC screen

Use one runner with an explicit experiment selector so the three model variants share preprocessing, split, seed, optimizer, stopping rule, metric reconstruction, and output schema. B00 uses a conventional convolutional feature extractor followed by a bidirectional LSTM. B01 uses depthwise-separable convolution blocks and a linear CTC head after height pooling. B02 keeps the B01 backbone and adds a kernel-3 temporal Conv1D neck.

The screen uses seed 42, 50 maximum epochs, early stopping after 10 non-improving development epochs, RGB 32×192 aspect-preserving resize/right padding, batch size 32, and AdamW. Select the checkpoint using development CER with exact-match as tie-break. Train and development IDs come from the existing Pilot 007 `base_fit_fold_*.jsonl` and `model_dev.jsonl`; this is an exploratory, previously exposed split. Never read test or cross-data labels. Record parameter count, exact match, CER, same-length error rate, and edit operation counts. Runs are sequential, not concurrent.

Source is being added to the local LightOCR checkout while gmoe remains a separate uncommitted working tree. Reconcile those Git states before any source push; never overwrite remote untracked files.
