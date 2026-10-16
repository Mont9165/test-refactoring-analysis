"""R4-2 helper: auto-suggest `trigger_category` candidates from the
commit message + PR text in `socio_technical_annotation.csv`.

For each row this script scans all text fields with keyword regexes
mapped to the project's trigger taxonomy, and emits two new columns:
  - `auto_hint_category` — comma-separated candidate categories,
                            ranked by total match weight (most likely first).
  - `auto_hint_evidence` — first matching snippet per category, separated
                            by ' | '.

This is **a starting point for the human annotator**, not ground truth.
The annotator should still read the commit / PR text and make the final
call. Auto hints accelerate the work and make inter-rater agreement
testable (compute Cohen's κ between auto-hint and human, then between
two humans, to characterise the auto-hint baseline).

Usage:
    python auto_hint_triggers.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Iterable

THIS_DIR = Path(__file__).resolve().parent
INPUT_CSV = THIS_DIR / "socio_technical_annotation.csv"
OUTPUT_CSV = THIS_DIR / "socio_technical_annotation_with_hints.csv"

TEXT_FIELDS = [
    "commit_subject", "commit_body",
    "pr_title", "pr_body",
    "pr_comments_excerpt", "pr_reviews_excerpt",
]

# Category rules using the literature-grounded taxonomy in
# revision/R4-2_taxonomy.md. Each rule maps a pattern to (Tier 1 category,
# optional Tier 2 sub-code, weight). The script picks Tier 1 by total
# weight; Tier 2 is reported as a comma-separated list of matched sub-codes.
KEYWORD_RULES: list[tuple[str, list[tuple[str, str, int]]]] = [
    ("bug_fix", [
        (r"\bflak(y|e|iness)\b", "flaky_test", 3),
        (r"\bintermittent(ly)?\b", "flaky_test", 3),
        (r"\bnon[-\s]?deterministic\b", "flaky_test", 3),
        (r"\brace condition\b", "flaky_test", 3),
        (r"\bunstable test", "flaky_test", 3),
        (r"\b(passes|fails) intermittently\b", "flaky_test", 3),
        (r"\bunreliable\b", "flaky_test", 2),
        (r"\bbroken test", "broken_test", 3),
        (r"\bfailing test", "broken_test", 3),
        (r"\btest(s)? (fail|broke|broken)\b", "broken_test", 3),
        (r"\bfix(ed|es)? broken\b", "broken_test", 2),
        (r"\bregression\b", "regression", 2),
        (r"\bfix(ed|es)? #\d+", "regression", 2),
        (r"\bfix(ed|es)? test\b", "broken_test", 2),
        (r"\bincorrect (assert|expectation|oracle)", "incorrect_oracle", 3),
    ]),
    ("address_review_feedback", [
        (r"\bcode review\b", "pr_comment", 3),
        (r"\b(addressed|address) (the )?(review |reviewer |feedback)", "pr_comment", 3),
        (r"\bas (suggested|requested) by", "as_suggested", 2),
        (r"\bper review\b", "pr_comment", 2),
        (r"\bPR (comment|feedback)", "pr_comment", 2),
        (r"\breviewer (comment|suggestion|note)", "pr_comment", 2),
        (r"\bstyle conformity\b", "style_conformity", 2),
    ]),
    ("improve_maintainability", [
        (r"\bDRY\b", "dry_duplication", 3),
        (r"\bduplicat(e|ion|ed)\b", "dry_duplication", 2),
        (r"\bclean[\s-]?up\b", "cleanup_dead_code", 2),
        (r"\bsimplif(y|ied|ies|ying)\b", "simplify_setup", 2),
        (r"\bmaintain(ability|able)\b", "", 3),
        (r"\btidy\b|\btidier\b", "", 2),
        (r"\brefactor(ing|ed)? for (clarity|readability|simplicity)", "", 3),
        (r"\bextract (helper|method|class)\b", "consolidate_helpers", 1),
        (r"\bfixture (reuse|sharing|consolidat)", "fixture_reuse", 3),
    ]),
    ("improve_comprehension", [
        (r"\breadabilit(y|ies)\b", "intent", 3),
        (r"\bmore expressive\b", "assertion_clarity", 2),
        (r"\bself[-\s]?documenting\b", "intent", 3),
        (r"\bclarif(y|ied|ying)\b", "intent", 2),
        (r"\bnaming\b", "naming", 2),
        (r"\bverbose\b", "verbosity", 2),
    ]),
    ("improve_performance", [
        (r"\bspeed up\b", "ci_speed", 3),
        (r"\bslow test\b", "ci_speed", 3),
        (r"\bCI (failure|failing|red|broken)\b", "ci_speed", 3),
        (r"\b(timeout|timed out)\b", "timeout_avoidance", 2),
        (r"\bbuild (failure|failing|red)\b", "ci_speed", 2),
        (r"\bperformance\b", "ci_speed", 2),
        (r"\b(jenkins|travis|github actions|circleci)\b", "ci_speed", 1),
        (r"\bparalleli[sz]e\b", "parallelism", 2),
    ]),
    ("remove_code_smell", [
        (r"\btest smell\b", "", 3),
        (r"\bcode smell\b", "", 3),
        (r"\banti[\s-]?pattern\b", "", 2),
        (r"\bsonar(qube|cloud|lint)\b", "sonarqube_warning", 3),
        (r"\bassertion roulette\b", "assertion_roulette", 3),
        (r"\bmagic number\b", "magic_number_test", 3),
        (r"\bduplicate assert\b", "duplicate_assert", 3),
        (r"\bmystery guest\b", "mystery_guest", 3),
        (r"\beager test\b", "eager_test", 3),
        (r"\blazy test\b", "lazy_test", 3),
        (r"\bgeneral fixture\b", "general_fixture", 3),
        (r"\bobscure test\b", "obscure_test", 3),
        (r"\bconditional test logic\b", "conditional_test_logic", 3),
    ]),
    ("modernize_test_framework", [
        (r"\bjunit\s*5\b|\bjupiter\b", "junit4_to_junit5", 3),
        (r"\bmigrat(e|ion|ing) (to )?junit", "junit4_to_junit5", 3),
        (r"\bassertThrows?\b", "try_catch_to_assertthrows", 3),
        (r"\bparameteri[sz]ed test\b", "parameterise", 3),
        (r"\bassertJ\b|\bassertj\b", "assertj_adoption", 3),
        (r"\blambda(rize|-rize|s)\b", "lambda_fixture", 2),
        (r"\bmodern(ize|ization)\b", "", 2),
    ]),
    ("improve_test_isolation", [
        (r"\bmock(s|ing|ed)?\b", "simplify_mocking", 1),
        (r"\btest double", "replace_dependency_with_double", 3),
        (r"\bawaitility\b|\bawait\b", "awaitility_for_async", 2),
        (r"\bisolat(e|ion|ing)\b", "", 2),
        (r"\b(remove|delete|drop) (unused )?mock", "delete_unused_mock", 3),
    ]),
    ("sync_with_production", [
        (r"\bfollow[\s-]?up to\b", "rename_follow", 3),
        (r"\bafter (rename|moving|extracting)", "rename_follow", 3),
        (r"\bsync (test|tests) with\b", "api_migration", 3),
        (r"\bupdate test(s)? (after|for) (rename|move|extract)", "rename_follow", 3),
        (r"\bfollow(s)? refactor", "rename_follow", 3),
        (r"\bAPI (migration|change)\b", "api_migration", 3),
    ]),
    ("support_feature", [
        (r"\badd(ed|s)? (a |new )?test", "new_test_for_feature", 2),
        (r"\bnew test", "new_test_for_feature", 2),
        (r"\btest(s)? for (a )?new", "new_test_for_feature", 3),
        (r"\bcoverage for\b", "new_test_for_feature", 2),
        (r"\bimplement(ed|s|ation)\b", "new_test_for_feature", 1),
        (r"\bsupport for\b", "update_for_changed_api", 1),
        (r"\b(intro|introduc)(e|ed|ing)\b", "new_test_for_feature", 1),
    ]),
]


def find_matches(text: str, rules: list[tuple[str, str, int]]) -> tuple[int, list[tuple[str, str]], set[str]]:
    """Return (total_weight, [(snippet, subcode), ...], {subcodes})."""
    if not text:
        return 0, [], set()
    total = 0
    evidence: list[tuple[str, str]] = []
    seen_offsets: set[int] = set()
    subcodes: set[str] = set()
    for pattern, subcode, weight in rules:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            total += weight
            if subcode:
                subcodes.add(subcode)
            key = m.start() // 50
            if key in seen_offsets:
                continue
            seen_offsets.add(key)
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 50)
            snippet = text[start:end].replace("\n", " ").strip()
            evidence.append((snippet, subcode))
    return total, evidence, subcodes


def hint_for_row(row: dict) -> tuple[str, str, str]:
    """Aggregate matches across all text fields, rank Tier 1 categories,
    return (auto_hint_category_csv, auto_hint_subcodes_csv, evidence_str).
    The Tier 1 winner appears first in auto_hint_category; further
    matched categories follow in order of weight.
    """
    blob = "\n\n".join(str(row.get(f, "") or "") for f in TEXT_FIELDS)
    cat_scores: list[tuple[str, int, list[tuple[str, str]], set[str]]] = []
    for category, rules in KEYWORD_RULES:
        weight, evidence, subcodes = find_matches(blob, rules)
        if weight > 0:
            cat_scores.append((category, weight, evidence, subcodes))
    if not cat_scores:
        return "not_documented", "", ""
    cat_scores.sort(key=lambda x: -x[1])
    cats = ",".join(c for c, _w, _e, _s in cat_scores)
    all_subcodes = sorted({s for _c, _w, _e, ss in cat_scores for s in ss})
    subcodes_str = ",".join(all_subcodes)
    # Evidence: best snippet per category.
    ev_parts: list[str] = []
    for c, _w, ev, _s in cat_scores:
        if ev:
            snippet, subcode = ev[0]
            tag = f"{c}:{subcode}" if subcode else c
            ev_parts.append(f"[{tag}] {snippet}")
    return cats, subcodes_str, " | ".join(ev_parts)


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"[error] {INPUT_CSV} not found", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(INPUT_CSV.open(encoding="utf-8")))
    if not rows:
        print("[error] empty CSV", file=sys.stderr)
        return 1
    print(f"[info] loaded {len(rows)} rows from {INPUT_CSV.name}")

    fieldnames = list(rows[0].keys())
    new_cols = ["auto_hint_category", "auto_hint_subcodes", "auto_hint_evidence"]
    insert_at = len(fieldnames)
    try:
        insert_at = fieldnames.index("trigger_category")
    except ValueError:
        pass
    keep_pre = [c for c in fieldnames[:insert_at] if c not in new_cols]
    keep_post = [c for c in fieldnames[insert_at:] if c not in new_cols]
    fieldnames = keep_pre + new_cols + keep_post

    counters: dict[str, int] = {}
    for r in rows:
        cats, subcodes, ev = hint_for_row(r)
        r["auto_hint_category"] = cats
        r["auto_hint_subcodes"] = subcodes
        r["auto_hint_evidence"] = ev
        primary = cats.split(",")[0] if cats else "not_documented"
        counters[primary] = counters.get(primary, 0) + 1

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"[done] wrote {len(rows)} rows -> {OUTPUT_CSV.name}")
    print("\nPrimary auto-hint category distribution:")
    for cat, c in sorted(counters.items(), key=lambda kv: -kv[1]):
        print(f"  {c:>4}  {cat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
