"""R3-15: Classify the 136 commits where neither test refactoring nor general
refactoring was found, despite the commit message containing "test" + "refactor".

Inputs:
  - Manual annotation CSV (4_manual_inspection/src/refactoring_data_2025-02-19.csv)
    -> distinguishes test-refactor commits (real type) vs no-test-refactor.
  - RM JSON outputs (/tmp/rm_sensitivity/json/<sha>.json)
    -> distinguishes commits with general (RM-detected) refactoring vs none.
  - GitHub commit metadata (cached via gh API or cloned repos for diff stats).

Output:
  - no_refactor_commits.csv: one row per "no refactoring at all" commit with
    automatically-derived classification heuristics.
  - Summary stats printed to stdout.

Heuristic categories (assigned automatically; final labels need annotator review):
  - production_only_changes : commit modifies only production files (not test
    files), so the keyword filter caught a non-test commit.
  - formatting_only         : diff is dominated by whitespace / import changes
    (heuristic: low Java semantic-line count).
  - test_changes_no_refactor: commit modifies test files but RM detects no
    refactoring and our manual annotation also marks "Non-Refactoring".
  - keyword_false_positive  : commit message contains "test" and "refactor"
    but the changes are unrelated (e.g., "fixed test" + "refactor" in
    different sentences referring to different code).
  - other                   : couldn't classify automatically.

Usage:
    python classify_no_refactor_commits.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ANN_CSV = Path("/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/"
               "4_manual_inspection/src/refactoring_data_2025-02-19.csv")
RM_JSON_DIR = Path("/tmp/rm_sensitivity/json")
REPOS_DIR = Path("/tmp/pit_pipeline_v2/repos")

SKIP_TYPES = {"Non-Refactoring", "Any Refactoring", ""}
COMMIT_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})"
)
TEST_PATH_HINTS = ("/src/test/", "/tests/", "/test/")


def is_test_path(p: str) -> bool:
    pl = p.lower()
    if any(h in pl for h in TEST_PATH_HINTS):
        return True
    return p.endswith(("Test.java", "Tests.java", "IT.java", "ITCase.java"))


def parse_url(url: str):
    m = COMMIT_URL_RE.match(url.strip())
    if not m:
        return None
    return m["owner"], m["repo"], m["sha"]


def has_general_refactoring_in_test_files(rm_json: Path) -> tuple[bool, bool, int, int]:
    """Return (has_any_refactoring, has_test_file_refactoring, total, in_tests)."""
    if not rm_json.exists():
        return False, False, 0, 0
    try:
        data = json.loads(rm_json.read_text())
    except Exception:
        return False, False, 0, 0
    total = in_tests = 0
    for c in data.get("commits", []):
        for ref in c.get("refactorings", []):
            total += 1
            paths: set[str] = set()
            for side in ("leftSideLocations", "rightSideLocations"):
                for loc in ref.get(side, []) or []:
                    fp = loc.get("filePath")
                    if fp:
                        paths.add(fp)
            if any(is_test_path(p) for p in paths):
                in_tests += 1
    return total > 0, in_tests > 0, total, in_tests


def gh_diff_stats(repo_dir: Path, sha: str) -> tuple[int, int, int, int]:
    """Return (n_changed_files, n_test_files, n_added_lines, n_deleted_lines)."""
    if not repo_dir.exists():
        return 0, 0, 0, 0
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "show", "--numstat", "--format=", sha],
            text=True, timeout=30,
        )
    except Exception:
        return 0, 0, 0, 0
    files = test_files = added = deleted = 0
    for line in out.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        a, d, path = parts[0], parts[1], parts[2]
        files += 1
        if is_test_path(path):
            test_files += 1
        try:
            added += int(a)
            deleted += int(d)
        except ValueError:
            pass
    return files, test_files, added, deleted


def main() -> int:
    rows = list(csv.DictReader(ANN_CSV.open(encoding="utf-8-sig")))
    per_commit = defaultdict(set)
    for r in rows:
        per_commit[r["url"]].add(r["type_name"])

    no_test_refactor = [u for u, t in per_commit.items() if not (t - SKIP_TYPES)]
    print(f"[info] commits without test refactoring: {len(no_test_refactor)} of {len(per_commit)}")

    out_rows = []
    paper_136 = 0
    for url in no_test_refactor:
        parsed = parse_url(url)
        if not parsed:
            continue
        owner, repo, sha = parsed
        rm = has_general_refactoring_in_test_files(RM_JSON_DIR / f"{sha}.json")
        rm_any, rm_test, rm_total, rm_in_tests = rm
        repo_dir = REPOS_DIR / f"{owner}__{repo}"
        n_files, n_test_files, added, deleted = gh_diff_stats(repo_dir, sha)

        category = "other"
        if not rm_any:
            # Paper's "136 commits with no refactoring at all" set:
            paper_136 += 1
            if n_files == 0:
                category = "diff_unavailable"
            elif n_test_files == 0:
                category = "production_only_changes"
            elif added + deleted <= 5:
                category = "formatting_or_tiny_change"
            else:
                category = "test_changes_no_refactor"
        else:
            # Has general refactoring but no test refactoring — these are NOT
            # part of paper's "136" set; they're the "general-only" rows in
            # the RQ1 distribution table.
            category = "general_refactoring_only"

        out_rows.append({
            "commit_url": url,
            "owner": owner,
            "repo": repo,
            "sha": sha,
            "rm_total": rm_total,
            "rm_in_tests": rm_in_tests,
            "n_changed_files": n_files,
            "n_test_files_changed": n_test_files,
            "lines_added": added,
            "lines_deleted": deleted,
            "category": category,
        })

    out_csv = Path(__file__).resolve().parent / "no_refactor_classification.csv"
    fieldnames = list(out_rows[0].keys()) if out_rows else []
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"[done] {len(out_rows)} rows -> {out_csv}")

    # Summary
    from collections import Counter
    cat_counter = Counter(r["category"] for r in out_rows)
    print("\nCategory distribution (all 'no test refactoring' commits):")
    for cat, c in cat_counter.most_common():
        print(f"  {c:>4} {cat}")

    print(f"\n'no refactoring at all' (paper's 136 set candidate): {paper_136}")
    paper_rows = [r for r in out_rows if r["category"] != "general_refactoring_only"]
    paper_counter = Counter(r["category"] for r in paper_rows)
    print("Within that subset:")
    for cat, c in paper_counter.most_common():
        print(f"  {c:>4} {cat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
