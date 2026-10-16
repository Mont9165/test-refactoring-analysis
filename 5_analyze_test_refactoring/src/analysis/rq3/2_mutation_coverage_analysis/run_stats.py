"""Run Wilcoxon + Vargha-Delaney over the wide CSV.

Overall (per-metric) statistics use a self-contained EXACT two-sided
Wilcoxon signed-rank test: zero differences are dropped, |differences|
receive average (mid) ranks, and the null distribution of W+ is fully
enumerated over all 2^k sign assignments (k <= 22; normal approximation
with tie correction is used beyond that and flagged in the `test` column).
This matches the values reported in the response letter / paper and
replaces the earlier scipy asymptotic p-values, which disagreed with the
exact test near alpha (e.g. branch coverage: asymptotic 0.043 vs exact
0.0625 at k=5, where the exact test cannot reach significance at all).

The per-refactoring-type breakdown still uses the shared analyze_grouped_metrics
from ../../test.py (imported lazily; requires scipy).

Usage:
    python run_stats.py --wide /tmp/pit_pipeline/mutation_coverage_wide.csv
    python run_stats.py --wide ... --stratify-by recovery_layer_used_after
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent.parent  # .../analysis/
sys.path.insert(0, str(ANALYSIS_DIR))


def _exact_wilcoxon(diffs: list[float]) -> tuple[float, float, float, str]:
    """Exact two-sided Wilcoxon signed-rank p over non-zero diffs.

    Returns (p, W_plus, W_minus, method). Average ranks for tied |d|;
    exact enumeration of the W+ null distribution for k <= 22.
    """
    k = len(diffs)
    if k == 0:
        return float("nan"), 0.0, 0.0, "no-nonzero-pairs"
    absd = [abs(d) for d in diffs]
    order = sorted(range(k), key=lambda i: absd[i])
    ranks = [0.0] * k
    i = 0
    while i < k:
        j = i
        while j < k and absd[order[j]] == absd[order[i]]:
            j += 1
        r = (i + 1 + j) / 2.0
        for t in range(i, j):
            ranks[order[t]] = r
        i = j
    w_plus = sum(ranks[i] for i in range(k) if diffs[i] > 0)
    w_minus = sum(ranks[i] for i in range(k) if diffs[i] < 0)
    if k <= 22:
        # DP over doubled ranks so half-integer midranks stay integral.
        dbl = [int(round(2 * r)) for r in ranks]
        dist: dict[int, int] = {0: 1}
        for r in dbl:
            nxt: dict[int, int] = {}
            for s, c in dist.items():
                nxt[s] = nxt.get(s, 0) + c
                nxt[s + r] = nxt.get(s + r, 0) + c
            dist = nxt
        total = 2 ** k
        w_min2 = int(round(2 * min(w_plus, w_minus)))
        tail = sum(c for s, c in dist.items() if s <= w_min2)
        p = min(1.0, 2.0 * tail / total)
        return p, w_plus, w_minus, "exact_midranks_zero_drop"
    # fallback: normal approximation with tie correction
    import math
    mu = k * (k + 1) / 4.0
    tie_term = 0.0
    seen: dict[float, int] = {}
    for r in ranks:
        seen[r] = seen.get(r, 0) + 1
    for cnt in seen.values():
        tie_term += cnt ** 3 - cnt
    sigma = math.sqrt(k * (k + 1) * (2 * k + 1) / 24.0 - tie_term / 48.0)
    z = (min(w_plus, w_minus) - mu) / sigma if sigma else 0.0
    p = min(1.0, 2.0 * 0.5 * (1 + math.erf(z / math.sqrt(2))))
    return p, w_plus, w_minus, "normal_approx_tie_corrected"


def exact_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-metric exact Wilcoxon + Vargha-Delaney A12 = P(before > after)."""
    rows = []
    for col in df.columns:
        if not col.endswith("_before"):
            continue
        base = col[: -len("_before")]
        after_col = base + "_after"
        if after_col not in df.columns:
            continue
        sub = df[[col, after_col]].dropna()
        if sub.empty:
            continue
        before = sub[col].tolist()
        after = sub[after_col].tolist()
        n = len(before)
        diffs = [a - b for b, a in zip(before, after) if a != b]
        p, w_plus, w_minus, method = _exact_wilcoxon(diffs)
        num = sum(
            (1.0 if x > y else 0.5 if x == y else 0.0)
            for x in before
            for y in after
        )
        a12 = num / (n * n)
        rows.append({
            "metric": base,
            "n": n,
            "k_nonzero": len(diffs),
            "median_before": statistics.median(before),
            "median_after": statistics.median(after),
            "A12": a12,
            "p_value": p,
            "test": method,
        })
    return pd.DataFrame(rows)


def run_block(df, label: str, out_overall: Path | None, out_grouped: Path | None) -> None:
    """Run the overall + per-type analyses on a (possibly filtered) df."""
    print(f"\n========== {label}  (n={len(df)}) ==========")
    if df.empty:
        print("(empty stratum — skipping)")
        return
    print("\n=== Overall (exact paired Wilcoxon + Vargha-Delaney) ===")
    overall = exact_metrics(df)
    if overall is not None and not overall.empty:
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(overall)
        if out_overall:
            overall.to_csv(out_overall, index=False)
            print(f"[done] -> {out_overall}")
    else:
        print("(no metrics produced — check column naming)")

    print("\n=== Per refactoring type ===")
    try:
        from test import analyze_grouped_metrics  # noqa: E402 (lazy: needs scipy)
    except ImportError as exc:
        print(f"(skipping per-type breakdown: {exc})")
        return
    grouped = analyze_grouped_metrics(df)
    if grouped is not None and not grouped.empty:
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(grouped)
        if out_grouped:
            grouped.to_csv(out_grouped, index=False)
            print(f"[done] -> {out_grouped}")
    else:
        print("(no per-type metrics; missing type_name column or empty input)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wide", required=True, type=Path)
    ap.add_argument("--out-overall", type=Path, default=None,
                    help="optional: write overall metrics CSV here")
    ap.add_argument("--out-grouped", type=Path, default=None,
                    help="optional: write per-type_name metrics CSV here")
    ap.add_argument("--stratify-by", default=None,
                    help="optional column name. Splits the input into Stratum A "
                         "(value == 'none') and Stratum B (everything else) and "
                         "reports per-stratum stats in addition to the overall.")
    args = ap.parse_args()

    df = pd.read_csv(args.wide)
    print(f"[info] loaded {len(df)} rows, {len(df.columns)} columns")

    # Stratification column: capture BEFORE the non-numeric-pair filter drops it.
    stratum_series = None
    if args.stratify_by and args.stratify_by in df.columns:
        stratum_series = df[args.stratify_by].copy()

    # Drop non-numeric *_before/*_after pairs (e.g., sha_before/sha_after) so
    # analyze_metrics doesn't try to subtract strings.
    keep_cols = []
    drop_pairs = []
    for col in df.columns:
        if col.endswith("_before"):
            base = col[:-len("_before")]
            after_col = base + "_after"
            if after_col in df.columns and not (
                pd.api.types.is_numeric_dtype(df[col])
                and pd.api.types.is_numeric_dtype(df[after_col])
            ):
                drop_pairs.append((col, after_col))
                continue
        keep_cols.append(col)
    if drop_pairs:
        print(f"[info] dropping non-numeric pairs: {drop_pairs}")
    df = df[keep_cols]

    if args.stratify_by:
        if stratum_series is None:
            print(f"[error] --stratify-by column '{args.stratify_by}' not in CSV")
            return 1
        # Stratum A = baseline (no recovery needed)
        a_mask = stratum_series.astype(str).str.lower().isin(["none", "nan", ""])
        a = df[a_mask]
        b = df[~a_mask]
        run_block(df, "ALL (combined)", args.out_overall, args.out_grouped)
        out_a_overall = (args.out_overall.with_suffix(".stratumA.csv")
                         if args.out_overall else None)
        out_b_overall = (args.out_overall.with_suffix(".stratumB.csv")
                         if args.out_overall else None)
        run_block(a, "Stratum A — original / no recovery", out_a_overall, None)
        run_block(b, "Stratum B — recovery required",      out_b_overall, None)
    else:
        run_block(df, "ALL", args.out_overall, args.out_grouped)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
