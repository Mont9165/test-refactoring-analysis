"""Reproduce the Dataset Characterisation numbers (Section 4.2.3 / R2-4).

Characterizes the projects behind the manual-inspection sample
(sampling_test_commits.csv, 190 project names; note google/wycheproof and
C2SP/wycheproof are the same repository before/after a transfer):

  - maturity: median age (reference date 2026-04-30, the gh-API fetch date
    of project_characteristics.csv), stars, SEART commit counts
  - size: median Java SLOC and test SLOC from java_loc_per_project.csv
    (produced by count_java_loc.py at each repo's current default branch;
    two repos with no Java at HEAD are excluded from the medians)
  - test-framework adoption from project_characteristics.csv (top-level
    build-script inspection; shares overlap and are lower bounds)
  - domain distribution from project_domains.csv

Usage: python summarize_sample_projects.py
"""
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SAMPLE_CSV = REPO / "2_sampling_test_refactor_commits/result/sampling_test_commits.csv"
CHAR_CSV = HERE / "project_characteristics.csv"
LOC_CSV = HERE / "java_loc_per_project.csv"
DOMAIN_CSV = HERE / "project_domains.csv"
REF_DATE = datetime(2026, 4, 30, tzinfo=timezone.utc)

FRAMEWORK_COLS = [
    "framework_junit4", "framework_junit5", "framework_testng",
    "framework_mockito", "framework_assertj", "framework_hamcrest",
    "framework_spock",
]


def years_since(iso_ts):
    if not iso_ts:
        return None
    try:
        dt = datetime.strptime(iso_ts.split("T")[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None
    return (REF_DATE - dt).days / 365.25


def pi(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def first(vals):
    return next((v for v in vals if v is not None), None)


def main() -> int:
    with open(SAMPLE_CSV) as f:
        sample = set()
        for r in csv.DictReader(f):
            m = re.search(r"github\.com/([^/]+/[^/]+)", r["repository_url"])
            sample.add(m.group(1) if m else r["repository_name"])
    n = len(sample)
    print(f"sample projects (name-level): {n}")

    by_lower = defaultdict(list)
    with open(CHAR_CSV) as f:
        for r in csv.DictReader(f):
            by_lower[r["full_name"].lower()].append(r)
    rows = []
    for p in sorted(sample):
        cands = by_lower.get(p.lower(), [])
        rows.append(cands)

    stars = sorted(v for v in (first([pi(r["stars_api"]) for r in c]) for c in rows) if v is not None)
    commits = sorted(v for v in (first([pi(r["commits_seart"]) for r in c]) for c in rows) if v is not None)
    ages = sorted(v for v in (first([years_since(r["created_at"]) for r in c]) for c in rows) if v is not None)
    print(f"stars:   n={len(stars)}  median={median(stars)}")
    print(f"commits: n={len(commits)}  median={median(commits):,.0f}")
    print(f"age (y): n={len(ages)}  median={median(ages):.1f}  (reference {REF_DATE.date()})")

    fw = Counter()
    multi = 0
    for c in rows:
        r = c[0] if c else {}
        hits = [col for col in FRAMEWORK_COLS if r.get(col) == "1"]
        fw.update(hits)
        if len(hits) >= 2:
            multi += 1
    print("framework adoption (share of all sample projects; overlapping, lower bounds):")
    for col, k in fw.most_common():
        print(f"  {col[10:]:9s} {k:>3}  {100*k/n:5.1f}%")
    print(f"projects declaring >=2 frameworks: {multi} ({100*multi/n:.0f}%)")

    with open(LOC_CSV) as f:
        loc = {r["full_name"]: r for r in csv.DictReader(f) if not r["error"]}
    ok = [r for r in loc.values() if int(r["java_code"]) > 0]
    code = sorted(int(r["java_code"]) for r in ok)
    tcode = sorted(int(r["test_code"]) for r in ok)
    share = sorted(int(r["test_code"]) / int(r["java_code"]) for r in ok)
    print(f"Java SLOC (n={len(ok)} with Java at HEAD): median={median(code):,.0f}")
    print(f"test SLOC: median={median(tcode):,.0f}   per-project test share: median={median(share)*100:.1f}%")
    print(f"excluded (no Java at current HEAD): {sorted(set(loc) - {r['full_name'] for r in ok})}")

    with open(DOMAIN_CSV) as f:
        dom = Counter(r["domain"] for r in csv.DictReader(f))
    print("domain distribution:")
    for k, v in dom.most_common():
        print(f"  {k:18s} {v:>3}  {100*v/sum(dom.values()):5.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
