import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import controller


class ControllerTests(unittest.TestCase):
    def test_hash_is_stable_under_key_order(self):
        self.assertEqual(controller.digest({"a": 1, "b": 2}), controller.digest({"b": 2, "a": 1}))

    def test_init_is_idempotence_guarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = root / "campaign.json"
            campaign.write_text(json.dumps({"campaign_id": "tiny", "output_root": str(root / "results"),
                "screening": {"seed": 42}, "runs": [{"run_id": "r1", "model": {"loops": 0}}]}))
            controller.init(Namespace(campaign=campaign, output_root=None, workdir=None, max_runs=30))
            state_path = root / "results/research_loop/search_state.json"
            state = json.loads(state_path.read_text())
            self.assertEqual(state["runs"][0]["status"], "planned")
            with self.assertRaises(SystemExit):
                controller.init(Namespace(campaign=campaign, output_root=None, workdir=None, max_runs=30))

    def test_lost_job_becomes_review_required_and_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "search_state.json"
            state = {"output_root": str(root), "max_runs": 30,
                     "runs": [{"run_id": "missing", "status": "running", "pid": 99999999}]}
            controller.atomic_json(state_path, state)
            active, _ = controller.reconcile(state_path, state)
            self.assertEqual(active, [])
            self.assertEqual(state["runs"][0]["status"], "interrupted_needs_review")
            self.assertFalse(controller.launch_next(state_path, state))
            self.assertEqual(state["status"], "paused_on_failure")

    def test_controller_lock_prevents_duplicate_daemon(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "controller.lock"
            with controller.ControllerLock(lock_path):
                with self.assertRaises(SystemExit):
                    controller.ControllerLock(lock_path).__enter__()

    def test_partial_run_directory_halts_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "search_state.json"
            run_dir = root / "r1"
            run_dir.mkdir()
            (run_dir / "controller_manifest.json").write_text("{}")
            state = {"output_root": str(root), "max_runs": 30, "runs": [{
                "run_id": "r1", "status": "planned", "config": {"seed": 42},
                "config_hash": "abc", "pid": None}]}
            controller.atomic_json(state_path, state)
            self.assertFalse(controller.launch_next(state_path, state))
            self.assertEqual(state["runs"][0]["status"], "interrupted_needs_review")


if __name__ == "__main__":
    unittest.main()
