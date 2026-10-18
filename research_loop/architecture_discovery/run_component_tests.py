"""Run the component suite and persist output when a remote SSH stream is flaky."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()
    tests_dir = Path(__file__).resolve().parent
    started = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-v"],
            cwd=tests_dir, capture_output=True, text=True,
            timeout=args.timeout_seconds, check=False,
        )
        output = result.stdout + result.stderr
        status = "passed" if result.returncode == 0 else "failed"
        exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        chunks = [exc.stdout, exc.stderr]
        output = "".join(
            chunk.decode(errors="replace") if isinstance(chunk, bytes) else (chunk or "")
            for chunk in chunks
        ) + "\nTEST_SUITE_TIMEOUT\n"
        status, exit_code = "timeout", 124
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "component_tests.log").write_text(output, encoding="utf-8")
    summary = {
        "status": status,
        "exit_code": exit_code,
        "started_at_unix": started,
        "finished_at_unix": time.time(),
        "runtime_seconds": time.time() - started,
        "test_directory": str(tests_dir),
        "suite": "unittest discover",
        "test_data_accessed": False,
    }
    (args.output_dir / "component_tests.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
