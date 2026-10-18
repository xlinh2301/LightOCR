# I03–I05 CTC input screen

Compare the reference RGB 32×192 setup already represented by B01 with I03 RGB 32×256 and I05 grayscale 32×192, keeping the B01 depthwise-CNN + CTC architecture and all training/split settings fixed. Run the two distinct configurations sequentially on seed 42. The Pilot 007 model-dev split is already exposed, so results remain exploratory. Test and cross-data data stay sealed.

## Acceptance criteria

- I03 changes only the maximum input width from 192 to 256.
- I05 changes only the input color representation to grayscale at 32×192.
- Both preserve frozen train/dev membership, CTC feasibility checks and the shared artifact schema.
- I02 is recorded as covered by B01, which already uses the reference RGB 32×192 input.
