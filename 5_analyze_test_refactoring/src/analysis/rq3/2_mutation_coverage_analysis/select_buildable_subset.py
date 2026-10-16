"""Identify the subset of RQ3 commits where both refactor SHA and its parent
   compile under Maven. Output: buildable_commits.csv.

Usage:
    python select_buildable_subset.py \
        --input ../1_analyze_testsmell_diff/file_level_wide.csv \
        --workdir ./repos \
        --output ./buildable_commits.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

COMMIT_URL_RE = re.compile(r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})")


@dataclass
class CommitRecord:
    commit_url: str
    owner: str
    repo: str
    sha: str
    parent_sha: str | None = None
    build_system: str | None = None  # "maven" | "gradle" | "unknown"
    builds_before: bool = False
    builds_after: bool = False
    error: str = ""


def parse_url(url: str) -> tuple[str, str, str] | None:
    m = COMMIT_URL_RE.match(url.strip())
    if not m:
        return None
    return m["owner"], m["repo"], m["sha"]


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, (proc.stdout + proc.stderr)[-2000:]


def detect_build_system(repo_dir: Path) -> str:
    if (repo_dir / "pom.xml").exists():
        return "maven"
    if (repo_dir / "build.gradle").exists() or (repo_dir / "build.gradle.kts").exists():
        return "gradle"
    return "unknown"


def try_build(repo_dir: Path, build_system: str) -> tuple[bool, str]:
    if build_system == "maven":
        rc, out = run(["mvn", "-B", "-q", "-DskipTests", "test-compile"], cwd=repo_dir, timeout=900)
        return rc == 0, out
    return False, f"unsupported build system: {build_system}"


def process(record: CommitRecord, workdir: Path) -> CommitRecord:
    repo_dir = workdir / f"{record.owner}__{record.repo}"
    if not repo_dir.exists():
        rc, out = run([
            "git", "clone", "--filter=blob:none", "--no-tags",
            f"https://github.com/{record.owner}/{record.repo}.git", str(repo_dir),
        ], timeout=900)
        if rc != 0:
            record.error = f"clone failed: {out[-200:]}"
            return record

    rc, _ = run(["git", "fetch", "--depth=2", "origin", record.sha], cwd=repo_dir, timeout=300)
    rc, out = run(["git", "checkout", "-q", record.sha], cwd=repo_dir)
    if rc != 0:
        record.error = f"checkout failed: {out[-200:]}"
        return record

    rc, parent_out = run(["git", "rev-parse", f"{record.sha}^"], cwd=repo_dir)
    if rc != 0:
        record.error = "no parent commit"
        return record
    record.parent_sha = parent_out.strip().splitlines()[-1]

    record.build_system = detect_build_system(repo_dir)

    ok_after, _ = try_build(repo_dir, record.build_system)
    record.builds_after = ok_after

    run(["git", "checkout", "-q", record.parent_sha], cwd=repo_dir)
    ok_before, _ = try_build(repo_dir, record.build_system)
    record.builds_before = ok_before
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--workdir", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--limit", type=int, default=None, help="optional cap for dry runs")
    args = ap.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    records: list[CommitRecord] = []
    with args.input.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = row["commit_url"].strip()
            if url in seen:
                continue
            seen.add(url)
            parsed = parse_url(url)
            if not parsed:
                continue
            owner, repo, sha = parsed
            records.append(CommitRecord(commit_url=url, owner=owner, repo=repo, sha=sha))

    if args.limit:
        records = records[: args.limit]

    print(f"[info] {len(records)} unique commits to inspect", file=sys.stderr)

    fieldnames = list(asdict(records[0]).keys())
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, r in enumerate(records, 1):
            try:
                r = process(r, args.workdir)
            except subprocess.TimeoutExpired:
                r.error = "timeout"
            except Exception as e:  # noqa: BLE001
                r.error = f"exception: {e}"
            writer.writerow(asdict(r))
            f.flush()
            print(f"[{i}/{len(records)}] {r.commit_url} before={r.builds_before} after={r.builds_after} {r.error}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
