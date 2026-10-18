import unittest

from PIL import Image

from train import augment_crop


class TrainAugmentationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
