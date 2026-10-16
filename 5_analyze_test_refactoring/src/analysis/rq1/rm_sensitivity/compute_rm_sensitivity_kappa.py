"""R2-6: Cohen's kappa + mean test-file precision for the two-rater
RefactoringMiner 3.0.10 sensitivity sample (50 test-file detections).

Reads the two independent rater files
    manual_validation_sample_rater_a_linked.csv
    manual_validation_sample_rater_b_linked.csv
each with a binary `is_correct` column (1 = the detection's `rm_type` is a
correct test-file refactoring, 0 = wrong). Computes:
  * Cohen's kappa between rater a and rater b on is_correct;
  * mean test-file precision (fraction of detections judged correct) from a
    reconciled label, preferring the consensus file
    manual_validation_sample_linked.csv if its is_correct is filled, else
    falling back to rater agreement (disagreements are reported, not guessed);
  * per-rm_type precision so we can see which types fall below the 70%
    exclusion threshold used in the RQ1 re-run;
  * transparent LLM cross-check summaries for Claude and Codex/GPT labels, if
    those files exist. These are triangulation statistics, not human-rater
    labels.

Runs safely before labeling is complete: it reports how many of the 50 rows are
filled and exits cleanly if either rater file is empty.

Usage:
    python compute_rm_sensitivity_kappa.py
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RATER_A = HERE / "manual_validation_sample_rater_a_linked.csv"
RATER_B = HERE / "manual_validation_sample_rater_b_linked.csv"
CONSENSUS = HERE / "manual_validation_sample_linked.csv"
# LLM automated cross-checks (NOT human raters — reported transparently as triangulation).
CLAUDE = HERE / "manual_validation_sample_claude_linked.csv"
CODEX = HERE / "manual_validation_sample_codex_linked.csv"

_TRUE = {"1", "1.0", "yes", "y", "true", "t", "correct", "ok", "〇", "○", "o"}
_FALSE = {"0", "0.0", "no", "n", "false", "f", "incorrect", "wrong", "×", "x", "✗"}


def parse_correct(v: str | None) -> int | None:
    """Map a free-form is_correct cell to 1 / 0, or None if blank/unknown."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if not s:
        return None
    if s in _TRUE:
        return 1
    if s in _FALSE:
        return 0
    return None  # unrecognised -> treat as unlabeled, surfaced below


def row_key(r: dict) -> tuple:
    return (r.get("sha", ""), r.get("rm_type", ""), r.get("file_path", ""))


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing file: {path}")
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))


def binary_kappa(xs: list[int], ys: list[int]) -> tuple[float, float, float, int]:
    """Return (kappa, observed agreement, expected agreement, agreements)."""
    n = len(xs)
    agree = sum(1 for x, y in zip(xs, ys) if x == y)
    po = agree / n
    cx, cy = Counter(xs), Counter(ys)
    pe = sum((cx[c] / n) * (cy[c] / n) for c in {0, 1})
    kappa = (po - pe) / (1 - pe) if pe != 1 else float("nan")
    return kappa, po, pe, agree


def load_llm(path: Path, column: str) -> dict[int, int]:
    labels: dict[int, int] = {}
    if not path.exists():
        return labels
    for i, r in enumerate(load(path)):
        c = parse_correct(r.get(column))
        if c is not None:
            labels[i] = c
    return labels


def main() -> int:
    a_rows, b_rows = load(RATER_A), load(RATER_B)
    if len(a_rows) != len(b_rows):
        print(f"WARNING: row count differs (a={len(a_rows)}, b={len(b_rows)})")

    # Align by composite key; fall back to row order if keys are unpopulated.
    b_by_key = {row_key(r): r for r in b_rows}
    aligned: list[tuple[dict, dict]] = []
    if all(row_key(r) in b_by_key for r in a_rows) and len(b_by_key) == len(b_rows):
        aligned = [(r, b_by_key[row_key(r)]) for r in a_rows]
    else:
        print("NOTE: composite-key alignment failed; aligning by row order.")
        aligned = list(zip(a_rows, b_rows))

    total = len(aligned)
    a_filled = sum(1 for r in a_rows if parse_correct(r.get("is_correct")) is not None)
    b_filled = sum(1 for r in b_rows if parse_correct(r.get("is_correct")) is not None)
    print(f"Sample size            = {total} detections")
    print(f"is_correct filled      = rater_a {a_filled}/{len(a_rows)}, "
          f"rater_b {b_filled}/{len(b_rows)}")

    # ---- LLM automated cross-check (available independently of human labels) ----
    llm_labels = {
        "Claude": load_llm(CLAUDE, "claude_is_correct"),
        "Codex/GPT": load_llm(CODEX, "codex_is_correct"),
    }
    printed_llm_header = False
    for name, labels in llm_labels.items():
        if labels:
            if not printed_llm_header:
                print("\n[LLM cross-checks: transparent triangulation, NOT human raters]")
                printed_llm_header = True
            cc = sum(labels.values())
            print(f"  {name:9s} precision = {cc}/{len(labels)} = {cc / len(labels):.4f}")
    if llm_labels["Claude"] and llm_labels["Codex/GPT"]:
        common = sorted(set(llm_labels["Claude"]) & set(llm_labels["Codex/GPT"]))
        if common:
            xs = [llm_labels["Claude"][i] for i in common]
            ys = [llm_labels["Codex/GPT"][i] for i in common]
            k, po, _pe, agree = binary_kappa(xs, ys)
            print(f"  Claude vs Codex/GPT agreement = {po:.4f} ({agree}/{len(common)}), "
                  f"kappa = {k:.4f}")

    pairs = [
        (parse_correct(ra.get("is_correct")), parse_correct(rb.get("is_correct")))
        for ra, rb in aligned
    ]
    both = [(a, b) for a, b in pairs if a is not None and b is not None]
    if not both:
        print("\nNot enough labels yet to compute kappa. Fill is_correct in both "
              "rater files and re-run.")
        return 0

    # ---- Cohen's kappa on the binary is_correct judgement ----
    n = len(both)
    agree = sum(1 for a, b in both if a == b)
    po = agree / n
    labels = {0, 1}
    kappa, po, pe, agree = binary_kappa([a for a, _ in both], [b for _, b in both])
    print(f"\nN (both raters labeled) = {n}")
    print(f"Raw agreement Po        = {po:.4f} ({agree}/{n})")
    print(f"Expected agreement Pe   = {pe:.4f}")
    print(f"Cohen's kappa           = {kappa:.4f}")

    # ---- Reconciled label for precision ----
    reconciled: dict[int, int] = {}   # index -> reconciled is_correct
    disagreements = []
    cons_correct: dict[tuple, int] = {}
    if CONSENSUS.exists():
        for r in load(CONSENSUS):
            c = parse_correct(r.get("is_correct"))
            if c is not None:
                cons_correct[row_key(r)] = c
    for i, (ra, rb) in enumerate(aligned):
        a, b = parse_correct(ra.get("is_correct")), parse_correct(rb.get("is_correct"))
        cons = cons_correct.get(row_key(ra))
        if cons is not None:
            reconciled[i] = cons
        elif a is not None and a == b:
            reconciled[i] = a
        elif a is not None and b is not None and a != b:
            disagreements.append(i)

    if disagreements:
        print(f"\n{len(disagreements)} rater disagreement(s) need third-annotator "
              f"resolution (fill is_correct in {CONSENSUS.name}); "
              f"precision below uses only resolved rows.")

    rec_idx = sorted(reconciled)
    if rec_idx:
        n_rec = len(rec_idx)
        n_corr = sum(reconciled[i] for i in rec_idx)
        print(f"\nReconciled rows         = {n_rec}")
        print(f"Mean test-file precision = {n_corr / n_rec:.4f} ({n_corr}/{n_rec})")

        per_type_tot: dict[str, int] = defaultdict(int)
        per_type_ok: dict[str, int] = defaultdict(int)
        for i in rec_idx:
            t = aligned[i][0].get("rm_type", "?")
            per_type_tot[t] += 1
            per_type_ok[t] += reconciled[i]
        print("\nPer-rm_type precision (flagging < 0.70 exclusion threshold):")
        for t in sorted(per_type_tot, key=lambda x: per_type_ok[x] / per_type_tot[x]):
            p = per_type_ok[t] / per_type_tot[t]
            flag = "  <-- below 70%" if p < 0.70 else ""
            print(f"  {p:5.2f}  ({per_type_ok[t]:2d}/{per_type_tot[t]:2d})  {t}{flag}")

        # ---- human (reconciled) vs LLM agreement: transparent cross-check stats ----
        for name, labels in llm_labels.items():
            common = [i for i in rec_idx if i in labels]
            if common:
                hv = [reconciled[i] for i in common]
                lv = [labels[i] for i in common]
                kappa_hl, po, _pe, agree_hl = binary_kappa(hv, lv)
                print(f"\nHuman(reconciled) vs {name} cross-check (n={len(common)}):")
                print(f"  raw agreement = {po:.4f} ({agree_hl}/{len(common)})")
                print(f"  Cohen's kappa = {kappa_hl:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
