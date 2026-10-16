"""R2-6: add clickable GitHub diff-anchor links to the RM validation sample.

Each RefactoringMiner detection has a commit_url, a file_path, and left/right
side JSON ranges (startLine). To let a human rater jump straight to the
changed lines, GitHub uses per-file anchors of the form

    <commit_url>#diff-<sha256(file_path)>L<n>    (left / deleted side)
    <commit_url>#diff-<sha256(file_path)>R<n>    (right / added side)

This script reads each rater CSV, parses the first range of left_side /
right_side, and writes two new columns:
  - diff_link_before : anchor on the deleted (left) line
  - diff_link_after  : anchor on the added (right) line

Usage:
    python add_diff_links.py
Writes *_linked.csv next to each input.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = [
    "manual_validation_sample.csv",
    "manual_validation_sample_rater_a.csv",
    "manual_validation_sample_rater_b.csv",
]


def first_start_line(side_json: str) -> int | None:
    try:
        items = json.loads(side_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not items:
        return None
    # Prefer the first range that has a startLine.
    for it in items:
        sl = it.get("startLine")
        if isinstance(sl, int):
            return sl
    return None


def diff_anchor(commit_url: str, file_path: str, side: str, line: int | None) -> str:
    if line is None:
        return ""
    fh = hashlib.sha256(file_path.encode("utf-8")).hexdigest()
    return f"{commit_url}#diff-{fh}{side}{line}"


def process(path: Path) -> None:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if not rows:
        return
    fields = list(rows[0].keys())
    for col in ("diff_link_before", "diff_link_after"):
        if col not in fields:
            # insert right after file_path for readability
            idx = fields.index("file_path") + 1 if "file_path" in fields else len(fields)
            fields.insert(idx, col)
    for r in rows:
        cu = r.get("commit_url", "")
        fp = r.get("file_path", "")
        lb = first_start_line(r.get("left_side", ""))
        rb = first_start_line(r.get("right_side", ""))
        r["diff_link_before"] = diff_anchor(cu, fp, "L", lb)
        r["diff_link_after"] = diff_anchor(cu, fp, "R", rb)
    out = path.with_name(path.stem + "_linked.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    filled = sum(1 for r in rows if r["diff_link_after"] or r["diff_link_before"])
    print(f"{path.name}: {len(rows)} rows, {filled} with at least one diff link -> {out.name}")


def main() -> int:
    for name in INPUTS:
        p = HERE / name
        if p.exists():
            process(p)
        else:
            print(f"[skip] {name} not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
