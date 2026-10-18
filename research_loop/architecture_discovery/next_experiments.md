
## LightOCR-1M LoopOCR follow-up (2026-10-19)

- A separate local split (2,201 train / 244 previously exposed model-dev) allowed one 48×320 K4 seed-42 run after a stale Docker network namespace blocked SSH. It reached 152/244 exact (62.30%) and 11.75% CER at best epoch 40. It is exploratory and not comparable to remote 1,467/244 results.
- The failure analysis found a very weak small sample for six-digit strings (1/17 exact), 58 deletions, and 64 substitutions. The inspected examples suggest both blur and high-contrast failure cases; no causal claim is established.
- Next controlled screen: same split, model, seed, resolution, optimizer, schedule and epoch budget; change only train-only augmentation to rotation ±4°, brightness/contrast ±20%, blur p=0.10/radius≤1.0 and Gaussian noise σ=0.04. Use only the exposed model-dev split for exploratory selection; do not touch test/cross-data.
- gmoe access failure was traced to ssh-client staying attached to a stale network namespace after gluetun restart. A separate ssh-client-repaired helper now reaches gmoe intermittently; the original active SSH process was preserved. The remote controller remains 10/30 runs complete.
