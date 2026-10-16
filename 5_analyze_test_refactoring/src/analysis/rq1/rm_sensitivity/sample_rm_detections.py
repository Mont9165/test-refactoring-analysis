"""Flatten per-commit RefactoringMiner JSON outputs into one row per detection,
filter to test files, then draw a stratified random sample for manual
precision validation.

Usage:
    python sample_rm_detections.py \
        --rm-json-dir ./rm_json \
        --output-flat ./all_test_file_detections.csv \
        --output-sample ./manual_validation_sample.csv \
        --per-type 5 --total-cap 100
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

TEST_PATH_HINTS = ("/src/test/", "/tests/", "/test/")
TEST_NAME_SUFFIXES = ("Test.java", "Tests.java", "IT.java", "ITCase.java")

FLAT_COLS = [
    "commit_url", "sha", "rm_type", "rm_description",
    "file_path", "left_side", "right_side",
]
SAMPLE_COLS = FLAT_COLS + ["is_correct", "correct_type", "notes"]


def is_test_file(path: str) -> bool:
    p = path.lower()
    if any(h in p for h in TEST_PATH_HINTS):
        return True
    return any(path.endswith(s) for s in TEST_NAME_SUFFIXES)


def extract_paths(refactoring: dict) -> list[str]:
    paths: list[str] = []
    for side in ("leftSideLocations", "rightSideLocations"):
        for loc in refactoring.get(side, []) or []:
            fp = loc.get("filePath")
            if fp:
                paths.append(fp)
    return paths


def to_url(repo_field: str, sha: str) -> str:
    if not repo_field:
        return f"https://github.com/UNKNOWN/UNKNOWN/commit/{sha}"
    base = repo_field.rstrip("/").removesuffix(".git")
    return f"{base}/commit/{sha}"


def flatten(json_dir: Path) -> list[dict]:
    out: list[dict] = []
    for jf in sorted(json_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        for commit in data.get("commits", []):
            sha = commit.get("sha1") or commit.get("sha", "")
            url = commit.get("url") or to_url(commit.get("repository", ""), sha)
            for ref in commit.get("refactorings", []):
                paths = extract_paths(ref)
                test_paths = [p for p in paths if is_test_file(p)]
                if not test_paths:
                    continue
                out.append({
                    "commit_url": url,
                    "sha": sha,
                    "rm_type": ref.get("type", ""),
                    "rm_description": ref.get("description", ""),
                    "file_path": "; ".join(sorted(set(test_paths))),
                    "left_side": json.dumps(ref.get("leftSideLocations", []), ensure_ascii=False),
                    "right_side": json.dumps(ref.get("rightSideLocations", []), ensure_ascii=False),
                })
    return out


def stratified_sample(rows: list[dict], per_type: int, total_cap: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_type[r["rm_type"]].append(r)
    picked: list[dict] = []
    for t, group in sorted(by_type.items()):
        rng.shuffle(group)
        picked.extend(group[:per_type])
    rng.shuffle(picked)
    return picked[:total_cap]


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rm-json-dir", required=True, type=Path)
    ap.add_argument("--output-flat", required=True, type=Path)
    ap.add_argument("--output-sample", required=True, type=Path)
    ap.add_argument("--per-type", type=int, default=5)
    ap.add_argument("--total-cap", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = flatten(args.rm_json_dir)
    write_csv(args.output_flat, rows, FLAT_COLS)
    sample = stratified_sample(rows, args.per_type, args.total_cap, args.seed)
    for r in sample:
        r.setdefault("is_correct", "")
        r.setdefault("correct_type", "")
        r.setdefault("notes", "")
    write_csv(args.output_sample, sample, SAMPLE_COLS)
    print(f"[done] flat: {len(rows)} test-file detections -> {args.output_flat}")
    print(f"[done] sample: {len(sample)} rows -> {args.output_sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
