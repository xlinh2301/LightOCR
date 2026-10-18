import unittest

import torch

from loopocr import LoopOCR, ctc_input_lengths, ctc_required_steps, greedy_decode, parameter_count


class LoopOCRTests(unittest.TestCase):
    def test_output_and_width_lengths(self):
        for width in (192, 191, 187):
            model = LoopOCR(width=32, heads=4, ff_width=64, loops=2,
                            max_steps=64, iteration_conditioning=True)
            output = model(torch.randn(2, 3, 32, width))
            self.assertEqual(output.shape, (2, (width + 3) // 4, 11))
            self.assertTrue(torch.allclose(output.exp().sum(-1), torch.ones_like(output[..., 0]), atol=1e-5))
            self.assertTrue(torch.equal(ctc_input_lengths(torch.tensor([width])), torch.tensor([(width + 3) // 4])))

    def test_ctc_repeat_feasibility(self):
        self.assertEqual(ctc_required_steps("1001"), 5)
        self.assertEqual(ctc_required_steps("1234"), 4)
        self.assertEqual(ctc_required_steps(""), 0)

    def test_greedy_repeat_collapse_order(self):
        # 1, blank, 1 must remain two adjacent equal characters after CTC collapse.
        ids = torch.tensor([[2, 2, 0, 2, 3, 3, 0]])
        probs = torch.full((1, 7, 11), -20.0)
        probs.scatter_(2, ids.unsqueeze(-1), 0.0)
        self.assertEqual(greedy_decode(probs, torch.tensor([7])), [[2, 2, 3]])

    def test_finite_gradient_and_parameter_sharing(self):
        model = LoopOCR(width=32, heads=4, ff_width=64, loops=4)
        x = torch.randn(2, 3, 32, 192)
        loss = -model(x).mean()
        loss.backward()
        self.assertTrue(torch.isfinite(loss))
        self.assertTrue(all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()))
        one = parameter_count(LoopOCR(width=32, heads=4, ff_width=64, loops=1))
        four = parameter_count(model)
        self.assertLess(four - one, 32 * 4)  # Only iteration codes should scale with K.

    def test_cnn_control_has_no_transformer(self):
        model = LoopOCR(width=32, heads=4, ff_width=64, loops=0, mixer="none")
        self.assertEqual(model(torch.randn(1, 3, 32, 192)).shape, (1, 48, 11))
        self.assertFalse(any("attention" in name.lower() for name, _ in model.named_parameters()))


if __name__ == "__main__":
    unittest.main()
