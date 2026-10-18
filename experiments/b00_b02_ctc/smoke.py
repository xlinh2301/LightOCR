"""Small CUDA forward/backward check for the three CTC architecture variants."""
import sys
import torch

sys.path.insert(0, "/media/gmo/linhnx/workspace/workdir_Research/source/LightOCR-1M/experiments/b00_b02_ctc")
from train import Network

for experiment in ("B00", "B01", "B02"):
    model = Network(experiment).cuda()
    logits = model(torch.randn(2, 3, 32, 192, device="cuda"))
    targets = torch.tensor([1, 2, 3, 4], device="cuda")
    loss = torch.nn.CTCLoss(blank=0)(
        logits.float().transpose(0, 1), targets,
        torch.tensor([logits.shape[1], logits.shape[1]]),
        torch.tensor([2, 2]),
    )
    loss.backward()
    print(experiment, tuple(logits.shape), sum(p.numel() for p in model.parameters()), float(loss))
    del model, logits, loss
    torch.cuda.empty_cache()
