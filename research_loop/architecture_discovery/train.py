"""Train one LoopOCR-v1 configuration on the frozen in-domain train/dev split."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import subprocess
import time
import traceback
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageEnhance, ImageFilter
from torch import nn
from torch.utils.data import DataLoader, Dataset

from loopocr import LoopOCR, ctc_input_lengths, ctc_required_steps, greedy_decode, parameter_count

WORKDIR = Path("/media/gmo/linhnx/workspace/workdir_Research")
CHARS = "0123456789"
MEAN = np.array([.485, .456, .406], np.float32)
STD = np.array([.229, .224, .225], np.float32)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def read_ids(path: Path) -> list[str]:
    return [Path(json.loads(line)["sample_id"]).name
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def augment_crop(image: Image.Image, cfg: dict) -> Image.Image:
    """Apply mild train-only geometric and photometric perturbations."""
    if not cfg:
        return image
    rotation = float(cfg.get("rotation_degrees", 0.0))
    if rotation:
        image = image.rotate(random.uniform(-rotation, rotation),
            resample=Image.Resampling.BILINEAR, expand=False,
            fillcolor=tuple(int(v * 255) for v in MEAN))
    brightness = float(cfg.get("brightness_delta", 0.0))
    if brightness:
        image = ImageEnhance.Brightness(image).enhance(
            random.uniform(max(0.1, 1.0 - brightness), 1.0 + brightness))
    contrast = float(cfg.get("contrast_delta", 0.0))
    if contrast:
        image = ImageEnhance.Contrast(image).enhance(
            random.uniform(max(0.1, 1.0 - contrast), 1.0 + contrast))
    if random.random() < float(cfg.get("blur_probability", 0.0)):
        image = image.filter(ImageFilter.GaussianBlur(
            radius=random.uniform(0.1, float(cfg.get("blur_radius_max", 0.6)))))
    return image


class Crops(Dataset):
    def __init__(self, ids, labels, image_paths, augmentation=None,
                 image_height: int = 32, image_width: int = 192):
        self.ids, self.labels, self.image_paths = ids, labels, image_paths
        self.augmentation = augmentation or {}
        if image_height < 1 or image_width < 1:
            raise ValueError("image_height and image_width must be positive")
        self.image_height, self.image_width = image_height, image_width

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index):
        sample_id = self.ids[index]
        truth = self.labels[sample_id]
        with Image.open(self.image_paths[sample_id]) as image:
            image = augment_crop(image.convert("RGB"), self.augmentation)
            width, height = image.size
            out_width = max(1, min(self.image_width, round(width * self.image_height / height)))
            pixels = np.asarray(image.resize((out_width, self.image_height), Image.Resampling.BILINEAR), dtype=np.float32) / 255
        padded = np.empty((self.image_height, self.image_width, 3), dtype=np.float32)
        padded[:] = MEAN
        padded[:, :out_width] = pixels
        tensor = torch.from_numpy(((padded - MEAN) / STD).transpose(2, 0, 1).copy())
        noise_std = float(self.augmentation.get("gaussian_noise_std", 0.0))
        if noise_std:
            tensor = tensor + torch.randn_like(tensor) * noise_std
        target = torch.tensor([int(c) + 1 for c in truth], dtype=torch.long)
        return tensor, target, sample_id, truth, out_width


def collate(rows):
    images, targets, ids, truths, widths = zip(*rows)
    return (torch.stack(images), torch.cat(targets), torch.tensor([len(t) for t in targets]),
            list(ids), list(truths), torch.tensor(widths))


def edit_counts(reference: str, hypothesis: str):
    dp = [[0] * (len(hypothesis) + 1) for _ in range(len(reference) + 1)]
    for i in range(len(reference) + 1):
        dp[i][0] = i
    for j in range(len(hypothesis) + 1):
        dp[0][j] = j
    for i, ref in enumerate(reference, 1):
        for j, hyp in enumerate(hypothesis, 1):
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + (ref != hyp))
    i, j = len(reference), len(hypothesis)
    sub = delete = insert = 0
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1] + (reference[i-1] != hypothesis[j-1]):
            sub += reference[i-1] != hypothesis[j-1]
            i -= 1; j -= 1
        elif i and dp[i][j] == dp[i-1][j] + 1:
            delete += 1; i -= 1
        else:
            insert += 1; j -= 1
    return sub, delete, insert


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    predictions = []
    for images, _, _, ids, truths, widths in loader:
        probs = model(images.to(device)).cpu()
        lengths = ctc_input_lengths(widths).clamp(max=probs.shape[1])
        decoded = greedy_decode(probs, lengths)
        for sid, truth, seq in zip(ids, truths, decoded):
            pred = "".join(str(x - 1) for x in seq)
            sub, deletion, insertion = edit_counts(truth, pred)
            predictions.append({"sample_id": sid, "truth": truth, "prediction": pred,
                                "substitutions": sub, "deletions": deletion, "insertions": insertion})
    n = len(predictions)
    char_count = sum(len(x["truth"]) for x in predictions)
    errors = sum(x[k] for x in predictions for k in ("substitutions", "deletions", "insertions"))
    exact = sum(x["truth"] == x["prediction"] for x in predictions)
    return predictions, {"n": n, "exact_count": exact, "exact_match": exact / max(n, 1),
                        "cer": errors / max(char_count, 1), "edit_count": errors,
                        "reference_chars": char_count}


def resolve_data(workdir: Path, source_root: Path):
    data = workdir / "data/Indomain_curated/crops"
    cache = source_root / "EditCTC/experiments/PAE_CTC/pilot_007/cache"
    labels = json.loads((data / "train_label.json").read_text(encoding="utf-8"))
    train = sum((read_ids(cache / f"base_fit_fold_{i}.jsonl") for i in range(5)), [])
    dev = read_ids(cache / "model_dev.jsonl")
    overlap = sorted(set(train) & set(dev))
    if len(train) != 1467 or len(dev) != 244 or overlap:
        raise RuntimeError(f"fixed split audit failed: train={len(train)} dev={len(dev)} overlap={len(overlap)}")
    bad = [sid for sid in train + dev if sid not in labels or not labels.get(sid)
           or any(c not in CHARS for c in labels.get(sid, ""))]
    if bad:
        raise RuntimeError(f"missing/invalid targets: n={len(bad)} examples={bad[:8]}")
    image_paths, missing, ambiguous = {}, [], []
    counts = {"train": 0, "valid": 0}
    for sid in sorted(set(train + dev)):
        matches = [(part, data / part / sid) for part in ("train", "valid") if (data / part / sid).is_file()]
        if len(matches) == 0:
            missing.append(sid)
        elif len(matches) > 1:
            ambiguous.append(sid)
        else:
            part, path = matches[0]
            counts[part] += 1
            image_paths[sid] = path
    if missing or ambiguous:
        raise RuntimeError(f"image audit failed: missing={len(missing)} ambiguous={len(ambiguous)}")
    audit = {"train_n": len(train), "model_dev_n": len(dev), "physical_source_counts": counts,
             "label_file_sha256": sha256(data / "train_label.json"),
             "split_manifest_sha256": sha256(cache / "manifest.json"),
             "test_and_cross_data_read": False, "missing_ids": missing, "ambiguous_ids": ambiguous}
    return labels, train, dev, image_paths, audit


def run(config_path: Path, run_dir: Path):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    run_dir.mkdir(parents=True, exist_ok=True)
    if any((run_dir / name).exists() for name in ("manifest.json", "checkpoint_best.pt", "summary.json")):
        raise FileExistsError(f"refusing to reuse a run directory with existing artifacts: {run_dir}")
    start = time.time()
    save_json(run_dir / "progress_summary.json", {"status": "initializing", "started_at": start})
    workdir = Path(cfg.get("workdir", WORKDIR))
    source_root = Path(cfg.get("source_root", workdir / "source"))
    labels, train_ids, dev_ids, image_paths, audit = resolve_data(workdir, source_root)
    seed = int(cfg["seed"])
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; this run requires MLR_LinhNX")
    generator = torch.Generator().manual_seed(seed)
    batch = int(cfg.get("batch_size", 32)); workers = int(cfg.get("workers", 4))
    image_height = int(cfg.get("image_height", 32)); image_width = int(cfg.get("image_width", 192))
    required_position_steps = (image_width + 3) // 4
    if int(cfg["model"].get("max_steps", 64)) < required_position_steps:
        raise ValueError(f"model.max_steps={cfg['model'].get('max_steps')} is below input sequence length {required_position_steps}")
    train_loader = DataLoader(Crops(train_ids, labels, image_paths, cfg.get("augmentation"), image_height, image_width), batch_size=batch, shuffle=True,
        generator=generator, num_workers=workers, pin_memory=True, collate_fn=collate)
    dev_loader = DataLoader(Crops(dev_ids, labels, image_paths, image_height=image_height, image_width=image_width), batch_size=batch, shuffle=False,
        num_workers=workers, pin_memory=True, collate_fn=collate)
    model = LoopOCR(**cfg["model"]).cuda()
    params = parameter_count(model)
    invalid = []
    for _, _, _, ids, truths, widths in DataLoader(Crops(train_ids, labels, image_paths, image_height=image_height, image_width=image_width),
            batch_size=64, shuffle=False, num_workers=0, collate_fn=collate):
        for sid, truth, width in zip(ids, truths, widths.tolist()):
            frames = int(ctc_input_lengths(torch.tensor([width]))[0])
            need = ctc_required_steps(truth)
            if frames < need:
                invalid.append({"sample_id": sid, "required_steps": need, "available_steps": frames})
    save_json(run_dir / "data_file_audit.json", audit)
    save_json(run_dir / "ctc_feasibility.json", {"invalid_count": len(invalid), "invalid_samples": invalid,
        "all_rows_retained": True})
    if invalid:
        raise RuntimeError(f"CTC infeasible rows: {len(invalid)}")
    source_dir = Path(cfg.get("repo_path") or (source_root / "LightOCR-1M"))
    source_commit = subprocess.run(["git", "-C", str(source_dir), "rev-parse", "HEAD"],
        text=True, capture_output=True).stdout.strip()
    source_dirty = subprocess.run(["git", "-C", str(source_dir), "status", "--short"],
        text=True, capture_output=True).stdout.splitlines()
    manifest = {"run_id": cfg["run_id"], "config": cfg, "config_sha256": sha256(config_path),
        "source_commit": source_commit, "source_dirty_state": source_dirty,
        "source_code_sha256": {name: sha256(Path(__file__).with_name(name)) for name in ("train.py", "loopocr.py")},
        "data_audit": audit, "params": params,
        "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "seed": seed,
        "test_and_cross_data_read": False}
    save_json(run_dir / "manifest.json", manifest)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(cfg.get("lr", 0.001)),
                                  weight_decay=float(cfg.get("weight_decay", 1e-4)))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=int(cfg["epochs"]))
    loss_fn = nn.CTCLoss(blank=0, zero_infinity=False)
    history = (run_dir / "train_history.csv").open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(history, fieldnames=["epoch", "train_loss", "dev_cer", "dev_exact_match", "seconds"])
    writer.writeheader()
    best_key = (float("inf"), 0.0); best_epoch = 0; stale = 0
    torch.cuda.reset_peak_memory_stats()
    try:
        for epoch in range(1, int(cfg["epochs"]) + 1):
            model.train(); loss_sum = 0.0; batch_count = 0; epoch_start = time.time()
            for images, targets, target_lengths, _, _, widths in train_loader:
                images, targets = images.cuda(non_blocking=True), targets.cuda(non_blocking=True)
                input_lengths = ctc_input_lengths(widths).cuda(non_blocking=True)
                optimizer.zero_grad(set_to_none=True)
                log_probs = model(images).transpose(0, 1)
                loss = loss_fn(log_probs, targets, input_lengths, target_lengths.cuda())
                if not torch.isfinite(loss):
                    raise RuntimeError(f"nonfinite loss at epoch {epoch}")
                loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0); optimizer.step()
                loss_sum += float(loss.detach()); batch_count += 1
            scheduler.step()
            predictions, metrics = evaluate(model, dev_loader, torch.device("cuda"))
            writer.writerow({"epoch": epoch, "train_loss": loss_sum / max(batch_count, 1),
                "dev_cer": metrics["cer"], "dev_exact_match": metrics["exact_match"],
                "seconds": time.time() - epoch_start})
            history.flush()
            key = (metrics["cer"], -metrics["exact_match"])
            if key < best_key:
                best_key, best_epoch, stale = key, epoch, 0
                torch.save({"state_dict": model.state_dict(), "config": cfg,
                            "epoch": epoch, "dev_metrics": metrics}, run_dir / "checkpoint_best.pt")
                with (run_dir / "predictions_dev.jsonl").open("w", encoding="utf-8") as f:
                    for row in predictions:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                save_json(run_dir / "metrics_dev.json", metrics)
            else:
                stale += 1
            save_json(run_dir / "progress_summary.json", {"status": "running", "epoch": epoch,
                "epochs": int(cfg["epochs"]), "best_epoch": best_epoch,
                "best_dev_cer": best_key[0], "best_dev_exact_match": -best_key[1], "updated_at": time.time()})
            if stale >= int(cfg.get("patience", 10)):
                break
    finally:
        history.close()
    ckpt = run_dir / "checkpoint_best.pt"
    if not ckpt.exists():
        raise RuntimeError("no checkpoint was produced")
    result = {"status": "completed", "best_epoch": best_epoch, "best_dev_cer": best_key[0],
        "best_dev_exact_match": -best_key[1], "params": params, "runtime_seconds": time.time() - start,
        "peak_vram_bytes": torch.cuda.max_memory_allocated(), "checkpoint_sha256": sha256(ckpt),
        "predictions_sha256": sha256(run_dir / "predictions_dev.jsonl"), "finished_at": time.time()}
    save_json(run_dir / "summary.json", result)
    save_json(run_dir / "progress_summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.config, args.run_dir), indent=2))
    except Exception as error:
        if args.run_dir.exists():
            save_json(args.run_dir / "progress_summary.json", {"status": "failed",
                "error": repr(error), "traceback": traceback.format_exc(), "finished_at": time.time()})
        raise


if __name__ == "__main__":
    main()
