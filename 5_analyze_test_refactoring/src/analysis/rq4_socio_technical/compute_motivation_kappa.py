"""R4-2: Cohen's kappa + final distribution for the two-rater test-refactoring
motivation coding.

Reads motivation_coding_final.csv (exported from test-refactoring-purpose.xlsx,
sheet シート2) which has columns category_kosei, category_fujiwara, and
'final label'. Prints inter-rater agreement and the reconciled distribution.

The CSV has 187 rows. The 2 Lambdarize Method rows are dropped because the
minor revision removed that type from the catalogue (it is a general
refactoring), which leaves the 185 cases reported in the paper.
Category definitions: CODEBOOK.md.

Usage:
    python compute_motivation_kappa.py
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "motivation_coding_final.csv"
REMOVED_TYPES = {"Lambdarize Method"}


def norm(v: str | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    rows = [r for r in rows if r["type_name"] not in REMOVED_TYPES]
    # Detect column names (final label header varies)
    final_col = next(c for c in rows[0].keys() if c.lower().replace(" ", "") in ("finallabel", "final"))

    pairs = []
    finals = []
    for r in rows:
        k, f = norm(r.get("category_kosei")), norm(r.get("category_fujiwara"))
        if k and f:
            pairs.append((k, f))
        fin = norm(r.get(final_col))
        if fin:
            finals.append(fin)

    n = len(pairs)
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    cats = {a for a, _ in pairs} | {b for _, b in pairs}
    ka, kb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ka[c] / n) * (kb[c] / n) for c in cats)
    kappa = (po - pe) / (1 - pe)

    print(f"N (both raters labeled) = {n}")
    print(f"Raw agreement Po        = {po:.4f} ({agree}/{n})")
    print(f"Expected agreement Pe   = {pe:.4f}")
    print(f"Cohen's kappa           = {kappa:.4f}")
    print()
    nf = len(finals)
    print(f"Reconciled final distribution (n={nf}):")
    for cat, cnt in Counter(finals).most_common():
        print(f"  {cnt:3d}  ({100 * cnt / nf:4.1f}%)  {cat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
