"""Step 3: residue audit on the canonical 208-commit set (Section 9.1 of the paper).

Reproduces:
  - 208 commits = 366 valid commits minus the 158 with a confirmed test
    refactoring;
  - RM 3.0.0 detects general-purpose refactorings in TEST FILES in 122 of
    them (58.7%), versus 72 recorded by the original collection run
    (= the general-only cell of the RQ1 distribution table);
  - the remaining 86 commits: 64.0% test maintenance, 20.9% formatting or
    very small changes, 15.1% production-only changes.

Diff statistics per commit are taken from rq3/no_refactor_classification.csv
(produced by rq3/classify_no_refactor_commits.py).
"""
import csv
import json
import re

from rm_runner import REPO_ROOT, JSONS, is_test_path

RQ1_OUT = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq1/output"
ANN_CSV = REPO_ROOT / "4_manual_inspection/src/refactoring_data_2025-02-19.csv"
CLS_CSV = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/no_refactor_classification.csv"
SHA_RE = re.compile(r"commit/([0-9a-f]+)")


def fresh_general_in_tests(sha):
    data = json.loads((JSONS / f"{sha}.json").read_text())
    for c in data.get("commits", []):
        for ref in c.get("refactorings", []):
            for side in ("leftSideLocations", "rightSideLocations"):
                for loc in ref.get(side, []) or []:
                    if is_test_path(loc.get("filePath", "")):
                        return True
    return False


def main():
    test_pc = set()
    for r in csv.DictReader(open(RQ1_OUT / "test/test_refactoring_per_commit.csv", encoding="utf-8-sig")):
        if float(r["refactoring_count"]) > 0:
            test_pc.add(SHA_RE.search(r["url"]).group(1))
    gen_pc = {r["commit_id"]
              for r in csv.DictReader(open(RQ1_OUT / "general/general_refactoring_per_commit.csv", encoding="utf-8-sig"))
              if float(r["refactoring_count"]) > 0}

    universe = set()
    for r in csv.DictReader(open(ANN_CSV, encoding="utf-8-sig")):
        m = SHA_RE.search((r.get("url") or ""))
        if m:
            universe.add(m.group(1))
    print(f"valid universe: {len(universe)}; canonical test commits: {len(test_pc)}")

    no_test = sorted(universe - test_pc)
    print(f"canonical no-test set: {len(no_test)}  (= {len(universe)} - {len(test_pc)})")

    fresh = [s for s in no_test if fresh_general_in_tests(s)]
    orig = [s for s in no_test if s in gen_pc]
    neither = [s for s in no_test if s not in set(fresh)]
    print(f"RM 3.0.0 finds test-file general refactorings in {len(fresh)} "
          f"({100*len(fresh)/len(no_test):.1f}%); original run recorded {len(orig)}")
    print(f"overlap {len(set(fresh)&set(orig))}, fresh-only {len(set(fresh)-set(orig))}, "
          f"orig-only {len(set(orig)-set(fresh))}")
    print(f"neither (no refactoring in test code): {len(neither)}")

    cls = {r["sha"]: r for r in csv.DictReader(open(CLS_CSV))}
    cats = {"diff_unavailable": 0, "production_only_changes": 0,
            "formatting_or_tiny_change": 0, "test_changes_no_refactor": 0}
    for s in neither:
        r = cls[s]
        nf, ntf = int(r["n_changed_files"]), int(r["n_test_files_changed"])
        ad, de = int(r["lines_added"]), int(r["lines_deleted"])
        if nf == 0:
            cats["diff_unavailable"] += 1
        elif ntf == 0:
            cats["production_only_changes"] += 1
        elif ad + de <= 5:
            cats["formatting_or_tiny_change"] += 1
        else:
            cats["test_changes_no_refactor"] += 1
    for k, v in cats.items():
        print(f"  {k}: {v} ({100*v/len(neither):.1f}%)")


if __name__ == "__main__":
    main()
