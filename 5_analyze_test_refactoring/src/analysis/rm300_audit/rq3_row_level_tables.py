"""Regenerate the paper's Table 7 and Table 8 statistics from the CURRENT
dataset (file_level_wide.csv / method_level_wide.csv; 405 pairs each) at the
row level, and classify the ORIGINAL 136 no-refactoring commits (Section 9.1).

Method: per smell (or per refactoring-type x smell with n>=6), exact two-sided
Wilcoxon signed-rank on non-zero paired differences (k>=6), Benjamini-Hochberg
within each family, matched-pairs rank-biserial r = (W+ - W-)/(W+ + W-).
Improvement/degradation percentages are shares of the pairs at each level;
degradations include newly introduced smells.
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
W = run_stats._exact_wilcoxon

FILE_CSV = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/1_analyze_testsmell_diff/file_level_wide.csv"
METHOD_CSV = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/smells_result/method_level_wide.csv"


def bh(items):
    valid = [(k, p) for k, p in items if p == p]
    m = len(valid)
    out, prev = {}, 1.0
    for rank, (k, p) in enumerate(sorted(valid, key=lambda x: -x[1]), 0):
        adj = min(p * m / (m - rank), prev)
        prev = adj
        out[k] = adj
    return out


def stats(rows, smells):
    for s in smells:
        diffs, imp, deg = [], 0, 0
        for r in rows:
            d = float(r[f"{s}_after"] or 0) - float(r[f"{s}_before"] or 0)
            if d < 0:
                imp += 1
            elif d > 0:
                deg += 1
            if d != 0:
                diffs.append(d)
        if len(diffs) >= 6:
            p, wp, wm, _ = W(diffs)
            rb = (wp - wm) / (wp + wm) if wp + wm else float("nan")
        else:
            p, rb = float("nan"), float("nan")
        yield dict(smell=s, n=len(rows), k=len(diffs), imp=imp, deg=deg, p=p, r=rb)


def table7():
    print("== Table 7 (overall, row level, BH q<0.05) ==")
    allr = []
    for label, path in (("File", FILE_CSV), ("Ref.", METHOD_CSV)):
        rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
        smells = sorted({c[:-7] for c in rows[0] if c.endswith("_before")})
        for r in stats(rows, smells):
            r["level"] = label
            allr.append(r)
    adj = bh([((r["level"], r["smell"]), r["p"]) for r in allr])
    for r in sorted(allr, key=lambda x: (x["level"], x["p"] if x["p"] == x["p"] else 9)):
        q = adj.get((r["level"], r["smell"]), float("nan"))
        if q == q and q < 0.05:
            print(f"  {r['level']:4s} {r['smell']:28s} imp {100*r['imp']/r['n']:5.1f}%  deg {100*r['deg']/r['n']:5.1f}%  "
                  f"p={r['p']:.3g}  q={q:.3g}  r={r['r']:+.2f}")


def table8():
    print("\n== Table 8 (per refactoring type x smell, row level, BH q<0.05) ==")
    allr = []
    for label, path in (("File", FILE_CSV), ("Ref.", METHOD_CSV)):
        rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
        smells = sorted({c[:-7] for c in rows[0] if c.endswith("_before")})
        by = defaultdict(list)
        for r in rows:
            by[r["type_name"]].append(r)
        for t, rr in by.items():
            if len(rr) < 6:
                continue
            for r in stats(rr, smells):
                r["level"], r["type"] = label, t
                allr.append(r)
    adj = bh([((r["level"], r["type"], r["smell"]), r["p"]) for r in allr])
    for r in sorted(allr, key=lambda x: (x["p"] if x["p"] == x["p"] else 9)):
        q = adj.get((r["level"], r["type"], r["smell"]), float("nan"))
        if q == q and q < 0.05:
            print(f"  {r['level']:4s} {r['type'][:26]:26s} {r['smell'][:26]:26s} n={r['n']:3d} "
                  f"imp {100*r['imp']/r['n']:5.1f}%  deg {100*r['deg']/r['n']:5.1f}%  p={r['p']:.3g}  q={q:.3g}  r={r['r']:+.2f}")


def classify_136():
    print("\n== Section 9.1: diff-structure classification of the original 136 ==")
    sha_re = re.compile(r"commit/([0-9a-f]+)")
    base = REPO_ROOT / "5_analyze_test_refactoring/src/analysis"
    test_pc, gen_pc = {}, {}
    for r in csv.DictReader(open(base / "rq1/output/test/test_refactoring_per_commit.csv", encoding="utf-8-sig")):
        test_pc[sha_re.search(r["url"]).group(1)] = float(r["refactoring_count"])
    for r in csv.DictReader(open(base / "rq1/output/general/general_refactoring_per_commit.csv", encoding="utf-8-sig")):
        gen_pc[r["commit_id"]] = float(r["refactoring_count"])
    univ = set()
    for r in csv.DictReader(open(REPO_ROOT / "4_manual_inspection/src/refactoring_data_2025-02-19.csv", encoding="utf-8-sig")):
        m = sha_re.search(r.get("url") or "")
        if m:
            univ.add(m.group(1))
    neither = [s for s in univ if test_pc.get(s, 0) == 0 and gen_pc.get(s, 0) == 0]
    cls = {r["sha"]: r for r in csv.DictReader(open(base / "rq3/no_refactor_classification.csv"))}
    cats = defaultdict(int)
    for s in neither:
        r = cls[s]
        nf, ntf = int(r["n_changed_files"]), int(r["n_test_files_changed"])
        ad, de = int(r["lines_added"]), int(r["lines_deleted"])
        if nf == 0:
            cats["diff_unavailable"] += 1
        elif ntf == 0:
            cats["name_matched_tooling_files"] += 1
        elif ad + de <= 5:
            cats["formatting_or_tiny_change"] += 1
        else:
            cats["test_changes_no_refactor"] += 1
    print(f"  neither set: {len(neither)} commits")
    for k, v in cats.items():
        print(f"  {k}: {v} ({100*v/len(neither):.1f}%)")


if __name__ == "__main__":
    table7()
    table8()
    classify_136()
