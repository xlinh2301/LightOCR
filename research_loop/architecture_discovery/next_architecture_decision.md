# Next architecture decision

**Current decision:** `DEBUG / AUDIT_PIPELINE` before GPU screening.

**Evidence:** Prior experiments on the exposed 244-example model-dev split are weak and A10 is highly seed-unstable. The latest remote connection has been intermittent; the remote checkout has no Git commits and its files are untracked. The host/container mounts, current baseline artifacts, and data hashes have not yet been reconciled for this run.

**Next actions:**

1. Reconnect and read-only inspect active processes, container mounts, source/data instructions, and prior experiment manifests/predictions.
2. Create a clean isolated remote worktree from the versioned project source without touching the untracked remote checkout or `.env`.
3. Run the LoopOCR and baseline CTC correctness tests plus the predeclared tiny-set memorization diagnostic.
4. If all gates pass, initialize `loopocr_v1_screen_20261019` and execute its seven configurations sequentially, one GPU run at a time.

No training job has been launched by this controller yet. It will refuse to start until `research_loop/sanity_results.json` records `status: passed`.
