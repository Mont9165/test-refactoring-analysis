# Reconstructed from the Claude Code session transcript 01704e59 (scratch file: rq3_recompute/followup/regen_change_patterns_nanmissing.py).
# Logic unchanged; only lines marked 'PATH (rebuild)' differ from the recovered original
# (verbatim copy: recovered_scratch/rq3_recompute/followup/regen_change_patterns_nanmissing.py).
"""R3-5: regenerate Figures 4 & 5 from the CURRENT 158-commit dataset.

The shipped change_patterns_{file,method}.csv (Aug 2025) are stale (a 173-unit
run) and lack a per-smell occurrence base. This script recomputes the change
patterns at the COMMIT level over the current file_level_wide.csv /
method_level_wide.csv (158 commits), and renders the original change_patterns_*_better.pdf
stacked-bar design with the per-smell occurrence count n annotated at the left of each bar
(X = number of commits in which the smell is PRESENT before refactoring -- the occurrence
base the reviewer asked for). It also prints the per-smell table for verification.

Only the two smells never observed in the corpus (n=0 at BOTH levels: Empty Test, Default
Test) are dropped; the same 17 smells are shown in both panels for comparability. No
occurrence threshold is imposed (see NEVER_OBSERVED below for the rationale).

Per commit, smell counts are summed across the commit's test files; a smell is
"present" if its pre-refactoring count > 0; improved/degraded/unchanged compare
the commit's summed pre vs post count.

Usage:  python regen_change_patterns_158.py
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

WIDE = Path(sys.argv[1])  # PATCH: data dir (file_level_wide.csv / method_level_wide.csv)
THIS = Path(sys.argv[2])  # PATCH: output dir

# four-category palette: Not present (pale) | No change/present-stable (grey) |
# Improvements (green) | Degradations (red).
COLOR_ABSENT, COLOR_NC, COLOR_IMP, COLOR_DEG = "#e8e8e8", "#9e9e9e", "#4daf4a", "#e41a1c"


# NumberOfMethods is a size metric, not a smell. bin-lin TestSmellDetector also ships two
# non-standard detectors (Verbose Test, Dependent Test) that never fire (Verbose:
# MAX_STATEMENTS=123 gate; Dependent: String-vs-Stream bug), so we report only tsDetect's
# 19 standard smells.
BROKEN_OR_NONSMELL = {"NumberOfMethods", "Verbose Test", "Dependent Test"}

# Never-observed smells: n=0 (not present in a single commit) at BOTH the file and method
# level, so they contribute only an empty 100%-no-change bar. We omit those two and show
# every smell that occurs at least once, with its occurrence count n at the left of the bar.
# We do NOT impose an occurrence threshold: the percentages are over all 158 commits (not
# over n), so even low-occurrence smells yield correct "rarely changes" bars and the n label
# lets the reader weight them. Kept as the SAME set across panels for file/method
# comparability (so Constructor Initialization, file n=12 / method n=0, also appears in the
# method panel as a flat n=0 bar); noted in the caption.
#   Empty Test (0, 0)   Default Test (0, 0)
NEVER_OBSERVED = {"Empty Test", "Default Test"}

EXCLUDE = BROKEN_OR_NONSMELL | NEVER_OBSERVED


def load_commit_level(wide_csv: Path):
    """PATCH (follow-up): unmeasured (empty) cells are MISSING, not 0. Per commit and smell, sum only the pairs
    measured on both sides; a commit with no measured pair for a smell is left out of that smell's base."""
    rows = list(csv.DictReader(wide_csv.open(encoding="utf-8-sig")))
    smells = [c[:-7] for c in rows[0] if c.endswith("_before") and c[:-7] not in EXCLUDE]

    def val(v):
        v = (v or "").strip()
        return None if v.lower() in ("", "nan") else float(v)

    per = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0]))  # commit -> smell -> [before, after, measured pairs]
    for r in rows:
        u = r["commit_url"]
        for s in smells:
            b, a = val(r.get(s + "_before")), val(r.get(s + "_after"))
            if b is None or a is None:
                continue
            per[u][s][0] += b
            per[u][s][1] += a
            per[u][s][2] += 1
    n_commits = sum(1 for u in per if any(per[u][s][2] > 0 for s in smells))

    stats = {}
    for s in smells:
        present = improved = degraded = nochange_present = not_present = base = 0
        for u in per:
            b, a, k = per[u][s]
            if k == 0:
                continue                  # smell not measured in this commit
            base += 1
            if b > 0:
                present += 1
            if a < b:
                improved += 1
            elif a > b:
                degraded += 1
            elif b > 0:
                nochange_present += 1
            else:
                not_present += 1
        stats[s] = dict(present=present, improved=improved, degraded=degraded,
                        nochange_present=nochange_present, not_present=not_present, base=base)
    return n_commits, stats


# label font size, shared by the per-segment percentages and the per-bar n=
# (the reviewer asked for the n to be in the SAME font size as the % labels).
LABEL_FS = 12


def render(level: str, wide_csv: Path):
    n_commits, stats = load_commit_level(wide_csv)
    # Order by occurrence count n (commits where the smell is present before refactoring),
    # largest at the bottom -- so reading the chart top-to-bottom, n ascends and the pale
    # "Not present" segments form a clean staircase that narrows toward the bottom.
    smells = sorted(stats.keys(), key=lambda s: stats[s]["present"], reverse=True)

    print(f"\n=== {level} level (n={n_commits} commits) ===")
    print(f"{'smell':28s} {'n(pres)':>7} {'improved':>8} {'degraded':>8} {'nochg':>6} {'absent':>6} {'base':>5}")
    for s in smells:
        d = stats[s]
        print(f"{s:28s} {d['present']:7d} {d['improved']:8d} {d['degraded']:8d} "
              f"{d['nochange_present']:6d} {d['not_present']:6d} {d['base']:5d}")

    y = np.arange(len(smells))
    absn = np.array([stats[s]["not_present"] / stats[s]["base"] * 100 for s in smells])  # PATCH: per-smell measured base
    ncp = np.array([stats[s]["nochange_present"] / stats[s]["base"] * 100 for s in smells])
    imp = np.array([stats[s]["improved"] / stats[s]["base"] * 100 for s in smells])
    deg = np.array([stats[s]["degraded"] / stats[s]["base"] * 100 for s in smells])

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_axisbelow(True)
    ax.grid(axis="x", linestyle=":", color="gray", alpha=0.6)
    ax.barh(y, absn, color=COLOR_ABSENT, label="Not present")
    ax.barh(y, ncp, left=absn, color=COLOR_NC, label="No change")
    ax.barh(y, imp, left=absn + ncp, color=COLOR_IMP, label="Improvements")
    ax.barh(y, deg, left=absn + ncp + imp, color=COLOR_DEG, label="Degradations")
    ax.set_yticks(y)
    ax.set_yticklabels(smells, fontsize=16)

    for i_y, s in enumerate(smells):
        av, ncv, impv, degv = absn[i_y], ncp[i_y], imp[i_y], deg[i_y]
        # n = occurrence base (commits in which the smell is present before refactoring),
        # at the far left, same font size as the % labels.
        nlab = f"n={stats[s]['present']}" + (f" (of {stats[s]['base']})" if stats[s]["base"] != n_commits else "")  # PATCH
        ax.text(1.0, i_y, nlab, va="center", ha="left",
                fontsize=LABEL_FS, fontweight="bold", color="black")
        # show the Not-present percentage on every bar; spell out the words "not present"
        # only ONCE (top bar) since the legend already names the pale colour. Centre the
        # label in the pale segment, but for a narrow pale segment left-align it past the
        # n= label so the two do not overlap.
        if av >= 8:
            txt = f"{av:.0f}% not present" if i_y == len(smells) - 1 else f"{av:.0f}%"
            if av >= 22:
                ax.text(av / 2, i_y, txt, va="center", ha="center",
                        fontsize=LABEL_FS - 2, color="#555555")
            else:
                ax.text(9.0, i_y, txt, va="center", ha="left",
                        fontsize=LABEL_FS - 2, color="#555555")
        # per-segment percentage labels (white, bold, centred) for the wide-enough segments.
        if ncv >= 12:
            ax.text(av + ncv / 2, i_y, f"{ncv:.1f}%", va="center", ha="center",
                    fontsize=LABEL_FS, fontweight="bold", color="white")
        if impv >= 4:
            ax.text(av + ncv + impv / 2, i_y, f"{impv:.1f}%", va="center", ha="center",
                    fontsize=LABEL_FS, fontweight="bold", color="white")
        if degv >= 4:
            ax.text(av + ncv + impv + degv / 2, i_y, f"{degv:.1f}%", va="center", ha="center",
                    fontsize=LABEL_FS, fontweight="bold", color="white")

    ax.set_xlabel(f"Percentage of the {n_commits} paired commits (%)", fontsize=14)  # PATCH: was hard-coded 158
    ax.tick_params(axis="x", labelsize=14)
    ax.set_xlim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=4, fontsize=11, frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(THIS / f"change_patterns_{level}_n{n_commits}.{ext}", dpi=300, bbox_inches="tight")  # PATCH
    plt.close(fig)
    print(f"[done] change_patterns_{level}_n{n_commits}.pdf / .png")  # PATCH


def main() -> int:
    render("file", WIDE / "file_level_wide.csv")
    render("method", WIDE / "method_level_wide.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
