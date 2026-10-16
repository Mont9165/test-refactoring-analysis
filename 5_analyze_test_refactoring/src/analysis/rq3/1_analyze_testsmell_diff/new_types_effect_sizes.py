"""B1 (Reviewer R2-7): For each "New" test-specific refactoring type
(catalogued by this paper, not present in prior tools), report the
Wilcoxon signed-rank p-value + Vargha-Delaney A12 for the change in
each test smell.

Reads: file_level_wide.csv (canonical RQ3 set, 405 instances × 19 smells).
Writes: new_types_effect_sizes_{file,method}.csv with one row per
        (refactoring_type × smell) pair, only for the "New" types.

Usage:
    python new_types_effect_sizes.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent.parent  # .../analysis/
sys.path.insert(0, str(ANALYSIS_DIR))

from test import vargha_delaney_effect  # noqa: E402

# Canonical 37 - 16 cited = 21 "New" types we identified by cross-referencing
# the appendix "Ref" column with canonical CSV type_name values. The paper
# headlines "19 new types"; the +2 difference comes from try/catch ↔ annotation
# inverse-pair entries in the catalog. We report all 21 for transparency.
NEW_TYPES = {
    "Add Cleanup Method", "Add Conditional Annotation", "Await Event",
    "Change Assertion Type", "De-Parameterize Test", "Delete Mock Object",
    "Flaky Test Mitigation", "Grouping Tests", "Inline Assertion",
    "Lambdarize Method", "Merge Test Method", "Print to Assertion",
    "Replace Dependency with Test Double",
    "Replace annotation with assertThrow", "Replace annotation with try/catch",
    "Replace assertThrow with try/catch", "Replace try/catch with annotation",
    "Replace try/catch with asserThrows",
    "Split Parameterize Test", "Split Test Method",
    "Tuning Resources",
}


def analyse_per_type_per_smell(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    smells = sorted({c.replace("_before", "") for c in df.columns
                     if c.endswith("_before") and c.replace("_before", "") + "_after" in df.columns})
    for type_name, group in df.groupby("type_name"):
        if type_name not in NEW_TYPES:
            continue
        for smell in smells:
            b_col, a_col = f"{smell}_before", f"{smell}_after"
            paired = group[[b_col, a_col]].dropna(how="any")
            if len(paired) < 1:
                continue
            before = paired[b_col].astype(float)
            after = paired[a_col].astype(float)
            n = len(before)
            improved = int((after < before).sum())
            degraded = int((after > before).sum())
            unchanged = n - improved - degraded
            try:
                if (before == after).all():
                    p_value = float("nan")
                    stat = 0.0
                else:
                    stat, p_value = wilcoxon(before, after)
            except Exception:
                stat, p_value = float("nan"), float("nan")
            try:
                a12 = vargha_delaney_effect(before.values, after.values)
            except Exception:
                a12 = float("nan")
            rows.append({
                "refactoring_type": type_name,
                "smell": smell,
                "n": n,
                "improved": improved,
                "degraded": degraded,
                "unchanged": unchanged,
                "wilcoxon_stat": stat,
                "p_value": p_value,
                "A12": a12,
                "mean_diff": float((after - before).mean()),
                "median_diff": float((after - before).median()),
            })
    return pd.DataFrame(rows)


def main() -> int:
    here = Path(__file__).resolve().parent
    file_csv = here / "file_level_wide.csv"
    method_csv = here / "method_level_wide.csv"

    for label, src in (("file", file_csv), ("method", method_csv)):
        if not src.exists():
            print(f"[skip] {src} not found", file=sys.stderr)
            continue
        df = pd.read_csv(src, encoding="utf-8-sig")
        print(f"[{label}] loaded {len(df)} rows from {src.name}")
        out = analyse_per_type_per_smell(df)
        # sort: type then |effect|
        out["abs_a12_dist"] = (out["A12"] - 0.5).abs()
        out = out.sort_values(["refactoring_type", "abs_a12_dist"], ascending=[True, False])
        out = out.drop(columns=["abs_a12_dist"])
        out_path = here / f"new_types_effect_sizes_{label}.csv"
        out.to_csv(out_path, index=False)
        print(f"[{label}] {len(out)} (type,smell) rows -> {out_path}")
        # Summary: show types whose A12 deviates from 0.5 most
        movers = out[out["n"] >= 3].copy()
        movers["abs_a12_dist"] = (movers["A12"] - 0.5).abs()
        movers = movers.sort_values("abs_a12_dist", ascending=False).head(15)
        print(f"\n[{label}] top 15 (type, smell) effect-size signals (n>=3):")
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(movers[["refactoring_type", "smell", "n", "improved", "degraded", "p_value", "A12", "mean_diff"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
