"""Evidence-backed data, CTC, CUDA, and tiny-set learning gate for LoopOCR-v1."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn

from loopocr import LoopOCR, ctc_input_lengths, ctc_required_steps, greedy_decode, parameter_count
from train import CHARS, Crops, collate, resolve_data, save_json


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_ctc_feasibility(split_ids, labels, image_paths):
    invalid = []
    widths = []
    for sample_id in split_ids:
        with Image.open(image_paths[sample_id]) as image:
            width, height = image.size
        resized_width = max(1, min(192, round(width * 32 / height)))
        available = (resized_width + 3) // 4
        required = ctc_required_steps(labels[sample_id])
        widths.append(resized_width)
        if available < required:
            invalid.append({"sample_id": sample_id, "required_steps": required,
                            "available_steps": available, "resized_width": resized_width})
    return {"n": len(split_ids), "invalid_count": len(invalid),
            "invalid_samples": invalid, "resized_width_min": min(widths, default=0),
            "resized_width_max": max(widths, default=0),
            "resized_width_mean": float(np.mean(widths)) if widths else 0.0,
            "ctc_steps_min": (min(widths) + 3) // 4 if widths else 0,
            "ctc_steps_max": (max(widths) + 3) // 4 if widths else 0}


@torch.no_grad()
def tiny_metrics(model, images, targets, target_lengths, truths, widths, loss_fn, device):
    model.eval()
    log_probs = model(images.to(device))
    input_lengths = ctc_input_lengths(widths).clamp(max=log_probs.shape[1])
    loss = loss_fn(log_probs.transpose(0, 1), targets.to(device),
                   input_lengths.to(device), target_lengths.to(device))
    decoded = greedy_decode(log_probs.cpu(), input_lengths.cpu())
    predictions = ["".join(str(token - 1) for token in sequence) for sequence in decoded]
    exact = sum(pred == truth for pred, truth in zip(predictions, truths))
    return {"loss": float(loss), "exact_count": exact,
            "exact_match": exact / max(len(truths), 1), "predictions": predictions}


def run(workdir: Path, output_dir: Path, seed: int = 42, tiny_count: int = 16,
        max_steps: int = 200, min_steps: int = 30, tiny_em_threshold: float = 0.8):
    if output_dir.joinpath("sanity_results.json").exists():
        raise FileExistsError(f"refusing to overwrite sanity evidence: {output_dir / 'sanity_results.json'}")
    started = time.time()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_root = workdir / "source"
    labels, train_ids, dev_ids, image_paths, data_audit = resolve_data(workdir, source_root)
    feasibility = {
        "train": audit_ctc_feasibility(train_ids, labels, image_paths),
        "model_dev": audit_ctc_feasibility(dev_ids, labels, image_paths),
    }
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    selected_ids = sorted(random.Random(seed).sample(sorted(train_ids), min(tiny_count, len(train_ids))))
    rows = [Crops(selected_ids, labels, image_paths)[i] for i in range(len(selected_ids))]
    images, targets, target_lengths, ids, truths, widths = collate(rows)
    tiny_model_config = {"width": 32, "heads": 4, "ff_width": 64, "loops": 1,
                         "max_steps": 64, "iteration_conditioning": True}
    result = {
        "status": "failed", "started_at": started, "seed": seed,
        "environment": {"python": __import__("sys").version,
                        "torch": torch.__version__,
                        "cuda_available": torch.cuda.is_available(),
                        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None},
        "data_audit": data_audit, "data_label_sha256": sha256(workdir / "data/Indomain_curated/crops/train_label.json"),
        "split_manifest_sha256": data_audit["split_manifest_sha256"],
        "ctc_feasibility": feasibility,
        "tiny_set": {"sample_ids": ids, "labels": truths, "model": tiny_model_config,
                     "max_steps": max_steps, "min_steps": min_steps,
                     "exact_match_threshold": tiny_em_threshold},
        "test_and_cross_data_read": False,
    }
    gate_checks = {
        "expected_split_sizes": data_audit["train_n"] == 1467 and data_audit["model_dev_n"] == 244,
        "all_expected_images_found": not data_audit["missing_ids"] and not data_audit["ambiguous_ids"],
        "ctc_feasible_train": feasibility["train"]["invalid_count"] == 0,
        "ctc_feasible_model_dev": feasibility["model_dev"]["invalid_count"] == 0,
        "cuda_available": torch.cuda.is_available(),
    }
    if gate_checks["cuda_available"]:
        device = torch.device("cuda")
        model = LoopOCR(**tiny_model_config).to(device)
        params = parameter_count(model)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-4)
        loss_fn = nn.CTCLoss(blank=0, zero_infinity=False)
        initial = tiny_metrics(model, images, targets, target_lengths, truths,
                               widths, loss_fn, device)
        history = []
        torch.cuda.reset_peak_memory_stats()
        model.train()
        for step in range(1, max_steps + 1):
            optimizer.zero_grad(set_to_none=True)
            log_probs = model(images.to(device)).transpose(0, 1)
            input_lengths = ctc_input_lengths(widths).to(device)
            loss = loss_fn(log_probs, targets.to(device), input_lengths, target_lengths.to(device))
            if not torch.isfinite(loss):
                raise RuntimeError(f"nonfinite tiny-set CTC loss at step {step}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            if step % 10 == 0 or step == max_steps:
                metrics = tiny_metrics(model, images, targets, target_lengths, truths,
                                       widths, loss_fn, device)
                history.append({"step": step, "loss": metrics["loss"],
                                "exact_count": metrics["exact_count"],
                                "exact_match": metrics["exact_match"]})
                if step >= min_steps and metrics["exact_match"] >= 1.0 and metrics["loss"] < initial["loss"]:
                    break
                model.train()
        final = tiny_metrics(model, images, targets, target_lengths, truths,
                             widths, loss_fn, device)
        result["tiny_set"].update({"initial_loss": initial["loss"],
            "initial_exact_count": initial["exact_count"], "initial_exact_match": initial["exact_match"],
            "final_loss": final["loss"], "final_exact_count": final["exact_count"],
            "final_exact_match": final["exact_match"], "final_predictions": final["predictions"],
            "history": history, "optimizer_steps": history[-1]["step"] if history else 0,
            "params": params, "peak_vram_bytes": torch.cuda.max_memory_allocated()})
        gate_checks["tiny_set_loss_decreased"] = final["loss"] < initial["loss"]
        gate_checks["tiny_set_em_threshold"] = final["exact_match"] >= tiny_em_threshold
        result["tiny_set_predictions_path"] = str(output_dir / "sanity_tiny_set_predictions.jsonl")
        with Path(result["tiny_set_predictions_path"]).open("w", encoding="utf-8") as stream:
            for sample_id, truth, prediction in zip(ids, truths, final["predictions"]):
                stream.write(json.dumps({"sample_id": sample_id, "truth": truth,
                                         "prediction": prediction}, ensure_ascii=False) + "\n")
    else:
        gate_checks["tiny_set_loss_decreased"] = False
        gate_checks["tiny_set_em_threshold"] = False
    result["gate_checks"] = gate_checks
    result["status"] = "passed" if all(gate_checks.values()) else "failed"
    result["finished_at"] = time.time()
    result["runtime_seconds"] = result["finished_at"] - started
    save_json(output_dir / "sanity_results.json", result)
    print(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, default=Path("/media/gmo/linhnx/workspace/workdir_Research"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tiny-count", type=int, default=16)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--min-steps", type=int, default=30)
    parser.add_argument("--tiny-em-threshold", type=float, default=0.8)
    args = parser.parse_args()
    result = run(args.workdir, args.output_dir, args.seed, args.tiny_count,
                 args.max_steps, args.min_steps, args.tiny_em_threshold)
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
