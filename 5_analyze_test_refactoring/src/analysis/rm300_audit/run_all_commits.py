"""Step 1: run RefactoringMiner 3.0.0 over every commit the audits need.

Covers three commit sets (idempotent -- cached JSONs are skipped):
  (a) the 158 canonical RQ3 commits (file_level_wide.csv),
  (b) up to three first-parent ancestors of each RQ3 commit,
  (c) the no-test-refactoring commits from the annotation export.

Usage:
    python run_all_commits.py            # (a) only
    python run_all_commits.py --audits   # (a) + (b) + (c)
"""
import argparse
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor

from rm_runner import REPO_ROOT, REPOS, JSONS, URL_RE, process_commit

CANONICAL = REPO_ROOT / "5_analyze_test_refactoring/src/analysis/rq3/1_analyze_testsmell_diff/file_level_wide.csv"
ANN_CSV = REPO_ROOT / "4_manual_inspection/src/refactoring_data_2025-02-19.csv"
SKIP_TYPES = {"Non-Refactoring", "Any Refactoring", ""}


def base_commits():
    commits = {}
    for r in csv.DictReader(open(CANONICAL, encoding="utf-8-sig")):
        m = URL_RE.match(r.get("commit_url", "").strip())
        if m:
            commits[m.group(3)] = (m.group(1), m.group(2))
    return commits


def no_test_refactor_commits():
    by_commit = {}
    for r in csv.DictReader(open(ANN_CSV, encoding="utf-8-sig")):
        m = URL_RE.match((r.get("url") or "").strip())
        if not m:
            continue
        by_commit.setdefault(m.groups(), []).append((r.get("type_name") or "").strip())
    return {sha: (owner, repo)
            for (owner, repo, sha), types in by_commit.items()
            if all(t in SKIP_TYPES for t in types)}


def ancestors_of(sha, owner, repo, k=3):
    repo_dir = REPOS / f"{owner}__{repo}"
    if not (repo_dir / ".git").is_dir():
        return []
    subprocess.run(["git", "fetch", "--depth", str(k + 2), "origin", sha],
                   cwd=repo_dir, capture_output=True, timeout=300)
    try:
        out = subprocess.check_output(
            ["git", "rev-list", "--first-parent", "-n", str(k), f"{sha}^"],
            cwd=repo_dir, text=True, timeout=60, stderr=subprocess.DEVNULL)
        return [l.strip() for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError:
        return []


def run(todo):
    statuses = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, (sha, status) in enumerate(ex.map(process_commit, sorted(todo.items())), 1):
            statuses[status] = statuses.get(status, 0) + 1
            if i % 25 == 0 or status not in ("ok", "cached"):
                print(f"[{i}/{len(todo)}] {sha[:10]} {status}", flush=True)
    print("[done]", statuses, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audits", action="store_true",
                    help="also run ancestors (co-occurrence) and residue commits")
    args = ap.parse_args()

    base = base_commits()
    print(f"[plan] RQ3 base commits: {len(base)}", flush=True)
    run(base)

    if args.audits:
        todo = {}
        for sha, (owner, repo) in sorted(base.items()):
            for anc in ancestors_of(sha, owner, repo):
                if not (JSONS / f"{anc}.json").exists():
                    todo[anc] = (owner, repo)
        print(f"[plan] ancestors to run: {len(todo)}", flush=True)
        residue = no_test_refactor_commits()
        for sha, (owner, repo) in residue.items():
            if not (JSONS / f"{sha}.json").exists():
                todo.setdefault(sha, (owner, repo))
        print(f"[plan] +residue commits: {len(residue)} (grand total {len(todo)})", flush=True)
        run(todo)


if __name__ == "__main__":
    main()
