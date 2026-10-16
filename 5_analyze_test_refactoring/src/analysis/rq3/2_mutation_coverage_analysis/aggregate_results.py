"""Aggregate per-commit PIT and JaCoCo XML reports into a single CSV ready for
the same Wilcoxon + Vargha-Delaney pipeline used in ../../test.py.

Outputs (when --wide-output is given):
- long-format CSV at --output: one row per (commit_url, side)
- wide-format CSV at --wide-output: one row per commit_url, with
  <metric>_before / <metric>_after columns + type_name from canonical csv

The --run-logs argument enables success-wins dedup: when the same
(commit_url, sha, side) appears in multiple run_log.csv files (e.g. an initial
run plus a retry pass), the row whose pit_ok is "true" wins. A failed retry
will never overwrite a previously-good measurement. Without --run-logs the
script falls back to its older XML-only behaviour driven by --buildable.

Usage:
    python aggregate_results.py \
        --output-root ./output \
        --run-logs run_log.csv,run_log_retry.csv \
        --output ./mutation_coverage_results.csv \
        --wide-output ./mutation_coverage_wide.csv \
        --canonical-csv ../1_analyze_testsmell_diff/file_level_wide.csv

    # Legacy (no run-log dedup):
    python aggregate_results.py --output-root ./output \
        --buildable ./buildable_commits.csv ...
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


def parse_pit(report_dir: Path) -> dict[str, int | float]:
    xml = report_dir / "mutations.xml"
    if not xml.exists():
        return {}
    try:
        root = ET.parse(xml).getroot()
    except ET.ParseError as e:
        print(f"[warn] could not parse {xml}: {e}", file=sys.stderr)
        return {}
    killed = survived = no_cov = total = 0
    for m in root.iter("mutation"):
        total += 1
        status = m.get("status", "")
        if status == "KILLED":
            killed += 1
        elif status == "SURVIVED":
            survived += 1
        elif status in {"NO_COVERAGE", "NON_VIABLE", "MEMORY_ERROR", "RUN_ERROR", "TIMED_OUT"}:
            no_cov += 1
    return {
        "mutations_total": total,
        "mutations_killed": killed,
        "mutations_survived": survived,
        "mutations_no_coverage": no_cov,
        "mutation_score": (killed / total) if total else 0.0,
    }


def parse_jacoco(report_dir: Path) -> dict[str, float]:
    xml = report_dir / "jacoco.xml"
    if not xml.exists():
        return {}
    try:
        root = ET.parse(xml).getroot()
    except ET.ParseError as e:
        print(f"[warn] could not parse {xml}: {e}", file=sys.stderr)
        return {}
    out: dict[str, float] = {}
    for counter in root.findall("counter"):
        ctype = counter.get("type", "").lower()
        covered = int(counter.get("covered", 0))
        missed = int(counter.get("missed", 0))
        denom = covered + missed
        if denom == 0:
            continue
        out[f"{ctype}_coverage"] = covered / denom
    return out


def load_run_logs_with_dedup(run_log_paths: list[Path]) -> list[dict]:
    """Load multiple run_log.csv files, applying success-wins dedup.

    For each (commit_url, sha, side), keep the row whose pit_ok == "true" if
    any such row exists; otherwise keep the most recently appended row. This
    ensures a flaky retry that fails to produce a report never overwrites a
    previously-recorded successful measurement.
    """
    def score(r: dict) -> tuple[int, int, int]:
        # Lexicographic preference: pit_ok > jacoco_ok > build_ok > anything.
        return (
            1 if r.get("pit_ok") == "true" else 0,
            1 if r.get("jacoco_ok") == "true" else 0,
            1 if r.get("build_ok") == "true" else 0,
        )
    by_key: dict[tuple[str, str, str], dict] = {}
    for p in run_log_paths:
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                key = (r.get("commit_url", ""), r.get("sha", ""), r.get("side", ""))
                existing = by_key.get(key)
                if existing is None or score(r) > score(existing):
                    by_key[key] = r
    return list(by_key.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", required=True, type=Path,
                    help="root dir produced by run_pit_jacoco.sh (one subdir per SHA)")
    ap.add_argument("--buildable", type=Path, default=None,
                    help="legacy: buildable_commits.csv from select_buildable_subset.py "
                         "(used only when --run-logs is absent)")
    ap.add_argument("--run-logs", default=None,
                    help="comma-separated list of run_log.csv files. When given, "
                         "applies success-wins dedup and emits one row per "
                         "(commit_url, sha, side) with pit_ok=true.")
    ap.add_argument("--output", required=True, type=Path,
                    help="long-format CSV (one row per side)")
    ap.add_argument("--wide-output", type=Path, default=None,
                    help="wide-format CSV (one row per commit_url) with _before/_after columns")
    ap.add_argument("--canonical-csv", type=Path, default=None,
                    help="canonical RQ3 CSV (file_level_wide.csv) for joining type_name")
    ap.add_argument("--tier", choices=("A", "B"), default="A",
                    help="A = pit_ok=true required (Tier A: PIT+coverage); "
                         "B = jacoco_ok=true required, pit_ok ignored (Tier B: "
                         "coverage only). Used to produce a larger-n line/branch "
                         "coverage subset that does not require PIT to have run.")
    args = ap.parse_args()

    rows: list[dict] = []
    if args.run_logs:
        log_paths = [Path(p.strip()) for p in args.run_logs.split(",") if p.strip()]
        deduped = load_run_logs_with_dedup(log_paths)
        gate_field = "pit_ok" if args.tier == "A" else "jacoco_ok"
        for r in deduped:
            if r.get(gate_field) != "true":
                continue   # only successful sides feed the metrics pivot
            sha = r.get("sha", "")
            side = r.get("side", "")
            url = r.get("commit_url", "")
            if side not in ("before", "after") or not sha or not url:
                continue
            d = args.output_root / sha
            metrics = {**parse_pit(d / "pit"), **parse_jacoco(d / "jacoco")}
            project = ""
            m = url.replace("https://github.com/", "").split("/commit/")[0]
            if "/" in m:
                project = m
            rows.append({
                "commit_url": url,
                "project": project,
                "sha": sha,
                "side": side,
                "recovery_layer_used": r.get("recovery_layer_used", "none") or "none",
                "jdk_version": r.get("jdk_version", "unknown") or "unknown",
                **metrics,
            })
    else:
        if args.buildable is None:
            print("[error] either --run-logs or --buildable is required", file=sys.stderr)
            return 2
        with args.buildable.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                for side, sha_field in (("before", "parent_sha"), ("after", "sha")):
                    sha = r.get(sha_field)
                    if not sha:
                        continue
                    d = args.output_root / sha
                    metrics = {**parse_pit(d / "pit"), **parse_jacoco(d / "jacoco")}
                    rows.append({
                        "commit_url": r["commit_url"],
                        "project": f'{r["owner"]}/{r["repo"]}',
                        "sha": sha,
                        "side": side,
                        "recovery_layer_used": "none",
                        "jdk_version": "unknown",
                        **metrics,
                    })

    fieldnames = sorted({k for r in rows for k in r.keys()})
    fieldnames = ["commit_url", "project", "sha", "side"] + [c for c in fieldnames if c not in ("commit_url", "project", "sha", "side")]
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"[done] long: {len(rows)} rows -> {args.output}")

    if args.wide_output:
        # Pivot long → wide. One row per commit_url.
        # Each metric becomes <metric>_before / <metric>_after.
        # Skip rows with `side` ∉ {before, after}.
        metric_cols = [c for c in fieldnames
                       if c not in ("commit_url", "project", "sha", "side")
                       and not c.endswith(("_before", "_after"))]

        per_url: dict[str, dict[str, object]] = defaultdict(dict)
        for r in rows:
            url = r["commit_url"]
            side = r.get("side")
            if side not in ("before", "after"):
                continue
            target = per_url[url]
            target.setdefault("commit_url", url)
            target.setdefault("project", r.get("project", ""))
            target[f"sha_{side}"] = r.get("sha", "")
            for m in metric_cols:
                if m in r:
                    target[f"{m}_{side}"] = r[m]

        # Optional join: type_name from the canonical RQ3 CSV.
        if args.canonical_csv and args.canonical_csv.exists():
            type_by_url: dict[str, set[str]] = defaultdict(set)
            with args.canonical_csv.open(encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    type_by_url[row["commit_url"]].add(row["type_name"])
            for url, target in per_url.items():
                target["type_name"] = ";".join(sorted(type_by_url.get(url, [])))

        # Build column order: keys, sha_before/after, metric_before/after pairs, type_name.
        wide_cols = ["commit_url", "project", "sha_before", "sha_after"]
        for m in metric_cols:
            wide_cols.extend([f"{m}_before", f"{m}_after"])
        if args.canonical_csv and args.canonical_csv.exists():
            wide_cols.append("type_name")

        # Filter to fully-paired commits (both sha_before AND sha_after present).
        # The downstream Wilcoxon pipeline expects paired data; partial-pair rows
        # would contaminate the row count even though test.py drops them via NaN.
        paired = {url: row for url, row in per_url.items()
                  if row.get("sha_before") and row.get("sha_after")}

        with args.wide_output.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=wide_cols, extrasaction="ignore")
            w.writeheader()
            for url in sorted(paired):
                w.writerow(paired[url])

        skipped = len(per_url) - len(paired)
        print(f"[done] wide: {len(paired)} paired rows -> {args.wide_output}"
              + (f"  ({skipped} partial-pair rows dropped)" if skipped else ""))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
