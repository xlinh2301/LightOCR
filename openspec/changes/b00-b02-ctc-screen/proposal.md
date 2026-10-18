# B00–B02 CTC architecture screen

Run the user-prioritized B00, B01, and B02 architectures sequentially with the same exploratory Pilot 007 train/model-dev split, RGB 32×192 preprocessing, CTC vocabulary, seed 42, and fixed training schedule. Do not load or evaluate test or cross-data data. Treat outputs as exploratory because this split has prior experimental exposure.

## Acceptance criteria

- B00 is a conventional CNN + BiLSTM + CTC recognizer.
- B01 is a depthwise separable CNN + CTC recognizer.
- B02 uses the B01 depthwise backbone with a Conv1D temporal neck + CTC.
- Each run saves config, split manifest, epoch history, model-dev predictions and metrics, checkpoint hash, and terminal status.
- CTC feasibility is audited before training; invalid examples are reported and cause a visible failure rather than being dropped.
- The runs execute one after another and never access test or cross-data labels.
