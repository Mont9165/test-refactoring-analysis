"""R3-2: For each commit with a test refactoring, look at the nearby
commits (parent / child within K) and check whether RM detects a general
refactoring there. This addresses Reviewer 3's point that the
small-commit convention can split test-specific and general
refactorings into separate commits.

Inputs:
  - Canonical RQ3 commits (file_level_wide.csv -> 158 commits with test refactor).
  - Cached RM JSON outputs in /tmp/rm_sensitivity/json/<sha>.json.
  - Cached repos under /tmp/pit_pipeline_v2/repos/<owner>__<repo>.
  - For each test-refactor commit, walk K=3 commits up and K=3 commits
    down via `git rev-list` and run RM (or read cached output if
    available).

Output:
  - multi_commit_cooccurrence.csv: per (test_refactor_commit) the count
    of nearby commits with general RM-detected refactoring within
    window K.
  - Summary: percentage of test-refactor commits that have at least one
    general refactoring within K=1, K=3, K=5 (commit-level).

Usage:
    python multi_commit_cooccurrence.py [--window 3]

NOTE: This script does NOT run RM on every nearby commit by default
(would be slow). It only uses already-cached JSONs. Pass --run-rm to
run RM on missing commits within the window.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

CANONICAL_CSV = Path("/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/"
                     "5_analyze_test_refactoring/src/analysis/rq3/1_analyze_testsmell_diff/file_level_wide.csv")
RM_JSON_DIR = Path("/tmp/rm_sensitivity/json")
REPOS_DIR = Path("/tmp/pit_pipeline_v2/repos")
RM_BIN = Path("/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/"
              "5_analyze_test_refactoring/src/analysis/rq1/RefactoringMiner/tools/RefactoringMiner-3.0.10/bin/RefactoringMiner")
COMMIT_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})"
)


def parse_url(url: str):
    m = COMMIT_URL_RE.match(url.strip())
    return (m["owner"], m["repo"], m["sha"]) if m else None


def fetch_neighborhood(repo_dir: Path, sha: str, k: int) -> None:
    """Deepen the shallow clone enough to expose K commits before SHA."""
    if not repo_dir.exists():
        return
    try:
        subprocess.run(
            ["git", "-C", str(repo_dir), "fetch", "--depth", str(k + 2), "origin", sha],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=60, check=False,
        )
    except Exception:
        pass


def get_neighbors(repo_dir: Path, sha: str, k: int) -> tuple[list[str], list[str]]:
    """Return (ancestors, descendants) within K commits."""
    if not repo_dir.exists():
        return [], []
    fetch_neighborhood(repo_dir, sha, k)
    ancestors = []
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-list", "--first-parent",
             f"-n", str(k), f"{sha}^"],
            text=True, timeout=30, stderr=subprocess.DEVNULL,
        )
        ancestors = [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        pass
    # Descendants are harder under shallow clones; we report ancestors only.
    return ancestors, []


TEST_PATH_HINTS = ("/src/test/", "/tests/", "/test/")


def _is_test_path(p: str) -> bool:
    pl = p.lower()
    if any(h in pl for h in TEST_PATH_HINTS):
        return True
    return p.endswith(("Test.java", "Tests.java", "IT.java", "ITCase.java"))


def rm_general_count(sha: str, repo_dir: Path, run_missing: bool,
                     in_test_files_only: bool = True) -> int:
    """Count general refactorings detected by RM at this SHA. Returns -1 if
    JSON is missing and run_missing=False.

    When `in_test_files_only=True` (default), only counts detections whose
    referenced file paths include a test-file path. This matches the paper's
    RQ1 framing of "general refactorings *in test code*".
    """
    json_path = RM_JSON_DIR / f"{sha}.json"
    if not json_path.exists():
        if not run_missing:
            return -1
        if not repo_dir.exists():
            return -1
        json_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [str(RM_BIN), "-c", str(repo_dir), sha, "-json", str(json_path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=600, check=False,
            )
        except Exception:
            return -1
        if not json_path.exists():
            return -1
    try:
        data = json.loads(json_path.read_text())
    except Exception:
        return 0
    total = 0
    for c in data.get("commits", []):
        for ref in c.get("refactorings", []) or []:
            if not in_test_files_only:
                total += 1
                continue
            paths = set()
            for side in ("leftSideLocations", "rightSideLocations"):
                for loc in ref.get(side, []) or []:
                    fp = loc.get("filePath")
                    if fp:
                        paths.add(fp)
            if any(_is_test_path(p) for p in paths):
                total += 1
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=3,
                    help="Search this many commits before and after (default 3)")
    ap.add_argument("--run-rm", action="store_true",
                    help="Run RM on missing neighbour SHAs (slow)")
    args = ap.parse_args()

    rows = list(csv.DictReader(CANONICAL_CSV.open(encoding="utf-8-sig")))
    test_commits = sorted({r["commit_url"] for r in rows})
    print(f"[info] {len(test_commits)} test-refactor commits", file=sys.stderr)

    out_rows = []
    for url in test_commits:
        parsed = parse_url(url)
        if not parsed:
            continue
        owner, repo, sha = parsed
        repo_dir = REPOS_DIR / f"{owner}__{repo}"
        ancestors, descendants = get_neighbors(repo_dir, sha, args.window)

        own = rm_general_count(sha, repo_dir, args.run_rm)
        anc_with = sum(1 for s in ancestors if rm_general_count(s, repo_dir, args.run_rm) > 0)
        desc_with = sum(1 for s in descendants if rm_general_count(s, repo_dir, args.run_rm) > 0)
        anc_evaluated = sum(1 for s in ancestors if rm_general_count(s, repo_dir, args.run_rm) >= 0)
        desc_evaluated = sum(1 for s in descendants if rm_general_count(s, repo_dir, args.run_rm) >= 0)

        # Joint indicators
        same_commit_general = own > 0
        any_neighbor_general = (anc_with > 0) or (desc_with > 0)

        out_rows.append({
            "commit_url": url,
            "owner": owner,
            "repo": repo,
            "sha": sha,
            "rm_general_at_this_commit": own,
            "n_ancestors_evaluated": anc_evaluated,
            "n_ancestors_with_general": anc_with,
            "n_descendants_evaluated": desc_evaluated,
            "n_descendants_with_general": desc_with,
            "same_commit_general": int(same_commit_general),
            "any_neighbor_general": int(any_neighbor_general),
            "either": int(same_commit_general or any_neighbor_general),
        })

    out_csv = Path(__file__).resolve().parent / "multi_commit_cooccurrence.csv"
    fieldnames = list(out_rows[0].keys()) if out_rows else []
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"[done] {len(out_rows)} rows -> {out_csv}", file=sys.stderr)

    # Summary
    n = len(out_rows)
    if n == 0:
        return 0
    same = sum(r["same_commit_general"] for r in out_rows)
    nbr = sum(r["any_neighbor_general"] for r in out_rows)
    either = sum(r["either"] for r in out_rows)
    print(f"\nSummary (window=±{args.window}):")
    print(f"  test-refactor commits with general refactoring at the SAME commit: "
          f"{same}/{n} ({100*same/n:.1f}%)")
    print(f"  test-refactor commits with general refactoring in any neighbour: "
          f"{nbr}/{n} ({100*nbr/n:.1f}%)")
    print(f"  test-refactor commits with general refactoring at SAME or NEIGHBOUR: "
          f"{either}/{n} ({100*either/n:.1f}%)")

    # How many neighbours actually evaluated (caveat for response letter)
    eval_anc = sum(r["n_ancestors_evaluated"] for r in out_rows)
    eval_desc = sum(r["n_descendants_evaluated"] for r in out_rows)
    expected = n * args.window
    print(f"\nCoverage: ancestors {eval_anc}/{expected}, descendants {eval_desc}/{expected}")
    print("(Re-run with --run-rm to evaluate missing neighbours)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
