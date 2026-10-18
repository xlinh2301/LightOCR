import tempfile
import unittest
from pathlib import Path

from PIL import Image

from sanity import audit_ctc_feasibility


class SanityTests(unittest.TestCase):
    def test_repeat_characters_require_blank_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.png"
            Image.new("RGB", (16, 32)).save(path)
            result = audit_ctc_feasibility(["sample.png"], {"sample.png": "1001"},
                                           {"sample.png": path})
            self.assertEqual(result["n"], 1)
            self.assertEqual(result["invalid_count"], 1)
            self.assertEqual(result["invalid_samples"][0]["required_steps"], 5)
            self.assertEqual(result["invalid_samples"][0]["available_steps"], 4)

    def test_feasible_width_reports_resized_sequence(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.png"
            Image.new("RGB", (64, 32)).save(path)
            result = audit_ctc_feasibility(["sample.png"], {"sample.png": "1001"},
                                           {"sample.png": path})
            self.assertEqual(result["invalid_count"], 0)
            self.assertEqual(result["resized_width_min"], 64)
            self.assertEqual(result["ctc_steps_min"], 16)


if __name__ == "__main__":
    unittest.main()
