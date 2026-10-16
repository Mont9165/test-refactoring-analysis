"""Drive run_pit_jacoco.sh over every distinct commit_url in the canonical RQ3
CSV. Resumable: a (commit_url) is skipped if both before and after rows are
already present in run_log.csv with at least one of build/jacoco/pit_ok.

Usage:
    python run_all_commits.py \
        --canonical-csv ../1_analyze_testsmell_diff/file_level_wide.csv \
        --runner ./run_pit_jacoco.sh \
        --results-dir /tmp/pit_pipeline/results \
        [--limit 5]
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


def already_processed(run_log_path: Path) -> dict[str, set[str]]:
    """Return {commit_url -> {side, ...}} for rows already logged."""
    out: dict[str, set[str]] = defaultdict(set)
    if not run_log_path.exists():
        return out
    with run_log_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            url = (r.get("commit_url") or "").strip()
            side = (r.get("side") or "").strip()
            if url and side in ("before", "after"):
                out[url].add(side)
    return out


def commits_with_both_pit_ok(run_log_path: Path) -> set[str]:
    """Return commit_urls where the LATEST run for both sides has pit_ok=true.

    When the same (commit_url, side) appears multiple times (e.g., from a
    retry run), keep the most recent row.
    """
    if not run_log_path.exists():
        return set()
    latest: dict[tuple[str, str], dict] = {}
    with run_log_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            url = (r.get("commit_url") or "").strip()
            side = (r.get("side") or "").strip()
            if url and side in ("before", "after"):
                latest[(url, side)] = r
    out: set[str] = set()
    by_url: dict[str, dict[str, dict]] = defaultdict(dict)
    for (url, side), row in latest.items():
        by_url[url][side] = row
    for url, sides in by_url.items():
        if "before" in sides and "after" in sides \
                and sides["before"].get("pit_ok") == "true" \
                and sides["after"].get("pit_ok") == "true":
            out.add(url)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical-csv", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path,
                    help="path to run_pit_jacoco.sh")
    ap.add_argument("--results-dir", required=True, type=Path,
                    help="WORK_DIR/results passed to the runner")
    ap.add_argument("--work-dir", type=Path, default=None,
                    help="WORK_DIR for the runner (default: parent of results-dir)")
    ap.add_argument("--limit", type=int, default=None,
                    help="optional cap on number of commits processed (debug)")
    ap.add_argument("--retry-failed", action="store_true",
                    help="reprocess commits whose previous run had pit_ok=false")
    args = ap.parse_args()

    runner_path = args.runner.resolve()
    if not runner_path.exists():
        print(f"[error] runner not found: {runner_path}", file=sys.stderr)
        return 2
    work_dir = (args.work_dir or args.results_dir.parent).resolve()
    args.results_dir.mkdir(parents=True, exist_ok=True)
    run_log = args.results_dir / "run_log.csv"

    seen: set[str] = set()
    commits: list[str] = []
    with args.canonical_csv.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            url = (r.get("commit_url") or "").strip()
            if url and url not in seen:
                seen.add(url)
                commits.append(url)

    if args.limit:
        commits = commits[: args.limit]

    done_sides = already_processed(run_log)
    fully_succeeded = commits_with_both_pit_ok(run_log)

    pending: list[str] = []
    for url in commits:
        if args.retry_failed:
            # Retry mode: skip commits where both sides already have pit_ok=true.
            if url in fully_succeeded:
                continue
        else:
            # Normal mode: skip commits where both sides have been attempted at all.
            sides = done_sides.get(url, set())
            if sides == {"before", "after"}:
                continue
        pending.append(url)

    print(f"[plan] {len(pending)} of {len(commits)} commits remaining "
          f"(already done: {len(commits) - len(pending)})", file=sys.stderr)

    env_extra = {
        "WORK_DIR": str(work_dir),
        "RESULTS_DIR": str(args.results_dir),
    }

    successes = failures = 0
    started = time.time()
    for i, url in enumerate(pending, 1):
        t0 = time.time()
        print(f"\n[{i}/{len(pending)}] {url}", file=sys.stderr)
        env = {**__import__("os").environ, **env_extra}
        rc = subprocess.call([str(runner_path), url], env=env)
        elapsed = time.time() - t0
        if rc == 0:
            successes += 1
        else:
            failures += 1
        print(f"[{i}/{len(pending)}] rc={rc} elapsed={elapsed:.0f}s "
              f"(running totals: ok={successes} fail={failures} "
              f"wall={time.time()-started:.0f}s)", file=sys.stderr)

    print(f"\n[done] {successes} ok, {failures} fail, "
          f"total wall={time.time()-started:.0f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
