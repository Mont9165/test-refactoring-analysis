"""B2 (Reviewer R3-5): Re-render Figures 4 / 5 from this paper to show
*absolute counts* alongside percentages, so readers can judge whether
small-n smells are driving the apparent rates.

Reads `change_patterns_{file,method}.csv` (already produced by
0_descriptive_analysis.py) and emits two new PDFs:
  change_patterns_{file,method}_with_counts.pdf

Each row carries an annotation "(n=<total>; +<imp>/-<deg>/=<noch>)"
so the per-smell sample sizes are visible.

Usage:
    python redo_change_patterns_with_counts.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent


def render(level: str) -> None:
    csv_path = THIS_DIR / f"change_patterns_{level}.csv"
    if not csv_path.exists():
        print(f"[skip] {csv_path} not found")
        return
    df = pd.read_csv(csv_path)
    df = df[df["test_smell"] != "NumberOfMethods"]
    df = df.sort_values("improvement_rate", ascending=False).reset_index(drop=True)

    y = np.arange(len(df))
    no_changes = df["no_change_rate"].values
    improvements = df["improvement_rate"].values
    degradations = df["degradation_rate"].values
    smells = df["test_smell"].values
    totals = df["total_pairs"].values
    imp_count = df["improvements"].values
    deg_count = df["degradations"].values
    nc_count = df["no_changes"].values

    color_nc = "#bdbdbd"
    color_imp = "#4daf4a"
    color_deg = "#e41a1c"

    fig, ax = plt.subplots(figsize=(13, 9))
    ax.barh(y, no_changes, color=color_nc, label="No Change")
    ax.barh(y, improvements, left=no_changes, color=color_imp, label="Improvements")
    ax.barh(y, degradations, left=no_changes + improvements, color=color_deg, label="Degradations")

    # y-axis labels: smell name + (n=...; +imp/-deg/=nc) on a second line.
    labels = [
        f"{smell}\n(n={t}; +{i}/−{d}/={n})"
        for smell, t, i, d, n in zip(smells, totals, imp_count, deg_count, nc_count)
    ]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Percentage of paired commits (%)", fontsize=12)
    ax.tick_params(axis="x", labelsize=11)
    ax.legend(loc="lower right", fontsize=11)

    # Add text annotations at the right edge with absolute counts.
    for i_y, (t, imp, deg, nc) in enumerate(zip(totals, imp_count, deg_count, nc_count)):
        ax.text(101, i_y, f" total {t}", va="center", fontsize=9, color="#444")

    ax.set_xlim(0, 115)
    plt.tight_layout()
    out = THIS_DIR / f"change_patterns_{level}_with_counts.pdf"
    fig.savefig(out, dpi=300)
    out_png = THIS_DIR / f"change_patterns_{level}_with_counts.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
    print(f"[done] {out}")
    print(f"[done] {out_png}")


def main() -> int:
    for lvl in ("file", "method"):
        render(lvl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
