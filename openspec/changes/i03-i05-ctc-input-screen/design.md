# Design: I03–I05 input screen

Use the B01 depthwise-separable CNN with a linear CTC head for both variants. I03 retains RGB/ImageNet normalization and aspect-preserving resize with right padding, changing the maximum width to 256. I05 retains 32×192 geometry but converts each crop to one luminance channel and normalizes it by `(x - 0.5) / 0.5`. The width stride remains four, and CTC input lengths are computed from the unpadded resized width.

Both runs use seed 42, 50 maximum epochs, patience 10, batch size 32, the frozen Pilot 007 train/dev IDs, and dev-only checkpoint selection by CER with exact-match tie-break. No test or cross-data paths are searched.
