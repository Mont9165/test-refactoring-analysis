"""Compute taxonomy saturation curve from the manual annotation log.

Usage:
    python compute_saturation.py \
        --input ../../../../../4_manual_inspection/src/refactoring_data_2025-02-19.csv \
        --output-dir .
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_types_in_order(path: Path, exclude: set[str] | None = None) -> list[str]:
    exclude = exclude or set()
    rows = []
    with path.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                idx = int(r.get("order_index", "0"))
            except ValueError:
                idx = 0
            rows.append((r.get("experiment_title", ""), idx, r.get("type_name", "").strip()))
    rows.sort(key=lambda x: (x[0], x[1]))
    return [t for _, _, t in rows if t and t not in exclude]


def cumulative_distinct(types: list[str]) -> list[int]:
    seen: set[str] = set()
    out: list[int] = []
    for t in types:
        seen.add(t)
        out.append(len(seen))
    return out


def per_window_new_types(types: list[str], window: int = 100) -> list[int]:
    seen: set[str] = set()
    counts: list[int] = []
    new_in_window = 0
    for i, t in enumerate(types, 1):
        if t not in seen:
            new_in_window += 1
            seen.add(t)
        if i % window == 0:
            counts.append(new_in_window)
            new_in_window = 0
    if len(types) % window:
        counts.append(new_in_window)
    return counts


def bootstrap_band(types: list[str], n_samples: int = 1000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = random.Random(seed)
    n = len(types)
    samples = np.zeros((n_samples, n), dtype=int)
    base = list(types)
    for i in range(n_samples):
        order = base[:]
        rng.shuffle(order)
        samples[i] = cumulative_distinct(order)
    return np.percentile(samples, 2.5, axis=0), np.percentile(samples, 97.5, axis=0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--exclude-types", default="Non-Refactoring",
                    help="comma-separated type_name values to drop before computing "
                         "the curve (default: Non-Refactoring)")
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    exclude = {t.strip() for t in args.exclude_types.split(",") if t.strip()}
    types = load_types_in_order(args.input, exclude=exclude)
    if not types:
        raise SystemExit("no annotations found")
    cum = cumulative_distinct(types)
    ci_low, ci_high = bootstrap_band(types)
    per_window = per_window_new_types(types, args.window)

    csv_path = args.output_dir / "saturation_curve.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "distinct_types", "ci_low", "ci_high"])
        for i, n in enumerate(cum, 1):
            w.writerow([i, n, int(ci_low[i - 1]), int(ci_high[i - 1])])

    per_path = args.output_dir / "saturation_per_window.csv"
    with per_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["window_index", "window_size", "new_types_in_window"])
        for i, c in enumerate(per_window, 1):
            w.writerow([i, args.window, c])

    plt.figure(figsize=(7, 4))
    xs = np.arange(1, len(cum) + 1)
    plt.plot(xs, cum, label="observed order")
    plt.fill_between(xs, ci_low, ci_high, alpha=0.2, label="95% CI (random order)")
    plt.xlabel("Annotated instance index k")
    plt.ylabel("Distinct refactoring types")
    plt.title("Taxonomy saturation curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output_dir / "saturation_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.bar(range(1, len(per_window) + 1), per_window)
    plt.xlabel(f"Window (size={args.window})")
    plt.ylabel("New types discovered in window")
    plt.title("New types per fixed-size annotation window")
    plt.tight_layout()
    plt.savefig(args.output_dir / "saturation_per_window.png", dpi=200)
    plt.close()

    print(f"[done] excluded={sorted(exclude) or '(none)'}")
    print(f"[done] total instances={len(types)}, distinct types={cum[-1]}")
    print(f"[done] outputs in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
