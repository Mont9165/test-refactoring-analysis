"""R2-6: compute Cohen's kappa + per-type precision from two raters'
independent labels of the RM test-file detection sample.

Inputs:
  - manual_validation_sample_rater_a.csv (filled by rater A)
  - manual_validation_sample_rater_b.csv (filled by rater B)
  Both CSVs have identical row order. Annotators fill `is_correct`
  ('Y' / 'N') and optional `correct_type` / `notes`.

Outputs:
  - rm_sensitivity_summary.csv : merged labels + per-row consensus
  - rm_per_type_precision.csv  : precision (Y / total) per rm_type
  - prints Cohen's kappa on `is_correct`

Usage:
    python compute_kappa.py
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
A = THIS_DIR / "manual_validation_sample_rater_a.csv"
B = THIS_DIR / "manual_validation_sample_rater_b.csv"


def normalise_y(v: str) -> str:
    v = (v or "").strip().lower()
    if v in ("y", "yes", "true", "1", "correct"):
        return "Y"
    if v in ("n", "no", "false", "0", "incorrect"):
        return "N"
    return ""  # blank / not yet coded


def cohen_kappa(labels_a: list[str], labels_b: list[str]) -> tuple[float, int, int]:
    """Cohen's kappa for binary {Y, N} labels. Skips rows where either
    label is blank. Returns (kappa, n_paired, n_agree)."""
    pairs = [(a, b) for a, b in zip(labels_a, labels_b) if a in ("Y", "N") and b in ("Y", "N")]
    n = len(pairs)
    if n == 0:
        return float("nan"), 0, 0
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    counts_a = Counter(p[0] for p in pairs)
    counts_b = Counter(p[1] for p in pairs)
    pe = sum((counts_a[c] / n) * (counts_b[c] / n) for c in ("Y", "N"))
    if pe >= 1.0:
        return float("nan"), n, agree
    kappa = (po - pe) / (1 - pe)
    return kappa, n, agree


def main() -> int:
    if not A.exists() or not B.exists():
        print(f"[error] missing rater CSV(s); expected {A.name} and {B.name}")
        return 1
    rows_a = list(csv.DictReader(A.open(encoding="utf-8")))
    rows_b = list(csv.DictReader(B.open(encoding="utf-8")))
    if len(rows_a) != len(rows_b):
        print(f"[warn] row count mismatch: A={len(rows_a)} B={len(rows_b)}")

    n = min(len(rows_a), len(rows_b))
    labels_a = [normalise_y(rows_a[i].get("is_correct", "")) for i in range(n)]
    labels_b = [normalise_y(rows_b[i].get("is_correct", "")) for i in range(n)]

    kappa, paired, agree = cohen_kappa(labels_a, labels_b)
    print(f"[kappa] rows={n}, paired (both labelled)={paired}, agree={agree}")
    if paired:
        print(f"[kappa] Cohen's kappa (binary Y/N) = {kappa:.3f}")
        print(f"[kappa] raw agreement = {agree}/{paired} = {100*agree/paired:.1f}%")

    # Merge view + reconciled label (= Y if both Y, N if both N, '?' otherwise).
    merged: list[dict] = []
    disagreements = 0
    for i in range(n):
        a = labels_a[i]
        b = labels_b[i]
        reconciled = a if a == b and a in ("Y", "N") else "?"
        if a != b and a in ("Y", "N") and b in ("Y", "N"):
            disagreements += 1
        row = dict(rows_a[i])
        row["rater_a_is_correct"] = a
        row["rater_b_is_correct"] = b
        row["rater_a_correct_type"] = rows_a[i].get("correct_type", "")
        row["rater_b_correct_type"] = rows_b[i].get("correct_type", "")
        row["rater_a_notes"] = rows_a[i].get("notes", "")
        row["rater_b_notes"] = rows_b[i].get("notes", "")
        row["reconciled_is_correct"] = reconciled
        merged.append(row)

    print(f"[reconcile] disagreements requiring discussion: {disagreements}")

    out_summary = THIS_DIR / "rm_sensitivity_summary.csv"
    with out_summary.open("w", newline="", encoding="utf-8") as f:
        # Use union of keys
        keys = list(rows_a[0].keys()) + [
            "rater_a_is_correct", "rater_b_is_correct",
            "rater_a_correct_type", "rater_b_correct_type",
            "rater_a_notes", "rater_b_notes",
            "reconciled_is_correct",
        ]
        seen = []
        for k in keys:
            if k not in seen:
                seen.append(k)
        w = csv.DictWriter(f, fieldnames=seen, extrasaction="ignore")
        w.writeheader()
        for r in merged:
            w.writerow(r)
    print(f"[done] {out_summary}")

    # Per-type precision using reconciled_is_correct (Y means RM was correct).
    per_type_total: defaultdict = defaultdict(int)
    per_type_correct: defaultdict = defaultdict(int)
    per_type_disagree: defaultdict = defaultdict(int)
    for r in merged:
        t = r.get("rm_type", "")
        rec = r.get("reconciled_is_correct", "")
        per_type_total[t] += 1
        if rec == "Y":
            per_type_correct[t] += 1
        if rec == "?":
            per_type_disagree[t] += 1
    out_prec = THIS_DIR / "rm_per_type_precision.csv"
    with out_prec.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rm_type", "n_in_sample", "n_correct", "n_disagree",
                    "precision_(reconciled_Y/total)"])
        for t in sorted(per_type_total):
            tot = per_type_total[t]
            cor = per_type_correct[t]
            dis = per_type_disagree[t]
            prec = (cor / tot) if tot else 0
            w.writerow([t, tot, cor, dis, f"{prec:.3f}"])
    print(f"[done] {out_prec}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
