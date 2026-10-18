import json
import tempfile
import unittest
from pathlib import Path

from verify_predictions import counts, reconstruct


class VerifyTests(unittest.TestCase):
    def test_edit_counts(self):
        self.assertEqual(counts("123", "193"), (1, 1, 0, 0))
        self.assertEqual(counts("123", "12"), (1, 0, 1, 0))
        self.assertEqual(counts("12", "123"), (1, 0, 0, 1))

    def test_reconstruction_preserves_leading_zero_and_checks_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "split.jsonl").write_text('{"sample_id":"a.png"}\n{"sample_id":"b.png"}\n')
            (root / "labels.json").write_text(json.dumps({"a.png": "012", "b.png": "77"}))
            (root / "predictions.jsonl").write_text(
                '{"sample_id":"a.png","truth":"012","prediction":"012"}\n'
                '{"sample_id":"b.png","truth":"77","prediction":"7"}\n')
            metrics, failures = reconstruct(root / "predictions.jsonl", root / "split.jsonl", root / "labels.json")
            self.assertEqual(metrics["exact_count"], 1)
            self.assertEqual(metrics["n"], 2)
            self.assertEqual(metrics["deletions"], 1)
            self.assertEqual(failures[0]["sample_id"], "b.png")


if __name__ == "__main__":
    unittest.main()
