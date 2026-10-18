"""Independently reconstruct model-dev OCR metrics and error cases from predictions."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def counts(reference: str, hypothesis: str):
    dp = [[0] * (len(hypothesis) + 1) for _ in range(len(reference) + 1)]
    for i in range(len(reference) + 1):
        dp[i][0] = i
    for j in range(len(hypothesis) + 1):
        dp[0][j] = j
    for i, a in enumerate(reference, 1):
        for j, b in enumerate(hypothesis, 1):
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + (a != b))
    i, j = len(reference), len(hypothesis)
    sub = deletion = insertion = 0
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1] + (reference[i-1] != hypothesis[j-1]):
            sub += reference[i-1] != hypothesis[j-1]
            i -= 1; j -= 1
        elif i and dp[i][j] == dp[i-1][j] + 1:
            deletion += 1; i -= 1
        else:
            insertion += 1; j -= 1
    return dp[-1][-1], sub, deletion, insertion


def reconstruct(prediction_file: Path, split_file: Path, labels_file: Path):
    expected = [Path(json.loads(line)["sample_id"]).name
                for line in split_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    labels = json.loads(labels_file.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in prediction_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {Path(row["sample_id"]).name: row for row in rows}
    duplicates = len(by_id) != len(rows)
    missing = sorted(set(expected) - set(by_id))
    unexpected = sorted(set(by_id) - set(expected))
    truth_mismatch = [sid for sid in set(expected) & set(by_id)
                      if by_id[sid].get("truth") != labels.get(sid)]
    if duplicates or missing or unexpected or truth_mismatch:
        raise ValueError(json.dumps({"duplicates": duplicates, "missing": missing,
            "unexpected": unexpected, "truth_mismatch": truth_mismatch}, indent=2))
    n = len(expected); chars = sub = deletion = insertion = exact = wrong_same = 0
    errors_by_length = Counter(); failures = []
    for sid in expected:
        row = by_id[sid]
        truth, pred = str(labels[sid]), str(row["prediction"])
        distance, s, d, ins = counts(truth, pred)
        chars += len(truth); sub += s; deletion += d; insertion += ins
        exact += truth == pred
        wrong_same += truth != pred and len(truth) == len(pred)
        errors_by_length[str(len(truth))] += distance
        if truth != pred:
            failures.append({"sample_id": sid, "truth": truth, "prediction": pred,
                "reference_length": len(truth), "prediction_length": len(pred),
                "edit_distance": distance, "substitutions": s, "deletions": d, "insertions": ins})
    metrics = {"n": n, "exact_count": exact, "exact_match": exact / max(n, 1),
        "cer": (sub + deletion + insertion) / max(chars, 1), "edits": sub + deletion + insertion,
        "reference_chars": chars, "substitutions": sub, "deletions": deletion, "insertions": insertion,
        "wrong_same_length_count": wrong_same, "wrong_same_length_rate": wrong_same / max(n, 1),
        "error_counts_by_truth_length": dict(errors_by_length), "predictions_reconstructed": True}
    failures.sort(key=lambda x: (-x["edit_distance"], x["sample_id"]))
    return metrics, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    metrics, failures = reconstruct(args.predictions, args.split, args.labels)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "metrics_reconstructed.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (args.output_dir / "failure_cases.jsonl").open("w", encoding="utf-8") as f:
        for row in failures:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
