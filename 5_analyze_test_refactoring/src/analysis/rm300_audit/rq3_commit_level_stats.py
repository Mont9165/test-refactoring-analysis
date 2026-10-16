"""RQ3 re-investigation: recompute the Table-7/Table-8 statistics from the
CURRENT dataset (file_level_wide.csv, 405 rows / 158 commits) at the COMMIT
level, removing the pseudo-replication of multiple file rows per commit.

For each smell (and each refactoring-type subgroup), before/after counts are
summed per commit; improvements/degradations are counted per commit; the exact
two-sided Wilcoxon signed-rank test (midranks, zero-drop; k>=6 rule) is run on
the per-commit differences with Benjamini--Hochberg correction; matched-pairs
rank-biserial r = (W+ - W-)/(W+ + W-) is reported.
"""
import csv
import importlib.util
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]

spec = importlib.util.spec_from_file_location(
    "run_stats", REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/2_mutation_coverage_analysis/run_stats.py")
run_stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_stats)
exact_wilcoxon = run_stats._exact_wilcoxon

FLW = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/1_analyze_testsmell_diff/file_level_wide.csv"


def load():
    rows = list(csv.DictReader(open(FLW, encoding="utf-8-sig")))
    smells = sorted({c[:-7] for c in rows[0] if c.endswith("_before")})
    per = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))  # commit -> smell -> [b,a]
    types = defaultdict(set)                                    # commit -> set(type)
    for r in rows:
        u = r["commit_url"]
        types[u].add(r["type_name"])
        for s in smells:
            b = float(r[f"{s}_before"] or 0)
            a = float(r[f"{s}_after"] or 0)
            per[u][s][0] += b
            per[u][s][1] += a
    return per, types, smells


def bh(pairs):
    """pairs: list of (key, p). Returns dict key -> BH-adjusted p."""
    valid = [(k, p) for k, p in pairs if p == p]
    m = len(valid)
    out = {}
    prev = 1.0
    for rank, (k, p) in enumerate(sorted(valid, key=lambda x: -x[1]), 0):
        adj = min(p * m / (m - rank), prev)
        prev = adj
        out[k] = adj
    return out


def analyse(per, commits, smells, label, min_k=6):
    results = []
    for s in smells:
        diffs = []
        imp = deg = 0
        for u in commits:
            b, a = per[u][s]
            d = a - b
            if d < 0:
                imp += 1
            elif d > 0:
                deg += 1
            if d != 0:
                diffs.append(d)
        if len(diffs) >= min_k:
            p, wp, wm, _ = exact_wilcoxon(diffs)
            r = (wp - wm) / (wp + wm) if (wp + wm) else float("nan")
        else:
            p, r = float("nan"), float("nan")
        results.append(dict(group=label, smell=s, n=len(commits), k=len(diffs),
                            imp=imp, deg=deg, p=p, r=r))
    return results


def main():
    per, types, smells = load()
    commits = sorted(per)
    print(f"{len(commits)} commits, {len(smells)} metrics\n")

    # ---- Table 7': overall per-smell, commit level ----
    res = analyse(per, commits, smells, "ALL")
    adj = bh([(r_["smell"], r_["p"]) for r_ in res])
    print("== Overall (commit level, n=158, BH over metrics) ==")
    for r_ in sorted(res, key=lambda x: (x["p"] if x["p"] == x["p"] else 9)):
        q = adj.get(r_["smell"], float("nan"))
        if q == q and q < 0.10:
            print(f"  {r_['smell']:28s} imp {r_['imp']:3d} ({100*r_['imp']/158:4.1f}%)  "
                  f"deg {r_['deg']:3d} ({100*r_['deg']/158:4.1f}%)  k={r_['k']:3d}  "
                  f"p={r_['p']:.4g}  BH q={q:.4g}  r={r_['r']:+.2f}")

    # ---- Table 8': per refactoring type x smell ----
    by_type = defaultdict(list)
    for u, ts in types.items():
        for t in ts:
            by_type[t].append(u)
    all_res = []
    for t, cs in sorted(by_type.items()):
        if len(cs) < 6:
            continue
        all_res += analyse(per, cs, smells, t)
    adj = bh([((r_["group"], r_["smell"]), r_["p"]) for r_ in all_res])
    print("\n== Per type x smell (commit level, n>=6 commits, BH over all pairs) ==")
    for r_ in sorted(all_res, key=lambda x: (x["p"] if x["p"] == x["p"] else 9)):
        q = adj.get((r_["group"], r_["smell"]), float("nan"))
        if q == q and q < 0.10:
            print(f"  {r_['group'][:26]:26s} x {r_['smell'][:24]:24s} n={r_['n']:2d} k={r_['k']:2d} "
                  f"imp={r_['imp']:2d} deg={r_['deg']:2d} p={r_['p']:.4g} BH q={q:.4g} r={r_['r']:+.2f}")

    # focus rows for comparison with old claims (regardless of significance)
    print("\n== Focus: Split Test Method / Grouping Tests (commit level) ==")
    for t in ("Split Test Method", "Grouping Tests"):
        cs = by_type.get(t, [])
        for r_ in analyse(per, cs, smells, t):
            if r_["smell"] in ("Duplicate Assert", "Magic Number Test", "Mystery Guest",
                               "Sensitive Equality", "NumberOfMethods") and r_["k"] > 0:
                print(f"  {t:18s} x {r_['smell'][:22]:22s} n={r_['n']:2d} k={r_['k']:2d} "
                      f"imp={r_['imp']:2d} deg={r_['deg']:2d} p={r_['p']:.4g} r={r_['r']:+.2f}")


if __name__ == "__main__":
    main()
