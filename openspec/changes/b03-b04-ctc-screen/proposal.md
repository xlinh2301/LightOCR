# B03–B04 CTC architecture screen

Continue the architecture screen with B03 (depthwise CNN + BiGRU + CTC) and B04 (standard CNN + CTC). Keep the Pilot 007 train/model-dev IDs, RGB 32×192 preprocessing, vocabulary, optimizer, seed 42, early stopping, and artifact schema matched to B00–B02. Run sequentially and keep test/cross-data sealed. Mark results exploratory because model-dev was previously exposed.

## Acceptance criteria

- B03 adds only a one-layer bidirectional GRU neck to the depthwise CNN backbone.
- B04 replaces depthwise-separable convolutions with standard convolutions while retaining height pooling and the CTC head.
- Both variants save config, split manifest, data audit, history, model-dev predictions, terminal metrics and checkpoint hash.
- No test or cross-data files are read.
- B05 is not run in this change: target lengths are variable (3–6), and its prescribed fallback is the same one-layer CNN+BiLSTM already represented by B00.
