"""Build the list of commits to retry from a run_log.csv.

Reads the existing run_log.csv and emits two .txt files, one URL per line:
  - retry_one.txt:   commits where exactly ONE side has pit_ok=true (quick win).
  - retry_both.txt:  commits where BOTH sides have pit_ok=false (harder).

Commits with both_sides_pit_ok=true are skipped (already done).

Usage:
    python build_retry_list.py <run_log.csv> <retry_one.txt> <retry_both.txt>
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: build_retry_list.py <run_log.csv> <retry_one.txt> <retry_both.txt>",
              file=sys.stderr)
        return 2
    run_log = Path(sys.argv[1])
    retry_one_path = Path(sys.argv[2])
    retry_both_path = Path(sys.argv[3])

    by_commit: dict[str, dict[str, dict]] = defaultdict(dict)
    with run_log.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            url = r["commit_url"]
            side = r.get("side", "")
            existing = by_commit[url].get(side)
            # success-wins for the same (url, side) — never let a failed run
            # overwrite a previously-succeeded run.
            if existing is None or existing.get("pit_ok") != "true":
                by_commit[url][side] = r

    one, both, done = [], [], []
    for url, sides in by_commit.items():
        b = sides.get("before", {}).get("pit_ok") == "true"
        a = sides.get("after", {}).get("pit_ok") == "true"
        if b and a:
            done.append(url)
        elif b or a:
            one.append(url)
        else:
            both.append(url)

    retry_one_path.write_text("\n".join(one) + ("\n" if one else ""), encoding="utf-8")
    retry_both_path.write_text("\n".join(both) + ("\n" if both else ""), encoding="utf-8")

    print(f"already done       : {len(done)}")
    print(f"retry one (quick)  : {len(one)} -> {retry_one_path}")
    print(f"retry both (hard)  : {len(both)} -> {retry_both_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
