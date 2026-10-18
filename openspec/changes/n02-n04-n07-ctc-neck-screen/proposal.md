# N02, N04 and N07 CTC neck screen

Run three user-prioritized neck comparisons on the B02 depthwise-CNN + CTC backbone family: learnable height attention pooling (N02), parallel temporal Conv1D kernels 3 and 5 (N04), and a fixed Sobel edge branch concatenated with RGB backbone features (N07). Keep the Pilot 007 train/dev split, preprocessing, seed, optimizer and training budget fixed. Run them sequentially on seed 42; results are exploratory. Never use test or cross-data for selection.

## Acceptance criteria

- N02 changes only height mean pooling to learned softmax attention, retaining kernel-3 Conv1D.
- N04 changes only the temporal neck to summed kernel-3 and kernel-5 Conv1D branches.
- N07 adds fixed Sobel magnitude features through a lightweight edge CNN branch, concatenates them with RGB features, then projects to the common 128-channel CTC sequence.
- Each run saves split/data audits, config, history, predictions, result and checkpoint hash.
- Record the approximation that N07 concatenates an independently downsampled edge branch with the CNN feature map before temporal projection.
