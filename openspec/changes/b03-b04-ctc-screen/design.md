# Design: B03–B04 CTC screen

Extend the shared runner so the four existing architecture choices retain their behavior. B03 uses the B01 depthwise CNN followed by a one-layer bidirectional GRU with 64 hidden units per direction. B04 uses standard 3×3 convolutions with the same channel progression and stride schedule as B01, followed by height mean pooling and a linear CTC head. All other settings remain fixed for the screen.

This is a single-seed exploratory comparison on the already exposed Pilot 007 split. The checkpoint is selected only on model-dev CER, with exact-match tie-break. Run B03 then B04, not concurrently, to preserve the ordered queue and isolate failures. The input-length and CTC-feasibility audits remain mandatory. B05's fixed-position classifier does not apply because training labels have variable lengths (3–6); its stated variable-length fallback duplicates B00's one-layer BiLSTM model and is therefore not a distinct experiment.
