"""Restartable sequential experiment controller; failed runs are retained, never retried."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def digest(data) -> str:
    blob = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def append_event(path: Path, kind: str, **fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"at": now(), "event": kind, **fields}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def load_state(state_path: Path):
    if not state_path.is_file():
        raise SystemExit(f"state not initialized: {state_path}; run init first")
    return json.loads(state_path.read_text(encoding="utf-8"))


def process_matches(pid: int, run_dir: str) -> bool:
    proc = Path(f"/proc/{pid}/cmdline")
    if not proc.exists():
        return False
    try:
        command = proc.read_bytes().replace(b"\0", b" ").decode(errors="replace")
        return run_dir in command and "architecture_discovery/train.py" in command
    except OSError:
        return False


def find_run_process(run_dir: str):
    for proc in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            command = proc.read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if run_dir in command and "architecture_discovery/train.py" in command:
            try:
                return int(proc.parent.name)
            except ValueError:
                pass
    return None


class ControllerLock:
    """Single controller/queue writer per campaign; keeps separate launches serialized."""
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+")
        try:
            if os.name == "nt":
                self.handle.seek(0, os.SEEK_END)
                if self.handle.tell() == 0:
                    self.handle.write(" ")
                    self.handle.flush()
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            raise SystemExit(f"another controller/queue writer holds {self.path}") from exc
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.handle:
            if os.name == "nt":
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()


def init(args):
    campaign_file = args.campaign.resolve()
    campaign = json.loads(campaign_file.read_text(encoding="utf-8"))
    root = Path(args.output_root or campaign["output_root"]).resolve()
    control = root / "research_loop"
    state_path = control / "search_state.json"
    if state_path.exists():
        raise SystemExit(f"refusing to overwrite existing controller state: {state_path}")
    runs = []
    seen = set()
    for item in campaign["runs"]:
        rid = item["run_id"]
        if rid in seen:
            raise SystemExit(f"duplicate run_id in campaign: {rid}")
        seen.add(rid)
        run_cfg = {**campaign["screening"], **item,
                   "workdir": getattr(args, "workdir", None) or campaign.get("workdir", "/media/gmo/linhnx/workspace/workdir_Research"),
                   "repo_path": getattr(args, "repo_path", None) or campaign.get("repo_path"),
                   "run_id": rid}
        cfg_hash = digest(run_cfg)
        runs.append({"run_id": rid, "config": run_cfg, "config_hash": cfg_hash,
                     "status": "planned", "pid": None, "started_at": None,
                     "finished_at": None, "exit_code": None})
    state = {"campaign_id": campaign["campaign_id"], "status": "awaiting_sanity_gate",
             "created_at": now(), "updated_at": now(), "output_root": str(root),
             "source_campaign": str(campaign_file), "source_campaign_sha256": hashlib.sha256(campaign_file.read_bytes()).hexdigest(),
             "max_runs": int(args.max_runs), "next_action": "run_sanity_tests_then_screen",
             "runs": runs, "decision_log": []}
    atomic_json(state_path, state)
    atomic_json(control / "campaign_snapshot.json", campaign)
    append_event(control / "events.jsonl", "campaign_initialized", campaign_id=state["campaign_id"],
                 run_count=len(runs), state_sha256=digest(state))
    print(json.dumps({"state": str(state_path), "runs": len(runs), "status": state["status"]}, indent=2))


def reconcile(state_path: Path, state: dict):
    root = Path(state["output_root"])
    changed = False
    active = []
    for run in state["runs"]:
        if run["status"] not in {"running", "launching"}:
            continue
        run_dir = root / run["run_id"]
        pid = run.get("pid")
        alive = bool(pid and process_matches(int(pid), str(run_dir)))
        progress_file = run_dir / "progress_summary.json"
        progress = json.loads(progress_file.read_text(encoding="utf-8")) if progress_file.exists() else {}
        if alive:
            active.append(run["run_id"])
            continue
        status = progress.get("status")
        if status == "completed" and (run_dir / "summary.json").exists() and (run_dir / "predictions_dev.jsonl").exists():
            run["status"] = "completed"
            run["result"] = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
            run["finished_at"] = progress.get("finished_at", now())
        elif status == "failed":
            run["status"] = "failed"
            run["failure"] = progress
            run["finished_at"] = progress.get("finished_at", now())
        else:
            run["status"] = "interrupted_needs_review"
            run["reconciliation_note"] = "PID no longer matches and no verified terminal result exists; automatic retry prohibited."
            run["finished_at"] = now()
        changed = True
    if changed:
        state["updated_at"] = now()
        atomic_json(state_path, state)
    return active, changed


def launch_next(state_path: Path, state: dict):
    root = Path(state["output_root"])
    runs = state["runs"]
    completed = sum(r["status"] == "completed" for r in runs)
    if completed >= state["max_runs"]:
        state["status"] = "budget_exhausted"
        state["next_action"] = "review_budget_and_evidence"
        atomic_json(state_path, state)
        return False
    failed = [r for r in runs if r["status"] in {"failed", "interrupted_needs_review"}]
    if failed:
        state["status"] = "paused_on_failure"
        state["next_action"] = "human_review_failure_before_any_retry"
        atomic_json(state_path, state)
        return False
    planned = next((r for r in runs if r["status"] == "planned"), None)
    if planned is None:
        state["status"] = "campaign_screen_complete"
        state["next_action"] = "independently_reconstruct_metrics_and_review"
        atomic_json(state_path, state)
        return False
    run_dir = root / planned["run_id"]
    if run_dir.exists():
        pid = find_run_process(str(run_dir))
        if pid is not None:
            planned.update({"status": "running", "pid": pid, "run_dir": str(run_dir),
                            "reconciliation_note": "Recovered matching training process after controller restart."})
            state["status"] = "running"
            state["updated_at"] = now()
            atomic_json(state_path, state)
            append_event(root / "research_loop/events.jsonl", "run_process_recovered",
                         run_id=planned["run_id"], pid=pid)
            return True
        progress_file = run_dir / "progress_summary.json"
        progress = json.loads(progress_file.read_text(encoding="utf-8")) if progress_file.exists() else {}
        if progress.get("status") == "completed" and (run_dir / "summary.json").exists() and (run_dir / "predictions_dev.jsonl").exists():
            planned["status"] = "completed"
            planned["result"] = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
            planned["finished_at"] = progress.get("finished_at", now())
            state["updated_at"] = now()
            atomic_json(state_path, state)
            append_event(root / "research_loop/events.jsonl", "completed_run_recovered",
                         run_id=planned["run_id"])
            return True
        if progress.get("status") == "failed":
            planned["status"] = "failed"
            planned["failure"] = progress
        else:
            planned["status"] = "interrupted_needs_review"
            planned["reconciliation_note"] = "Run directory exists but no matching process or verified terminal result was found; no automatic retry."
        planned["finished_at"] = now()
        state["status"] = "paused_on_failure"
        state["next_action"] = "human_review_failure_before_any_retry"
        state["updated_at"] = now()
        atomic_json(state_path, state)
        append_event(root / "research_loop/events.jsonl", "uncertain_launch_halted",
                     run_id=planned["run_id"], status=planned["status"])
        return False
    run_dir.mkdir(parents=True, exist_ok=False)
    cfg_path = run_dir / "config.json"
    atomic_json(cfg_path, planned["config"])
    run_manifest = {"run_id": planned["run_id"], "config_hash": planned["config_hash"],
                    "created_at": now(), "run_dir": str(run_dir), "status": "launching"}
    atomic_json(run_dir / "controller_manifest.json", run_manifest)
    command = [sys.executable, str(Path(__file__).with_name("train.py")),
               "--config", str(cfg_path), "--run-dir", str(run_dir)]
    log = (run_dir / "controller.log").open("ab", buffering=0)
    process = subprocess.Popen(command, cwd=str(Path(__file__).parent), stdout=log,
        stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
    planned.update({"status": "running", "pid": process.pid, "started_at": now(),
                    "command": command, "run_dir": str(run_dir)})
    state["status"] = "running"
    state["updated_at"] = now()
    atomic_json(state_path, state)
    append_event(Path(state["output_root"]) / "research_loop/events.jsonl", "run_started",
                 run_id=planned["run_id"], pid=process.pid, config_hash=planned["config_hash"], command=command)
    print(f"launched {planned['run_id']} pid={process.pid}")
    return True


def daemon(args):
    state_path = args.state.resolve()
    initial = load_state(state_path)
    gate = Path(initial["output_root"]) / "research_loop/sanity_results.json"
    if not gate.is_file():
        raise SystemExit(f"refusing to launch training before diagnostics are recorded: {gate}")
    sanity = json.loads(gate.read_text(encoding="utf-8"))
    if sanity.get("status") != "passed":
        raise SystemExit(f"diagnostic gate is not passed: status={sanity.get('status')}")
    stop = False
    def stop_handler(signum, frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    while not stop:
        state = load_state(state_path)
        active, changed = reconcile(state_path, state)
        if active:
            state["status"] = "running"
            state["updated_at"] = now()
            atomic_json(state_path, state)
        elif not launch_next(state_path, state):
            return 0
        time.sleep(args.poll_seconds)
    state = load_state(state_path)
    state["status"] = "controller_stopped_jobs_left_undisturbed"
    state["updated_at"] = now()
    atomic_json(state_path, state)
    append_event(Path(state["output_root"]) / "research_loop/events.jsonl", "controller_stopped")
    return 0


def show(args):
    state = load_state(args.state.resolve())
    active = [r["run_id"] for r in state["runs"]
              if r["status"] in {"running", "launching"} and r.get("pid")
              and process_matches(int(r["pid"]), r.get("run_dir", ""))]
    counts = {}
    for run in state["runs"]:
        counts[run["status"]] = counts.get(run["status"], 0) + 1
    print(json.dumps({"campaign_id": state["campaign_id"], "status": state["status"],
        "counts": counts, "active": active, "next_action": state.get("next_action"),
        "runs": [{k: r.get(k) for k in ("run_id", "status", "pid", "started_at", "finished_at")} for r in state["runs"]]}, indent=2))


def queue(args):
    state_path = args.state.resolve()
    state = load_state(state_path)
    if any(r["status"] in {"running", "launching"} for r in state["runs"]):
        raise SystemExit("cannot append a candidate while another run is active")
    candidate = json.loads(args.config.read_text(encoding="utf-8"))
    required = {"run_id", "hypothesis", "model", "seed"}
    missing = sorted(required - set(candidate))
    if missing:
        raise SystemExit(f"candidate misses required fields: {missing}")
    if any(r["run_id"] == candidate["run_id"] for r in state["runs"]):
        raise SystemExit(f"duplicate run_id: {candidate['run_id']}")
    if len(state["runs"]) >= state["max_runs"]:
        state["status"] = "budget_exhausted"
        state["next_action"] = "request_budget_decision"
        atomic_json(state_path, state)
        raise SystemExit("declared run budget exhausted")
    candidate.setdefault("epochs", 50)
    candidate.setdefault("patience", 10)
    candidate.setdefault("batch_size", 32)
    candidate.setdefault("workers", 4)
    candidate.setdefault("workdir", "/media/gmo/linhnx/workspace/workdir_Research")
    state["runs"].append({"run_id": candidate["run_id"], "config": candidate,
        "config_hash": digest(candidate), "status": "planned", "pid": None,
        "started_at": None, "finished_at": None, "exit_code": None})
    state["decision_log"].append({"at": now(), "action": "TUNE_OR_CHANGE_ARCHITECTURE",
        "hypothesis": candidate["hypothesis"], "run_id": candidate["run_id"],
        "config_hash": digest(candidate), "evidence_file": args.evidence})
    state["status"] = "ready"
    state["next_action"] = "run_next_queued_candidate"
    state["updated_at"] = now()
    atomic_json(state_path, state)
    append_event(Path(state["output_root"]) / "research_loop/events.jsonl", "run_queued",
                 run_id=candidate["run_id"], config_hash=digest(candidate), evidence_file=args.evidence)
    print(f"queued {candidate['run_id']}")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("init")
    p.add_argument("--campaign", type=Path, required=True)
    p.add_argument("--output-root")
    p.add_argument("--workdir")
    p.add_argument("--repo-path")
    p.add_argument("--max-runs", type=int, default=30)
    p.set_defaults(func=init)
    p = commands.add_parser("run")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--poll-seconds", type=int, default=30)
    p.set_defaults(func=daemon)
    p = commands.add_parser("status")
    p.add_argument("--state", type=Path, required=True)
    p.set_defaults(func=show)
    p = commands.add_parser("queue")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--evidence", required=True, help="relative report/artifact that justifies this candidate")
    p.set_defaults(func=queue)
    args = parser.parse_args()
    if args.command == "init":
        campaign = json.loads(args.campaign.read_text(encoding="utf-8"))
        root = Path(args.output_root or campaign["output_root"]).resolve()
        lock_path = root / "research_loop/controller.lock"
        with ControllerLock(lock_path):
            result = args.func(args)
    elif args.command in {"run", "queue"}:
        state_path = args.state.resolve()
        with ControllerLock(state_path.parent / "controller.lock"):
            result = args.func(args)
    else:
        result = args.func(args)
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    main()
