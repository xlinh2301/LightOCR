"""Zero-shot inference adapter for PaddleX/PaddleOCR recognition modules.

This script intentionally reads only a sample-ID split and image directories.
Labels are loaded later by verify_predictions.py so they cannot affect inference.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import time
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_ids(split_file: Path) -> list[str]:
    ids = []
    for line_no, line in enumerate(split_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        sid = Path(str(row["sample_id"])).name
        if sid in ids:
            raise ValueError(f"duplicate sample_id at line {line_no}: {sid}")
        ids.append(sid)
    if not ids:
        raise ValueError(f"empty split: {split_file}")
    return ids


def resolve_images(ids: list[str], image_roots: list[Path]) -> list[Path]:
    paths, missing, ambiguous = [], [], []
    for sid in ids:
        matches = [root / sid for root in image_roots if (root / sid).is_file()]
        if not matches:
            missing.append(sid)
        elif len(matches) > 1:
            ambiguous.append(sid)
        else:
            paths.append(matches[0])
    if missing or ambiguous:
        raise FileNotFoundError(json.dumps({"missing": missing[:20], "missing_n": len(missing),
                                           "ambiguous": ambiguous[:20], "ambiguous_n": len(ambiguous)}))
    return paths


def unpack_result(result) -> dict:
    value = getattr(result, "json", None)
    if callable(value):
        value = value()
    if value is None:
        value = result
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise TypeError(f"unexpected PaddleX result type: {type(value).__name__}")
    if isinstance(value.get("res"), dict):
        value = value["res"]
    text = value.get("rec_text")
    score = value.get("rec_score")
    if text is None:
        raise KeyError(f"PaddleX output does not contain rec_text: {value.keys()}")
    return {"prediction": str(text), "confidence": None if score is None else float(score),
            "raw_result": value}


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def model_files(model_name: str) -> list[dict]:
    """Hash only matching model-cache files, without copying or altering them."""
    roots = [Path.home() / ".paddlex", Path.home() / ".paddleocr"]
    found = []
    for root in roots:
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and model_name.lower() in str(path).lower():
                    found.append({"path": str(path), "size_bytes": path.stat().st_size,
                                  "sha256": sha256(path)})
    return found


def read_model_config(model_name: str) -> tuple[dict, list[Path]]:
    import yaml

    paths = [Path.home() / ".paddlex" / "official_models" / model_name / "inference.yml"]
    config_path = next((path for path in paths if path.is_file()), None)
    if config_path is None:
        return {}, []
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    preprocess = config.get("PreProcess", {})
    postprocess = config.get("PostProcess", {})
    chars = postprocess.get("character_dict", []) if isinstance(postprocess, dict) else []
    dict_blob = json.dumps(chars, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "inference_config_path": str(config_path),
        "inference_config_sha256": sha256(config_path),
        "preprocess_config": preprocess,
        "postprocess_name": postprocess.get("name") if isinstance(postprocess, dict) else None,
        "character_dictionary_size": len(chars),
        "character_dictionary_sha256": hashlib.sha256(dict_blob).hexdigest(),
    }, [config_path]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--split", required=True, type=Path)
    parser.add_argument("--image-root", required=True, type=Path, action="append",
                        help="Repeat for the audited crops/train and crops/valid directories.")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default="gpu:0")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--limit", type=int, default=None,
                        help="Optional prefix-only smoke run; never use its partial metrics for model selection.")
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {args.output_dir}")
    ids = load_ids(args.split)
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        ids = ids[:args.limit]
    paths = resolve_images(ids, args.image_root)

    from paddleocr import TextRecognition

    model = TextRecognition(model_name=args.model_name, device=args.device)
    start = time.perf_counter()
    rows = []
    for offset in range(0, len(paths), args.batch_size):
        batch_paths = paths[offset:offset + args.batch_size]
        results = model.predict(input=[str(p) for p in batch_paths], batch_size=args.batch_size)
        batch_rows = [unpack_result(result) for result in results]
        if len(batch_rows) != len(batch_paths):
            raise RuntimeError(f"batch prediction count mismatch at {offset}: got {len(batch_rows)}, expected {len(batch_paths)}")
        rows.extend(batch_rows)
        print(f"inference_progress={len(rows)}/{len(paths)}", flush=True)
    elapsed = time.perf_counter() - start
    if len(rows) != len(ids):
        raise RuntimeError(f"prediction count mismatch: got {len(rows)}, expected {len(ids)}")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    model_config, config_paths = read_model_config(args.model_name)
    for config_path in config_paths:
        shutil.copy2(config_path, args.output_dir / config_path.name)
    prediction_path = args.output_dir / "predictions_dev.jsonl"
    with prediction_path.open("w", encoding="utf-8", newline="\n") as stream:
        for sid, path, output in zip(ids, paths, rows):
            stream.write(json.dumps({"sample_id": sid, "image_path": str(path),
                                     "prediction": output["prediction"],
                                     "confidence": output["confidence"],
                                     "raw_result": output["raw_result"]},
                                    ensure_ascii=False) + "\n")
    manifest = {
        "model_name": args.model_name,
        "model_source_url": args.source_url,
        "split_file": str(args.split),
        "split_sha256": sha256(args.split),
        "image_roots": [str(p) for p in args.image_root],
        "n_samples": len(ids),
        "partial_smoke_run": args.limit is not None,
        "inference_device": args.device,
        "batch_size": args.batch_size,
        "elapsed_seconds": elapsed,
        "mean_ms_per_sample": elapsed * 1000 / len(ids),
        "paddlepaddle_version": package_version("paddlepaddle-gpu") or package_version("paddlepaddle"),
        "paddleocr_version": package_version("paddleocr"),
        "paddlex_version": package_version("paddlex"),
        "checkpoint_files": model_files(args.model_name),
        "model_config": model_config,
        "predictions_sha256": sha256(prediction_path),
        "test_and_cross_data_read": False,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
