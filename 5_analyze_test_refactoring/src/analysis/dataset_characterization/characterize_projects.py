"""Augment the SEART project list with GitHub metadata + testing framework
detection. Resume-friendly.

Usage:
    python characterize_projects.py \
        --seart ../../../1_collect_test_refactoring_commits/src/main/resources/input/projects_info.csv \
        --rq3 ../rq3/1_analyze_testsmell_diff/file_level_wide.csv \
        --output ./project_characteristics.csv
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import subprocess
import sys
import time
from pathlib import Path

COMMIT_URL_RE = re.compile(r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/")

FRAMEWORK_PATTERNS = {
    "framework_junit5": re.compile(r"junit-jupiter|junit\.jupiter", re.I),
    "framework_junit4": re.compile(r"junit:junit|<artifactId>junit</artifactId>", re.I),
    "framework_testng": re.compile(r"testng", re.I),
    "framework_mockito": re.compile(r"mockito", re.I),
    "framework_assertj": re.compile(r"assertj", re.I),
    "framework_hamcrest": re.compile(r"hamcrest", re.I),
    "framework_spock": re.compile(r"spock", re.I),
}

OUTPUT_COLS = [
    "full_name", "corpus_role", "stars_seart", "forks_seart", "commits_seart",
    "stars_api", "forks_api", "watchers_api", "size_kb", "topics", "license",
    "default_branch", "created_at", "pushed_at", "archived", "fork",
    "language_top", "language_java_pct",
    *FRAMEWORK_PATTERNS.keys(),
    "build_system", "fetch_error",
]


def gh_json(path: str) -> object | None:
    try:
        out = subprocess.check_output(["gh", "api", path], text=True, timeout=30)
    except subprocess.CalledProcessError:
        return None
    except subprocess.TimeoutExpired:
        return None
    if not out.strip():
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def detect_frameworks(text: str) -> dict[str, int]:
    return {k: int(bool(p.search(text))) for k, p in FRAMEWORK_PATTERNS.items()}


def fetch_build_text(full_name: str, default_branch: str) -> tuple[str, str]:
    for path in ("pom.xml", "build.gradle", "build.gradle.kts"):
        info = gh_json(f"repos/{full_name}/contents/{path}?ref={default_branch}")
        if isinstance(info, dict) and info.get("content"):
            try:
                content = base64.b64decode(info["content"]).decode("utf-8", errors="ignore")
            except Exception:
                continue
            return path, content
    return "", ""


def language_summary(full_name: str) -> tuple[str, float]:
    data = gh_json(f"repos/{full_name}/languages")
    if not isinstance(data, dict) or not data:
        return "", 0.0
    total = sum(data.values()) or 1
    top = max(data.items(), key=lambda kv: kv[1])
    java_share = data.get("Java", 0) / total
    return top[0], round(java_share, 4)


def process(full_name: str, role: str, seart_row: dict | None) -> dict:
    out: dict = {c: "" for c in OUTPUT_COLS}
    out.update({
        "full_name": full_name,
        "corpus_role": role,
        "stars_seart": (seart_row or {}).get("Stars", ""),
        "forks_seart": (seart_row or {}).get("Forks", ""),
        "commits_seart": (seart_row or {}).get("Commits", ""),
    })

    repo = gh_json(f"repos/{full_name}")
    if not isinstance(repo, dict):
        out["fetch_error"] = "repo lookup failed"
        return out

    out.update({
        "stars_api": repo.get("stargazers_count", ""),
        "forks_api": repo.get("forks_count", ""),
        "watchers_api": repo.get("subscribers_count", ""),
        "size_kb": repo.get("size", ""),
        "topics": ",".join(repo.get("topics") or []),
        "license": (repo.get("license") or {}).get("spdx_id", ""),
        "default_branch": repo.get("default_branch", ""),
        "created_at": repo.get("created_at", ""),
        "pushed_at": repo.get("pushed_at", ""),
        "archived": int(bool(repo.get("archived"))),
        "fork": int(bool(repo.get("fork"))),
    })

    top_lang, java_pct = language_summary(full_name)
    out["language_top"] = top_lang
    out["language_java_pct"] = java_pct

    build_path, build_text = fetch_build_text(full_name, out["default_branch"])
    out["build_system"] = build_path or ""
    if build_text:
        out.update(detect_frameworks(build_text))
    return out


def load_rq3_projects(rq3_csv: Path) -> set[str]:
    out: set[str] = set()
    if not rq3_csv.exists():
        return out
    with rq3_csv.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m = COMMIT_URL_RE.match(r.get("commit_url", ""))
            if m:
                out.add(f"{m['owner']}/{m['repo']}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seart", required=True, type=Path)
    ap.add_argument("--rq3", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    rq3_set = load_rq3_projects(args.rq3)

    seart_rows: dict[str, dict] = {}
    with args.seart.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            name = (r.get("Project Name") or "").strip()
            if name:
                seart_rows[name] = r

    # Process RQ3-subset projects FIRST so the response letter has data even
    # if the full 5,500-project run is interrupted (each project takes ~10s
    # of gh API time).
    targets: list[tuple[str, str]] = []
    rq3_done: set[str] = set()
    for name in rq3_set:
        role = "rq3_subset" if name in seart_rows else "rq3_subset_only"
        targets.append((name, role))
        rq3_done.add(name)
    for name in seart_rows:
        if name not in rq3_done:
            targets.append((name, "seart_corpus"))

    done: set[str] = set()
    if args.output.exists():
        with args.output.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                done.add(r["full_name"])

    new_file = not args.output.exists()
    with args.output.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLS)
        if new_file:
            w.writeheader()
        for i, (name, role) in enumerate(targets, 1):
            if name in done:
                continue
            row = process(name, role, seart_rows.get(name))
            w.writerow(row)
            f.flush()
            print(f"[{i}/{len(targets)}] {name} role={role} err={row.get('fetch_error', '')}", file=sys.stderr)
            time.sleep(args.sleep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
