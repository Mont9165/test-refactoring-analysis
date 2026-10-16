"""B5 follow-up: re-evaluate the existing RQ3 effectiveness tables under
the corrected n>=6 floor (instead of n>=5).

Reads:
  ../detailed_visualization/refactoring_effectiveness_{file,refactoring}.csv
Writes:
  refactoring_effectiveness_{file,refactoring}_with_n6_floor.csv
plus a flip report listing which (refactoring_type, test_smell) cells:
  - were `significant=True` at n>=5 but become inadmissible under n>=6
  - remain significant
  - or move from inadmissible to admissible (impossible — floor is a
    pure widening, but we report for completeness).

Usage:
    python recompute_with_n6_floor.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
SRC_DIR = THIS_DIR.parent / "detailed_visualization"


def reevaluate(level: str) -> None:
    src = SRC_DIR / f"refactoring_effectiveness_{level}.csv"
    if not src.exists():
        print(f"[skip] {src} not found")
        return
    df = pd.read_csv(src)
    if "sample_size" not in df.columns or "p_value" not in df.columns:
        print(f"[skip] unexpected schema in {src}")
        return

    # Convert significant to bool (csv has python bools)
    df["significant_old"] = df["significant"].astype(str).str.lower().eq("true")
    df["admissible_n5"] = df["sample_size"] >= 5
    df["admissible_n6"] = df["sample_size"] >= 6

    # New significance: must be admissible AND p < 0.05.
    df["significant_n6"] = df["admissible_n6"] & (df["p_value"].astype(float) < 0.05)

    out = THIS_DIR / f"refactoring_effectiveness_{level}_with_n6_floor.csv"
    df.to_csv(out, index=False)
    print(f"[done] {out}")

    # Build flip report
    flips_lost = df[df["significant_old"] & ~df["significant_n6"]][
        ["refactoring_type", "test_smell", "sample_size", "p_value", "effect_size"]
    ]
    kept = df[df["significant_old"] & df["significant_n6"]]
    print(f"\n[{level}] previously significant cells:        "
          f"{int(df['significant_old'].sum())}")
    print(f"[{level}] still significant under n>=6 floor:  "
          f"{len(kept)}")
    print(f"[{level}] LOST under n>=6 floor:                "
          f"{len(flips_lost)}")

    if len(flips_lost):
        print(f"\n[{level}] LOST cells (n=5 boundary):")
        with pd.option_context("display.max_rows", None, "display.width", 200):
            print(flips_lost.to_string(index=False))

    # Also list n=5 cells that, regardless of old significance, were
    # admissible under the old floor but no longer (these may show up
    # in figures even if not "significant").
    only_n5 = df[df["sample_size"] == 5]
    print(f"\n[{level}] cells with exactly n=5 (now inadmissible): {len(only_n5)}")


def main() -> int:
    for level in ("file", "refactoring"):
        reevaluate(level)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
