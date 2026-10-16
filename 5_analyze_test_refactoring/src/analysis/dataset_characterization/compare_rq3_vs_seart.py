"""AE-5 / R2-4 follow-up: Mann-Whitney U comparison between the RQ3
subset (manually-inspected commit projects) and the full SEART corpus
(sampling pool minus the RQ3 subset).

Reads project_characteristics.csv. Prints the per-metric U statistic,
two-sided p-value, and Cliff's delta.

Usage:
    python compare_rq3_vs_seart.py
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import mannwhitneyu

THIS_DIR = Path(__file__).resolve().parent
CSV_PATH = THIS_DIR / "project_characteristics.csv"


def parse_int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except (TypeError, ValueError):
        return default


def parse_float(s: str, default: float = 0.0) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


def years_since(iso_ts: str) -> float | None:
    if not iso_ts:
        return None
    try:
        dt = datetime.strptime(iso_ts.split("T")[0], "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
    except Exception:
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days / 365.25


def cliffs_delta(a: list[float], b: list[float]) -> float:
    """Cliff's delta = (#a>b - #a<b) / (na*nb)."""
    if not a or not b:
        return float("nan")
    gt = lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    return (gt - lt) / (len(a) * len(b))


def report(name: str, a: list[float], b: list[float]) -> None:
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if not a or not b:
        print(f"  {name:25s}  insufficient data ({len(a)}, {len(b)})")
        return
    try:
        stat, p = mannwhitneyu(a, b, alternative="two-sided")
    except Exception as e:
        print(f"  {name:25s}  error: {e}")
        return
    delta = cliffs_delta(a, b)
    a_med = sorted(a)[len(a) // 2]
    b_med = sorted(b)[len(b) // 2]
    print(f"  {name:25s}  rq3 n={len(a):>5} med={a_med:>10.2f}   seart n={len(b):>5} med={b_med:>10.2f}   "
          f"U={stat:>10.0f}  p={p:.3e}  Cliff δ={delta:+.3f}")


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    rq3 = [r for r in rows if r.get("corpus_role") in ("rq3_subset", "rq3_subset_only")]
    seart = [r for r in rows if r.get("corpus_role") == "seart_corpus"]
    print(f"RQ3 subset n={len(rq3)}, SEART corpus n={len(seart)}\n")

    metrics = {
        "stars_api":          lambda r: parse_int(r.get("stars_api", "")),
        "forks_api":          lambda r: parse_int(r.get("forks_api", "")),
        "size_kb":            lambda r: parse_int(r.get("size_kb", "")),
        "language_java_pct":  lambda r: parse_float(r.get("language_java_pct", "")),
        "age_years":          lambda r: years_since(r.get("created_at", "")),
        "years_since_push":   lambda r: years_since(r.get("pushed_at", "")),
    }

    print("Mann-Whitney U (two-sided) and Cliff's delta:")
    print(f"  {'metric':25s}  {'rq3':>5}{'':18}seart{'':18}  test stats")
    for name, fn in metrics.items():
        a = [fn(r) for r in rq3]
        b = [fn(r) for r in seart]
        report(name, a, b)

    # Framework presence (proportions). Use a binomial test or just
    # report the percentages — Mann-Whitney on 0/1 isn't ideal but is
    # a reasonable rank-based test.
    print("\nFramework adoption proportions (rq3 vs seart):")
    for col in ["framework_junit5", "framework_junit4", "framework_testng",
                "framework_mockito", "framework_assertj", "framework_hamcrest",
                "framework_spock"]:
        ar = sum(1 for r in rq3 if r.get(col) == "1") / max(len(rq3), 1) * 100
        br = sum(1 for r in seart if r.get(col) == "1") / max(len(seart), 1) * 100
        print(f"  {col[len('framework_'):]:10s}  rq3={ar:5.1f}%   seart={br:5.1f}%   Δ={ar-br:+5.1f} pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
