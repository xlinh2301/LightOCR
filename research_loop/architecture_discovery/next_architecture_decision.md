# Next architecture decision

**Current decision:** `RUN REPRODUCIBLE SANITY GATE` before GPU screening.

**Evidence:** Prior experiments on the exposed 244-example model-dev split are weak and A10 is highly seed-unstable. Local Windows syntax/model/controller/metric/feasibility checks pass (14/14); the deployed version passed its 12 tests in MLR_LinhNX. SSH is intermittent but currently usable. A clean remote clone exists at `source/LightOCR-1M-architecture-loop`; the original uncommitted source tree and `.env` remain untouched. The fixed train/model-dev image/label audit passes (1467/244, no missing/ambiguous IDs), with label and split-manifest hashes recorded in `loop_progress.md`. The new reproducible both-split CTC/tiny-set gate still needs deployment and execution.

**Next actions:**

1. Deploy the updated sanity runner to the clean gmoe clone and rerun all 14 component tests inside `MLR_LinhNX`.
2. Run both-split CTC feasibility plus the 16-train-image tiny-set memorization diagnostic; record evidence and hashes.
3. If all gates pass, initialize `loopocr_v1_screen_20261019` and execute its seven configurations sequentially, one GPU run at a time.

No training job has been launched by this controller yet. It will refuse to start until `research_loop/sanity_results.json` records `status: passed`.
