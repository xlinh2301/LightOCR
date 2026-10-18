"""LoopOCR-v1: compact CNN + recurrent/shared Transformer + digit CTC head."""
from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class DepthwiseSeparableBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, stride: tuple[int, int]):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, in_ch, 3, stride=stride, padding=1, groups=in_ch, bias=False),
            nn.BatchNorm2d(in_ch), nn.SiLU(inplace=True),
            nn.Conv2d(in_ch, out_ch, 1, bias=False),
            nn.BatchNorm2d(out_ch), nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class SharedTransformerRefiner(nn.Module):
    """One block reused K times; iteration embedding is optional and parameter-light."""
    def __init__(self, width: int, heads: int, ff_width: int, max_loops: int,
                 iteration_conditioning: bool = True, dropout: float = 0.0):
        super().__init__()
        self.block = nn.TransformerEncoderLayer(
            d_model=width, nhead=heads, dim_feedforward=ff_width, dropout=dropout,
            activation="gelu", batch_first=True, norm_first=True,
        )
        self.iteration_conditioning = iteration_conditioning
        self.iteration = nn.Embedding(max_loops, width) if iteration_conditioning else None
        self.norm = nn.LayerNorm(width)

    def forward(self, x: torch.Tensor, loops: int) -> torch.Tensor:
        if loops < 1 or loops > (self.iteration.num_embeddings if self.iteration is not None else 64):
            raise ValueError(f"invalid loop count: {loops}")
        for i in range(loops):
            if self.iteration is not None:
                x = x + self.iteration.weight[i].view(1, 1, -1)
            x = self.block(x)
        return self.norm(x)


class LoopOCR(nn.Module):
    """Input `[B,3,32,192]`; output log-probs `[B,T,11]`, blank index 0."""
    def __init__(self, *, width: int = 128, heads: int = 4, ff_width: int = 256,
                 loops: int = 1, mixer: str = "shared", max_steps: int = 64,
                 iteration_conditioning: bool = True, dropout: float = 0.0,
                 classes: int = 11):
        super().__init__()
        if width % heads:
            raise ValueError("width must be divisible by heads")
        if mixer not in {"none", "shared", "untied"}:
            raise ValueError(f"unknown mixer: {mixer}")
        if mixer == "none" and loops != 0:
            raise ValueError("mixer='none' requires loops=0")
        if mixer != "none" and loops < 1:
            raise ValueError("Transformer mixers require loops >= 1")
        self.loops = loops
        self.mixer = mixer
        self.stem = nn.Sequential(
            DepthwiseSeparableBlock(3, 32, (2, 2)),
            DepthwiseSeparableBlock(32, 64, (2, 2)),
            DepthwiseSeparableBlock(64, 96, (2, 1)),
            DepthwiseSeparableBlock(96, width, (2, 1)),
            DepthwiseSeparableBlock(width, width, (2, 1)),
        )
        self.input_norm = nn.LayerNorm(width)
        self.position = nn.Parameter(torch.zeros(1, max_steps, width))
        nn.init.trunc_normal_(self.position, std=0.02)
        if mixer == "shared":
            self.refiners = SharedTransformerRefiner(
                width, heads, ff_width, max_loops=max(loops, 1),
                iteration_conditioning=iteration_conditioning, dropout=dropout,
            )
            self.untied = None
        elif mixer == "untied":
            self.refiners = None
            self.untied = nn.ModuleList([
                nn.TransformerEncoderLayer(width, heads, ff_width, dropout,
                    activation="gelu", batch_first=True, norm_first=True)
                for _ in range(loops)
            ])
            self.output_norm = nn.LayerNorm(width)
        else:
            self.refiners = None
            self.untied = None
            self.output_norm = nn.Identity()
        self.head = nn.Linear(width, classes)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        x = self.stem(images).mean(dim=2).transpose(1, 2).contiguous()
        if x.shape[1] > self.position.shape[1]:
            raise ValueError(f"sequence length {x.shape[1]} exceeds positional capacity {self.position.shape[1]}")
        x = self.input_norm(x + self.position[:, :x.shape[1]])
        if self.refiners is not None:
            x = self.refiners(x, self.loops)
        elif self.untied is not None:
            for block in self.untied:
                x = block(x)
            x = self.output_norm(x)
        else:
            x = self.output_norm(x)
        return F.log_softmax(self.head(x), dim=-1)


def ctc_input_lengths(widths: torch.Tensor) -> torch.Tensor:
    """Two width-halving stem stages: ceil(width/4), matching padded convolutions."""
    return torch.div(widths + 3, 4, rounding_mode="floor")


def ctc_required_steps(target: str) -> int:
    """Minimum CTC frames for a string, including mandatory blank separators."""
    return len(target) + sum(a == b for a, b in zip(target, target[1:]))


def greedy_decode(log_probs: torch.Tensor, lengths: torch.Tensor) -> list[list[int]]:
    """Greedy CTC collapse: merge adjacent repeats before removing blank 0."""
    if log_probs.ndim != 3:
        raise ValueError("expected [B,T,C] log probabilities")
    out: list[list[int]] = []
    ids = log_probs.argmax(dim=-1)
    for row, n in zip(ids, lengths.tolist()):
        decoded: list[int] = []
        previous = 0
        for token in row[:n].tolist():
            if token != previous and token != 0:
                decoded.append(token)
            previous = token
        out.append(decoded)
    return out


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
