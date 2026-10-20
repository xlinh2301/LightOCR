# LightOCR project instructions

## Project scope

- This repository is the LightOCR research project. Phase 1 studies lightweight vision architectures (2024–2026); Phase 2 studies general text recognition. The model target is about 1M parameters; larger models are allowed as clearly labelled comparators.
- Use Codex agents for literature synthesis. OpenScholar LLM generation or training is out of scope; retrieval may be used. Verify research claims against primary sources, record provenance, retain negative results, and separate exploratory from confirmatory evidence.
- Use OpenSpec for implementation changes. Keep secrets, `.env`, local databases, restricted data, datasets, checkpoints, and generated artifacts out of Git unless a task explicitly requires otherwise.

## Default OCR experiment workflow

- When the user requests experiments for the cropped numeric-display OCR study, use `docs/research/experiment_matrix_45_user_provided.md` as the default hypothesis and priority matrix and `docs/research/experiment_reporting_contract_user_provided.md` as the required reporting contract. Apply these again for each new experiment task unless the user changes the scope. The 45 entries are a staged research plan, not a requirement to launch all runs at once.
- Before launching runs, inspect the active session/jobs, repository instructions and Git state on `gmoe`; preserve running work and existing outputs. The remote research source is `workdir_Research/source/LightOCR-1M` on `gmoe`, reached through WSL2 Ubuntu → `docker exec ssh-client` → SSH. Do not confuse this repository with EditCTC.
- Freeze and record the dataset version, device/source or near-duplicate grouped splits, preprocessing, vocabulary, decoder, training budget, seed, config and selection metric before comparing a family. Use development data for selection; keep frozen external/holdout data out of tuning and rankings. Never silently drop samples with invalid CTC lengths; report them and the handling decision.
- Return text as strings so leading zeros are preserved. For digit CTC use 10 digits plus blank and logits `[B,T,11]`; check the CTC feasibility condition `T >= L + R`, where `R` is the count of adjacent repeated target pairs.
- Use staged evaluation: first verify a functioning baseline (including non-blank predictions), then screen candidates with a predeclared reduced step budget, then fully train selected candidates. Do not compare under-trained screening checkpoints as confirmatory results. Screening may use seed 42; use seeds 42, 1337 and 2026 for the predeclared confirmation runs unless the user changes this protocol.
- For numeric-display OCR, prioritize B00–B03 baselines, I02–I05 input studies, N07–N09 structural necks with N11 matched-capacity control, then A06–A10 robustness studies. Run L03/L04 only after stable CTC convergence. The matrix’s priority is a hypothesis, not evidence that a method works.
- Report exact-match accuracy as primary, with CER, wrong-but-same-length rate, insertion/deletion rates, repeated-character cases, parameter count, FLOPs and measured latency. Keep sample-level development predictions and classify correct, same-length substitution, deletion, insertion and repeated-character errors; for mixed cases retain the full edit-operation counts.
- Every run must preserve resolved config, command, seed, split/config hashes, source revision and dirty state, checkpoint provenance/hash, hardware, runtime, best step, total steps, training history, metrics, predictions and failures. Never invent missing measurements. Use grouped bootstrap confidence intervals when samples share a device/source.
- Produce and update the run registry and comparison tables, error/robustness analyses, plots, `research_report.md` and `next_experiments.md` (or the task’s agreed equivalent). Separate observed results, hypotheses and confirmed conclusions. A single-seed screen is not evidence of stable improvement. For a selected neck and augmentation, use the matrix’s 2×2 factorial ablation and report the interaction separately from whether the combined model is best.

## Google Sheets and Drive record

- Record every completed or failed run in the existing `LightOCR Experiment Tracker` sheet: <https://docs.google.com/spreadsheets/d/1AKPO5ShSrpTZHIKB_-FIsTlURNehGYYtu2bzNRyNwDo/edit>. Keep the run ID, source revision, config/split identity, seeds, metrics, checkpoint and artifact locations in sync with the `Experiments` and `Evaluations` tabs. Update results as part of the experiment task, not as a later optional step.
- **Required run finalization:** before reporting an experiment task complete, reconcile the Sheet against the run manifests, training histories, saved predictions, evaluation outputs, and artifact directory. For each finished seed/run, update its `Experiments` and `Evaluations` rows with the actual terminal status, completion date, selected/best step, metrics, checkpoint hash, and artifact/Drive links that exist. Mark failed, interrupted, or invalid runs accurately and link their logs; never leave a finished run marked `Running`/`Planned`, and never fill missing values with estimates. For multi-seed campaigns, update the tracker incrementally as each seed finishes, then do a final reconciliation and record aggregate statistics only when all included runs have completed. If Sheets access is temporarily unavailable, preserve a ready-to-apply update locally, report the sync failure, and do not claim the tracker was updated.
- Google Drive project folder: `research/LightOCR` (`15WSD9IIR1ZLYg6OYKapDvTJqSydaDmPq`). Store source snapshots in `source-code` (`16EEN7wlyD2IL0YhfCoJdiRxlnUF36H6r`), model weights in `checkpoints` (`126H_DQHB_dkC4vZHjNc-RkM48PLfz_af`), and reports/predictions/configs in `experiment-artifacts` (`1f_yCFjyXoS5YP3I00rAS5GbIBZSqKv0s`). Use versioned names containing the Git commit or run ID; do not replace prior backups.
- When code changes, commit and push the relevant project changes to `https://github.com/xlinh2301/LightOCR.git`, then upload a versioned source snapshot to Drive. When a task produces checkpoints or experiment outputs, upload those to their corresponding Drive folders and put the Drive locations in the sheet/report. Never upload `.env`, credentials, restricted data, or unrelated local files.

## GitHub initialization and sync

- The Git root is the LightOCR project root, currently `C:\Users\USER\Documents\ChatGPT\LightOCR-1M` locally and `workdir_Research/source/LightOCR-1M` on `gmoe`. Run Git commands only after confirming the current directory and repository. Never initialize, stage, commit, or push from the EditCTC handoff checkout.
- The user-provided first-push sequence for an empty repository is:

  ```sh
  echo "# LightOCR" >> README.md
  git init
  git add README.md
  git commit -m "first commit"
  git branch -M main
  git remote add origin https://github.com/xlinh2301/LightOCR.git
  git push -u origin main
  ```

- Apply that sequence only when the project has no Git history and no `origin`. For an already initialized project, do not repeat `git init`, append duplicate README headers, or add a second remote. Preserve history and user changes; inspect remote state before pushing, and never force-push or overwrite remote commits. Include the applicable `AGENTS.md`, code, specs and research documentation in project commits, but exclude ignored secrets/data/artifacts.
- The supplied Google Workspace CLI (`gws`) is the Drive upload path. For source backup, create a ZIP from the committed Git tree (`git archive`) and upload it with `gws drive files create` to the `source-code` folder. For checkpoint/report backups, upload only the task’s explicit outputs to their designated folders. Confirm upload success and record the returned Drive file ID/link.

## Remote setup and task hygiene

- On `gmoe`, follow the repository’s active `AGENTS.md`, `EXPERIMENT_PROTOCOL.md`, OpenSpec and run-specific instructions. Inspect Git status and active sessions before edits or experiments; preserve untracked work and never overwrite prior results.
- Keep exploratory work separate from the frozen confirmatory holdout. Do not claim OCR effectiveness or a research contribution without controlled quantitative evidence.

## Research discussion and independent review

- For consequential research decisions—such as experiment priorities, explanations of results, changes to the data protocol, or claims in a report—use two independent Codex sub-agents when available. Ask one to propose a falsifiable, evidence-backed option and another to act as a skeptical reviewer of assumptions, alternatives, confounds, leakage, and whether the experiment can distinguish competing explanations. Have them make an initial assessment independently, then exchange concise critiques. Add an evidence auditor when the decision depends on data provenance, reconstructed metrics, leakage checks, or a major conclusion. The lead agent resolves disagreements against primary sources, code, manifests, and measured artifacts; do not decide by agent majority. An evidence auditor may inspect evaluation-only labels or metrics only after model/decoder/threshold/architecture/checkpoint choices are frozen, strictly for reconciliation and reporting; it must not advise those choices. Routine status checks do not require delegation.
- For code changes affecting data handling, model architecture or weights, preprocessing, vocabulary or decoding, metrics, or the training/evaluation protocol, require a read-only cross-review by an agent who did not author the change. The skeptical reviewer may also fill this role if they independently inspect the diff and complete the same review checklist; otherwise assign another reviewer. Provide the task/spec and diff; request findings with file/line, severity, rationale, and a concrete reproduction or check. Review correctness, edge cases, leakage, reproducibility, and the frozen dataset protocol before costly runs or correctness claims. Resolve findings or document why they do not apply. If no independent reviewer is available, perform a second-pass review and disclose that it was not independent.
- Keep each agent's inputs limited to the evidence needed for its role. Never expose evaluation-only labels or metrics to an agent whose work could influence model, threshold, architecture, or checkpoint selection. Sub-agents must not mutate shared code/data, update the tracker concurrently, or start overlapping LightOCR jobs unless explicitly assigned; the lead agent coordinates changes and preserves the one-GPU-job limit.
- Record material reviews in `agent_review.md` or the experiment report: agent roles and scope, evidence checked, findings, disagreements and resolution, checks performed, and the final decision. Agent suggestions are hypotheses, not experimental evidence.
- Use [AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) as a workflow reference for specialized research roles, staged literature/experiment/report work, detailed task notes, and recovery records. Use Codex sub-agents for execution in this project; do not add AgentLaboratory API credentials or its standalone runtime/dependency stack unless the user explicitly requests that integration. Its example instructions must never override this project's dataset and holdout restrictions.
