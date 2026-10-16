"""Enrich the RQ3 canonical commit list with commit messages and PR threads
fetched via the `gh` CLI, producing a CSV ready for socio-technical coding.

The script is restartable: rows already present in the output are skipped, so
GitHub rate-limit interruptions are tolerable. Run `gh auth status` first.

Usage:
    python enrich_with_pr_context.py \
        --input ../rq3/1_analyze_testsmell_diff/file_level_wide.csv \
        --output ./socio_technical_annotation.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from pathlib import Path

COMMIT_URL_RE = re.compile(r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})")

ANNOTATION_COLS = [
    "trigger_category",
    "trigger_subcode",
    "evidence_quote",
    "confidence",
    "notes",
]
CONTEXT_COLS = [
    "commit_url",
    "type_name",
    "owner",
    "repo",
    "sha",
    "commit_subject",
    "commit_body",
    "commit_author",
    "commit_date",
    "pr_number",
    "pr_title",
    "pr_body",
    "pr_state",
    "pr_comments_excerpt",
    "pr_reviews_excerpt",
]
ALL_COLS = CONTEXT_COLS + ANNOTATION_COLS


def gh_json(path: str) -> object | None:
    try:
        out = subprocess.check_output(["gh", "api", path], text=True, timeout=30)
    except subprocess.CalledProcessError:
        return None
    except subprocess.TimeoutExpired:
        return None
    if not out.strip():
        return None
    return json.loads(out)


def truncate(s: str | None, n: int = 1500) -> str:
    if not s:
        return ""
    s = s.replace("\r\n", "\n").strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def fetch_commit(owner: str, repo: str, sha: str) -> dict:
    data = gh_json(f"repos/{owner}/{repo}/commits/{sha}") or {}
    commit = data.get("commit", {})
    msg = commit.get("message", "")
    subject, _, body = msg.partition("\n")
    return {
        "commit_subject": subject.strip(),
        "commit_body": truncate(body, 2000),
        "commit_author": (commit.get("author") or {}).get("name", ""),
        "commit_date": (commit.get("author") or {}).get("date", ""),
    }


def fetch_pr_context(owner: str, repo: str, sha: str) -> dict:
    pulls = gh_json(f"repos/{owner}/{repo}/commits/{sha}/pulls") or []
    if not isinstance(pulls, list) or not pulls:
        return {}
    pr = pulls[0]
    pr_number = pr.get("number")
    comments = gh_json(f"repos/{owner}/{repo}/issues/{pr_number}/comments") or []
    reviews = gh_json(f"repos/{owner}/{repo}/pulls/{pr_number}/reviews") or []
    comment_text = "\n---\n".join(
        f"@{c.get('user', {}).get('login', '?')}: {c.get('body', '')}" for c in comments
    )
    review_text = "\n---\n".join(
        f"@{r.get('user', {}).get('login', '?')} ({r.get('state', '')}): {r.get('body', '')}"
        for r in reviews if r.get("body")
    )
    return {
        "pr_number": pr_number,
        "pr_title": pr.get("title", ""),
        "pr_body": truncate(pr.get("body"), 2000),
        "pr_state": pr.get("state", ""),
        "pr_comments_excerpt": truncate(comment_text, 3000),
        "pr_reviews_excerpt": truncate(review_text, 3000),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="seconds between GitHub API requests (default 1.0)")
    args = ap.parse_args()

    completed: set[tuple[str, str]] = set()
    if args.output.exists():
        with args.output.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                completed.add((r["commit_url"], r["type_name"]))
        print(f"[resume] {len(completed)} rows already done", file=sys.stderr)

    pending: list[tuple[str, str]] = []
    with args.input.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = (r["commit_url"], r["type_name"])
            if key in completed:
                continue
            pending.append(key)

    if not pending:
        print("[done] nothing to do", file=sys.stderr)
        return 0

    cache: dict[str, dict] = {}
    new_file = not args.output.exists()
    with args.output.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALL_COLS)
        if new_file:
            w.writeheader()

        for i, (commit_url, type_name) in enumerate(pending, 1):
            m = COMMIT_URL_RE.match(commit_url.strip())
            if not m:
                continue
            owner, repo, sha = m["owner"], m["repo"], m["sha"]

            if commit_url not in cache:
                ctx = {"commit_url": commit_url, "owner": owner, "repo": repo, "sha": sha}
                ctx.update(fetch_commit(owner, repo, sha))
                ctx.update(fetch_pr_context(owner, repo, sha))
                cache[commit_url] = ctx
                time.sleep(args.sleep)

            row = {**cache[commit_url], "type_name": type_name}
            for c in ANNOTATION_COLS:
                row.setdefault(c, "")
            w.writerow({c: row.get(c, "") for c in ALL_COLS})
            f.flush()
            print(f"[{i}/{len(pending)}] {commit_url} :: {type_name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
