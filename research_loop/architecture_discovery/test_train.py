import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from train import Crops, augment_crop, resolve_data


class TrainAugmentationTests(unittest.TestCase):
    def test_resolve_data_accepts_audited_custom_split_sizes(self):
        import json
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data = root / "data/Indomain_curated/crops"
            source = root / "source/EditCTC/experiments/PAE_CTC/pilot_007/cache"
            (data / "train").mkdir(parents=True)
            (data / "valid").mkdir()
            source.mkdir(parents=True)
            labels = {}
            train_ids = ["a.png", "b.png"]
            dev_ids = ["c.png"]
            for sid in train_ids + dev_ids:
                labels[sid] = "123"
                Image.new("RGB", (48, 32), color=(80, 120, 160)).save(
                    data / ("valid" if sid == "c.png" else "train") / sid)
            (data / "train_label.json").write_text(json.dumps(labels), encoding="utf-8")
            for fold, sid in enumerate(train_ids):
                (source / f"base_fit_fold_{fold}.jsonl").write_text(
                    json.dumps({"sample_id": sid}) + "\n", encoding="utf-8")
            for fold in range(2, 5):
                (source / f"base_fit_fold_{fold}.jsonl").write_text("", encoding="utf-8")
            (source / "model_dev.jsonl").write_text(
                json.dumps({"sample_id": "c.png"}) + "\n", encoding="utf-8")
            (source / "manifest.json").write_text("{}", encoding="utf-8")
            _, train, dev, paths, audit = resolve_data(root, root / "source", 2, 1)
            self.assertEqual((len(train), len(dev)), (2, 1))
            self.assertEqual(len(paths), 3)
            self.assertEqual(audit["expected_train_n"], 2)
            self.assertEqual(audit["split_kind"], "configured_exploratory_split")

    def test_disabled_augmentation_returns_input_unchanged(self):
        image = Image.new("RGB", (96, 32), color=(80, 120, 160))
        self.assertIs(augment_crop(image, {}), image)

    def test_augmentation_preserves_rgb_dimensions(self):
        image = Image.new("RGB", (96, 32), color=(80, 120, 160))
        result = augment_crop(image, {
            "rotation_degrees": 2.0,
            "brightness_delta": 0.12,
            "contrast_delta": 0.12,
            "blur_probability": 1.0,
            "blur_radius_max": 0.6,
        })
        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, image.size)

    def test_configurable_crop_resolution_and_ctc_width(self):
        with TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "sample.png"
            Image.new("RGB", (120, 40), color=(80, 120, 160)).save(image_path)
            sample = Crops(["sample.png"], {"sample.png": "1234"},
                           {"sample.png": image_path}, image_height=48, image_width=320)[0]
        image, target, sample_id, truth, resized_width = sample
        self.assertEqual(tuple(image.shape), (3, 48, 320))
        self.assertEqual(resized_width, 144)
        self.assertEqual(sample_id, "sample.png")
        self.assertEqual(truth, "1234")
        self.assertEqual(target.tolist(), [2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
