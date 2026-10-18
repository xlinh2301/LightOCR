# Architecture hypotheses and experiment rationale

Status: initial hypotheses; pending remote artifact and dataset audit.

## Current evidence

- The existing A10 seed follow-up on exposed Pilot 007 model-dev produced 80/244 EM for selected screen seed 42, 2/244 for seed 1337, and 1/244 for seed 2026. The mean EM is 11.34% (sample SD 18.58 percentage points); this is not stable evidence.
- Existing CNN/CTC and neck screens mostly achieved 0–3.28% EM on the same split. The report indicates a clean B02 baseline at 0/244.
- The published project report and A10 registry are local evidence. Before any new run, reconcile them with gmoe manifests, source revisions, process state, and data hashes.

## Hypotheses

| ID | Observed issue | Hypothesis | Minimal test | Interpretation rule |
|---|---|---|---|---|
| H0 | Low/unstable EM across CTC architectures | A pipeline/objective defect or CTC length/decoding inconsistency may dominate model differences. | Audit vocabulary, blank, `[B,T,C]`/CTC layout, width lengths, repeated-target feasibility, gradient and collapse tests; then a fixed tiny-set memorization check. | Do not screen architectures until correctness tests pass. If tiny-set learning fails, fix and document the cause before continuing. |
| H1 | Scratch CNNs underperform a pretrained TinyNeXt result reported in the handover. | Initialization/feature quality is a major factor, not merely the neck. | Reconstruct strongest baseline with its exact source, data and preprocessing; compare to a same-split scratch control. | If the control does not reproduce, stop interpreting architecture deltas. |
| H2 | Feature sequences may represent local digit ambiguity but cannot revise tokens globally. | A small sequence attention transition can improve character disambiguation. | CNN-only vs shared Transformer K=1 under the same training budget. | Require prediction-level error changes, not only loss changes. |
| H3 | Repeated use of one transition can refine uncertain digit positions efficiently. | Shared recurrent depth improves EM versus K=1 at modest parameter growth. | Shared K=2/4/6 and untied K=4 with matched executed depth. | Later loops should correct some earlier errors; if they merely amplify errors or do not help at matched compute, reject the recurrence claim. |
| H4 | A recurrent gain could be capacity rather than recurrence. | More channels alone explain improvement. | CNN-only width 192 control and report parameters/FLOPs/latency. | Do not attribute a gain to recurrence unless it beats an appropriate capacity/compute control. |

## Confirmation gate

The first seven configurations are single-seed model-development screens, not confirmatory evidence. Promote at most one frozen candidate only after sanity tests, complete prediction reconstruction, error analysis, and comparison with the relevant controls. Confirmation uses seeds 42, 1337, and 2026 without per-seed changes. The project target is strictly more than 90% EM on each seed and on the mean; on the existing 244-example split this means at least 220 exact strings per seed. Because the development split has already been reused, label any result there `development-target achieved`, not independent validation.
