## 1. Evidence audit

- [x] 1.1 Reconcile remote repo/data/run state and existing results before any training; preserve original untracked remote tree and clone the research branch separately.
- [ ] 1.2 Record CTC correctness, train/dev split provenance, and A10 instability diagnostics.
- [x] 1.3 Verify primary architecture papers and record OCR transfer limitations.

## 2. LoopOCR-v1 and controls

- [x] 2.1 Implement the lightweight CNN stem and shared recurrent Transformer CTC model.
- [x] 2.2 Add CNN-only, untied-depth, and parameter-matched control variants.
- [x] 2.3 Add deterministic unit tests for tensor shape, width lengths, CTC feasibility, repeated digits, and finite gradients.

## 3. Durable execution

- [x] 3.1 Implement atomic campaign state, config/source/data hashes, stable run IDs, and JSONL event history.
- [x] 3.2 Implement sequential launch and process/artifact reconciliation; never overwrite, auto-retry, or auto-kill.
- [x] 3.3 Add prediction reconstruction, metrics, run manifests, and failure-case exports.

## 4. Experiments and reporting

- [x] 4.1.1 Implement both-split CTC feasibility checks and deterministic train-only tiny-set memorization runner.
- [ ] 4.1.2 Execute the sanity/memorization gate in `MLR_LinhNX`, persist evidence, and open the controller gate only if passed.
- [ ] 4.2 Run first-family comparisons sequentially on `MLR_LinhNX` with a predeclared screening budget.
- [ ] 4.3 Reconstruct dev metrics from saved predictions and publish comparison/pareto/error tables.
- [ ] 4.4 Promote only by predeclared criteria; run 3 seeds only after freezing the candidate.
- [ ] 4.5 Reconcile each run to the Sheet and Drive; archive a research checkpoint and final status.
