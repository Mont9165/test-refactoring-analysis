"""RQ1 re-investigation: rebuild the Table-4 distribution from the verified
RefactoringMiner 3.0.0 run (general refactorings counted in TEST FILES, the
RQ1 construct), keeping the manual test-refactoring side unchanged.

Outputs the corrected cells, prevalence/co-occurrence rates, and Spearman rho
between per-commit test and general counts.
"""
import csv
import json
import re
from pathlib import Path

from rm_runner import REPO_ROOT, JSONS, is_test_path

SHA_RE = re.compile(r"commit/([0-9a-f]+)")


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den


def general_in_tests_count(sha):
    data = json.loads((JSONS / f"{sha}.json").read_text())
    n = 0
    for c in data.get("commits", []):
        for ref in c.get("refactorings", []):
            paths = {loc.get("filePath") for side in ("leftSideLocations", "rightSideLocations")
                     for loc in ref.get(side, []) or [] if loc.get("filePath")}
            if any(is_test_path(p) for p in paths):
                n += 1
    return n


def main():
    rq1 = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq1/output"
    test_counts = {}
    for r in csv.DictReader(open(rq1 / "test/test_refactoring_per_commit.csv", encoding="utf-8-sig")):
        sha = SHA_RE.search(r["url"]).group(1)
        test_counts[sha] = float(r["refactoring_count"])

    universe = {}
    ann = REPO_ROOT / "4_manual_inspection/src/refactoring_data_2025-02-19.csv"
    for r in csv.DictReader(open(ann, encoding="utf-8-sig")):
        m = SHA_RE.search((r.get("url") or ""))
        if m:
            universe[m.group(1)] = True
    shas = sorted(universe)
    print(f"universe: {len(shas)} commits")

    gen = {s: general_in_tests_count(s) for s in shas}
    t = {s: test_counts.get(s, 0) for s in shas}

    both = sum(1 for s in shas if t[s] > 0 and gen[s] > 0)
    test_only = sum(1 for s in shas if t[s] > 0 and gen[s] == 0)
    gen_only = sum(1 for s in shas if t[s] == 0 and gen[s] > 0)
    neither = sum(1 for s in shas if t[s] == 0 and gen[s] == 0)
    n = len(shas)
    print(f"Test only {test_only} ({100*test_only/n:.1f}%) | General only {gen_only} ({100*gen_only/n:.1f}%) | "
          f"Both {both} ({100*both/n:.1f}%) | Neither {neither} ({100*neither/n:.1f}%)")
    ntest, ngen = test_only + both, gen_only + both
    print(f"test prevalence {ntest}/{n} = {100*ntest/n:.1f}% | general prevalence {ngen}/{n} = {100*ngen/n:.1f}%")
    print(f"of test commits, with general: {both}/{ntest} = {100*both/ntest:.1f}%")
    print(f"of general commits, with test: {both}/{ngen} = {100*both/ngen:.1f}%")
    rho = spearman([t[s] for s in shas], [gen[s] for s in shas])
    print(f"Spearman rho (per-commit counts, n={n}): {rho:.3f}")


if __name__ == "__main__":
    main()
