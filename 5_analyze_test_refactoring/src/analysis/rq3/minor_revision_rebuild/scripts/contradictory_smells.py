# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/scripts/contradictory_smells.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/scripts/contradictory_smells.py).
"""B3 (Reviewer R3-5): Quantify contradictory test-smell pairs.

R3-5 calls out smell pairs that, by design, trade off against each other
— e.g., resolving Mystery Guest by inlining the resource creates Long
Setup; resolving Long Setup by extracting helpers may produce Mystery
Guest. We test this empirically: for each candidate pair, do the
direction of change correlate negatively across paired commits?

Reads file_level_wide.csv (and method_level_wide.csv) and emits a CSV +
text summary per smell-pair: Spearman ρ on the per-commit Δ(smell A) vs
Δ(smell B) and the joint counts of "A↑ B↓ / A↓ B↑ / both ↓ / both ↑".

Usage:
    python contradictory_smells.py
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

import sys
RQ3_DIR = Path(sys.argv[1])   # PATCH: data dir
THIS_DIR = Path(sys.argv[2])  # PATCH: output dir

# Pairs reviewers and prior literature flag as potentially contradictory.
# We evaluate every pair empirically and report the strongest negative
# correlations regardless of theoretical labelling.
CANDIDATE_PAIRS = [
    ("Mystery Guest", "General Fixture"),
    ("Mystery Guest", "Eager Test"),
    ("Eager Test", "Lazy Test"),
    ("Verbose Test", "Lazy Test"),
    ("Verbose Test", "Mystery Guest"),
    ("Assertion Roulette", "Lazy Test"),
    ("Conditional Test Logic", "Duplicate Assert"),
    ("Magic Number Test", "Mystery Guest"),
    ("Magic Number Test", "General Fixture"),
    ("Sensitive Equality", "Magic Number Test"),
]


def per_pair_stats(df: pd.DataFrame, smell_a: str, smell_b: str) -> dict | None:
    a_b, a_a = f"{smell_a}_before", f"{smell_a}_after"
    b_b, b_a = f"{smell_b}_before", f"{smell_b}_after"
    if not all(c in df.columns for c in (a_b, a_a, b_b, b_a)):
        return None
    paired = df[[a_b, a_a, b_b, b_a]].dropna(how="any")
    if paired.empty:
        return None
    delta_a = paired[a_a].astype(float) - paired[a_b].astype(float)
    delta_b = paired[b_a].astype(float) - paired[b_b].astype(float)
    n = len(paired)
    a_up_b_down = int(((delta_a > 0) & (delta_b < 0)).sum())
    a_down_b_up = int(((delta_a < 0) & (delta_b > 0)).sum())
    both_down = int(((delta_a < 0) & (delta_b < 0)).sum())
    both_up = int(((delta_a > 0) & (delta_b > 0)).sum())
    no_change = n - a_up_b_down - a_down_b_up - both_down - both_up
    try:
        rho, p = spearmanr(delta_a, delta_b)
    except Exception:
        rho, p = float("nan"), float("nan")
    return {
        "smell_a": smell_a,
        "smell_b": smell_b,
        "n_paired_commits": n,
        "spearman_rho": rho,
        "p_value": p,
        "a_up_b_down": a_up_b_down,
        "a_down_b_up": a_down_b_up,
        "both_down": both_down,
        "both_up": both_up,
        "either_unchanged": no_change,
    }


def all_pairs_stats(df: pd.DataFrame) -> pd.DataFrame:
    smells = sorted({c.replace("_before", "") for c in df.columns
                     if c.endswith("_before") and c != "NumberOfMethods_before"})
    rows = []
    for a, b in combinations(smells, 2):
        s = per_pair_stats(df, a, b)
        if s:
            rows.append(s)
    return pd.DataFrame(rows)


def main() -> int:
    for label in ("file", "method"):
        src = RQ3_DIR / f"{label}_level_wide.csv"
        if not src.exists():
            continue
        df = pd.read_csv(src, encoding="utf-8-sig")

        # All pairs (for response letter table)
        all_df = all_pairs_stats(df)
        all_df = all_df.sort_values("spearman_rho")  # most negative first
        out_all = THIS_DIR / f"contradictory_smells_{label}_all.csv"
        all_df.to_csv(out_all, index=False)
        print(f"[{label}] {len(all_df)} smell-pairs -> {out_all}")
        print(f"\n[{label}] top 10 negatively correlated pairs (most contradictory):")
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(all_df.head(10)[
                ["smell_a", "smell_b", "n_paired_commits",
                 "a_up_b_down", "a_down_b_up", "both_down", "both_up",
                 "spearman_rho", "p_value"]
            ])

        # Annotated curated pairs (the ones reviewers explicitly mentioned).
        curated_rows = [per_pair_stats(df, a, b) for a, b in CANDIDATE_PAIRS]
        curated_rows = [r for r in curated_rows if r]
        cur_df = pd.DataFrame(curated_rows)
        out_cur = THIS_DIR / f"contradictory_smells_{label}_curated.csv"
        cur_df.to_csv(out_cur, index=False)
        print(f"\n[{label}] curated pairs -> {out_cur}")
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(cur_df)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
