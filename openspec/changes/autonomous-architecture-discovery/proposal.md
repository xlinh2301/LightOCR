# Change: Autonomous architecture discovery for LightOCR

## Why

The existing exploratory OCR runs have not established stable CTC convergence. A10's three seeds have mean model-development exact match 11.34% with 18.58 percentage-point sample standard deviation. Repeating the former fixed architecture queue or selecting its best seed would not resolve this instability.

## What changes

- Add a restartable, stateful experiment controller that records hypotheses, immutable run identities, command lines, process state, outcomes, and next decisions.
- Add LoopOCR-v1: a lightweight CNN image stem, height-to-sequence projection, weight-tied Transformer refinement, and CTC head.
- Add controlled first-family comparisons: CNN-only, one Transformer block, shared recurrence at 2/4/6 loops, untied depth-4 control, and a parameter-matched wider control.
- Preserve all prior artifacts and keep model-development results exploratory. Do not access test/cross-data for selection.
- Run diagnostic tests before screening, then run GPU work sequentially in `MLR_LinhNX`.

## Out of scope

- Any change to EditCTC.
- Any claim of independent generalization from the exposed model-development split.
- Automatic hyperparameter search without a recorded hypothesis and bounded budget.
- Automatic process killing or retrying failed runs.

## Success measures

- CTC encoding/length/decoding audit and model-shape tests pass.
- LoopOCR variants produce valid `[B,T,11]` log probabilities and satisfy CTC length constraints.
- Controller safely resumes/reconciles runs, rejects duplicate IDs/config hashes, and retains failed jobs.
- Initial comparison artifacts contain measured parameters, runtime, memory, predictions, EM, CER, and a written decision.

## Constraints

- Target approximately 1M parameters; larger controls are allowed and must be labelled.
- Use the existing fixed train/model-development split only after verifying its hashes and provenance.
- Keep one GPU-intensive job active at a time.
- Freeze a candidate before three-seed confirmation; do not discard failed seeds.
