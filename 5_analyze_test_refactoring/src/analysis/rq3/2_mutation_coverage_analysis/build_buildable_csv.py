"""Construct buildable_commits.csv from run_log.csv.

The bulk runner (run_pit_jacoco.sh + run_all_commits.py) writes per-side
results to run_log.csv. The aggregator expects buildable_commits.csv with
one row per commit (containing parent_sha + sha). This helper joins the
two sides and emits buildable_commits.csv ready for `aggregate_results.py`.

Filtering: include a commit only when the user asks for it
(--include all|build|jacoco|pit). Default is `pit` (only commits where
both sides have pit_ok=true), which is what the response letter analysis
needs.

Usage:
    python build_buildable_csv.py \
        --run-log /tmp/pit_pipeline/results/run_log.csv \
        --output /tmp/pit_pipeline/buildable_commits.csv \
        --include pit
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

COMMIT_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-log", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--include", choices=("all", "build", "jacoco", "pit"),
                    default="pit",
                    help="Inclusion criterion (default: pit; both sides need pit_ok=true)")
    args = ap.parse_args()

    if not args.run_log.exists():
        raise SystemExit(f"run-log not found: {args.run_log}")

    by_url: dict[str, dict[str, dict]] = defaultdict(dict)
    with args.run_log.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            url = (r.get("commit_url") or "").strip()
            side = (r.get("side") or "").strip()
            if url and side in ("before", "after"):
                by_url[url][side] = r

    def passes(row: dict) -> bool:
        if args.include == "all":
            return True
        if args.include == "build":
            return row.get("build_ok") == "true"
        if args.include == "jacoco":
            return row.get("jacoco_ok") == "true"
        return row.get("pit_ok") == "true"

    out_rows = []
    skipped_partial = 0
    skipped_filter = 0
    for url, sides in by_url.items():
        if "before" not in sides or "after" not in sides:
            skipped_partial += 1
            continue
        if not passes(sides["before"]) or not passes(sides["after"]):
            skipped_filter += 1
            continue
        m = COMMIT_URL_RE.match(url)
        if not m:
            continue
        out_rows.append({
            "commit_url": url,
            "owner": m.group("owner"),
            "repo": m.group("repo"),
            "sha": sides["after"].get("sha", ""),
            "parent_sha": sides["before"].get("sha", ""),
            "build_system": "maven",
            "builds_before": "True",
            "builds_after": "True",
            "error": "",
        })

    fieldnames = [
        "commit_url", "owner", "repo", "sha", "parent_sha",
        "build_system", "builds_before", "builds_after", "error",
    ]
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"[done] wrote {len(out_rows)} rows to {args.output}")
    print(f"       skipped (partial sides): {skipped_partial}, "
          f"(filter: --include {args.include}): {skipped_filter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
