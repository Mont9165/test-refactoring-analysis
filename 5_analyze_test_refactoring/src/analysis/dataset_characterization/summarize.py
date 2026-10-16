"""Summarise project_characteristics.csv to feed AE-5 / R2-4 / R4-3.

Outputs to stdout the distributions of:
  - testing framework usage (junit5 / junit4 / testng / mockito / assertj / etc.)
  - top GitHub topics
  - language top / java percentage
  - stars/forks/age histograms (basic stats)
  - RQ3-subset vs SEART-corpus comparison

Usage:
    python summarize.py [--csv project_characteristics.csv]
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median, mean

FRAMEWORK_COLS = [
    "framework_junit5", "framework_junit4", "framework_testng",
    "framework_mockito", "framework_assertj", "framework_hamcrest",
    "framework_spock",
]


def parse_int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except (ValueError, TypeError):
        return default


def parse_float(s: str, default: float = 0.0) -> float:
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def years_since(iso_ts: str) -> float | None:
    if not iso_ts:
        return None
    try:
        dt = datetime.strptime(iso_ts.split("T")[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days / 365.25


def summarise_group(rows: list[dict], label: str) -> None:
    if not rows:
        print(f"\n=== {label}: (no rows) ===")
        return
    print(f"\n=== {label} (n={len(rows)}) ===")

    # Framework presence
    fw_counts = {col: sum(1 for r in rows if r.get(col) == "1") for col in FRAMEWORK_COLS}
    print("Test framework usage:")
    for col, c in sorted(fw_counts.items(), key=lambda kv: -kv[1]):
        pct = 100 * c / len(rows)
        print(f"  {col[len('framework_'):]:10s} {c:>4}  {pct:>5.1f}%")

    # Top topics
    topic_counter: Counter[str] = Counter()
    for r in rows:
        topics = (r.get("topics") or "").split(",")
        for t in topics:
            t = t.strip()
            if t:
                topic_counter[t] += 1
    if topic_counter:
        print("\nTop 15 topics:")
        for topic, c in topic_counter.most_common(15):
            print(f"  {c:>4} {topic}")

    # Language
    java_pct = [parse_float(r.get("language_java_pct", "0")) for r in rows]
    java_pct = [p for p in java_pct if p is not None]
    if java_pct:
        print(f"\nJava share of LOC: median={median(java_pct):.2f}, mean={mean(java_pct):.2f}, "
              f"share>0.5: {sum(1 for p in java_pct if p > 0.5)/len(java_pct)*100:.1f}%")

    top_langs = Counter()
    for r in rows:
        lang = r.get("language_top", "").strip()
        if lang:
            top_langs[lang] += 1
    if top_langs:
        print("Top 5 dominant languages:")
        for lang, c in top_langs.most_common(5):
            print(f"  {c:>4} {lang}")

    # Stars/forks
    stars = sorted(parse_int(r.get("stars_api", "0")) for r in rows)
    forks = sorted(parse_int(r.get("forks_api", "0")) for r in rows)
    sizes = sorted(parse_int(r.get("size_kb", "0")) for r in rows)
    if stars:
        print(f"\nStars: median={median(stars)}, P25={stars[len(stars)//4]}, "
              f"P75={stars[len(stars)*3//4]}, max={stars[-1]}")
        print(f"Forks: median={median(forks)}, max={forks[-1]}")
        print(f"Size (KB): median={median(sizes)}, max={sizes[-1]}")

    # Age
    ages = [years_since(r.get("created_at", "")) for r in rows]
    ages = [a for a in ages if a is not None]
    if ages:
        ages.sort()
        print(f"Repo age (years): median={median(ages):.1f}, P25={ages[len(ages)//4]:.1f}, "
              f"P75={ages[len(ages)*3//4]:.1f}")

    # Last push recency
    pushed = [years_since(r.get("pushed_at", "")) for r in rows]
    pushed = [p for p in pushed if p is not None]
    if pushed:
        pushed.sort()
        print(f"Years since last push: median={median(pushed):.1f}, "
              f"#stale (>2y): {sum(1 for p in pushed if p > 2)}")

    # Archived
    archived = sum(1 for r in rows if r.get("archived") == "1")
    print(f"Archived repos: {archived} ({100*archived/len(rows):.1f}%)")


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=here / "project_characteristics.csv")
    args = ap.parse_args()

    if not args.csv.exists():
        print(f"[error] {args.csv} not found")
        return 1

    with args.csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {args.csv}")

    rq3_subset = [r for r in rows if r.get("corpus_role") in ("rq3_subset", "rq3_subset_only")]
    seart_corpus = [r for r in rows if r.get("corpus_role") == "seart_corpus"]

    summarise_group(rq3_subset, "RQ3 SUBSET (manually-inspected commit projects)")
    summarise_group(seart_corpus, "SEART CORPUS (sampling pool, partial)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
