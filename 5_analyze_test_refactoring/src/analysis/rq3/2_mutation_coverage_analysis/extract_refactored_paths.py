"""Extract per-commit metadata needed to drive PIT/JaCoCo from the RefactorHub
annotation CSV.

For each commit_url, emit:
- owner, repo, sha
- one or more "modules" (Maven module paths derived from file locations)
- per-module: test_classes (FQNs), production_globs (PIT targetClasses glob),
  test_paths (relative paths)

Memo guidance: target classes for PIT are restricted to production classes
corresponding to the refactored test files (not the whole module).

Usage:
    # one commit, JSON to stdout
    python extract_refactored_paths.py \
        --csv .../refactoring_data_2025-02-19.csv \
        --commit-url https://github.com/apache/jspwiki/commit/62857b9...

    # all commits, JSON keyed by commit_url
    python extract_refactored_paths.py \
        --csv .../refactoring_data_2025-02-19.csv \
        --output commit_metadata.json
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

COMMIT_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/commit/(?P<sha>[0-9a-f]{7,40})"
)
TEST_SUFFIXES = ("ITCase", "Tests", "Test", "IT")  # order matters: longest first
TEST_PREFIXES = ("Test", "IT")  # "TestFoo" / "ITFoo" naming convention
MODULE_SPLIT_MARKERS = (
    "/src/test/java/",
    "/src/main/java/",
    "/src/test/kotlin/",
    "/src/main/kotlin/",
    "/src/test/",
    "/src/main/",
)
SKIP_TYPES = {"Non-Refactoring", "Any Refactoring", ""}


def parse_paths_and_classes(parameter_data: str) -> tuple[set[str], set[str]]:
    """Return (paths, fqns) extracted from RefactorHub `parameter_data`."""
    if not parameter_data or parameter_data.strip() == "{}":
        return set(), set()
    try:
        data = ast.literal_eval(parameter_data)
    except (SyntaxError, ValueError):
        return set(), set()
    paths: set[str] = set()
    fqns: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            elements = node.get("elements")
            if isinstance(elements, list):
                for el in elements:
                    if not isinstance(el, dict):
                        continue
                    cn = el.get("className")
                    if isinstance(cn, str) and cn.strip():
                        fqns.add(cn.strip())
                    loc = el.get("location")
                    if isinstance(loc, dict):
                        p = loc.get("path")
                        if isinstance(p, str) and p.strip():
                            paths.add(p.strip())
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return paths, fqns


def production_glob_from_simple(simple_name: str) -> str | None:
    """Strip the longest matching test affix from a simple class name.

    Examples (suffix convention):
        WorkflowManagerTest -> WorkflowManager*
        AuthenticationTests -> Authentication*
        FooITCase           -> Foo*
        FooIT               -> Foo*
    Examples (prefix convention):
        TestBytecodeLoader   -> BytecodeLoader*
        ITFoo                -> Foo*
    Returns None if no test affix is found.
    """
    base = simple_name.split("$", 1)[0]  # drop inner-class part
    for suf in TEST_SUFFIXES:
        if base.endswith(suf) and len(base) > len(suf):
            return base[: -len(suf)] + "*"
    for pre in TEST_PREFIXES:
        if base.startswith(pre) and len(base) > len(pre) and base[len(pre)].isupper():
            return base[len(pre):] + "*"
    return None


def _path_to_fqn(path: str) -> str | None:
    """Derive a Java FQN from a source-file path under .../src/{test,main}/{java,kotlin}/...

    Returns None when the path does not contain a recognized source-root marker.
    """
    for marker in ("/src/test/java/", "/src/main/java/",
                   "/src/test/kotlin/", "/src/main/kotlin/"):
        idx = path.find(marker)
        if idx < 0:
            continue
        rel = path[idx + len(marker):]
        if rel.endswith(".java") or rel.endswith(".kt"):
            rel = rel.rsplit(".", 1)[0]
        return rel.replace("/", ".")
    return None


def fqn_to_production_globs(fqn: str) -> list[str]:
    """Convert test FQN to PIT production-class globs.

    Returns a list of globs to use as PIT `targetClasses`:
    - The narrow class glob (e.g., `org.apache.wiki.workflow.WorkflowManager*`)
      covers `WorkflowManager` and any class starting with that name.
    - The package glob (e.g., `org.apache.wiki.workflow.*`) is added because
      tests typically exercise helper classes in the same package and because
      the narrowly-named class is sometimes an interface (PIT cannot mutate
      interfaces and reports "No mutations found" if the narrow glob matches
      only an interface).

    PIT accepts comma-separated globs in `-DtargetClasses=`, so emitting both
    is safe and resolves the most common "0 mutation units" failure mode.
    """
    base = fqn.split("$", 1)[0]
    if "." in base:
        package, simple = base.rsplit(".", 1)
    else:
        package, simple = "", base
    out: list[str] = []
    glob_simple = production_glob_from_simple(simple)
    if glob_simple:
        out.append(f"{package}.{glob_simple}" if package else glob_simple)
    if package:
        out.append(f"{package}.*")
    return out


def module_from_path(path: str) -> str:
    """Extract Maven module path (prefix before /src/test/java/ or similar)."""
    for marker in MODULE_SPLIT_MARKERS:
        if marker in path:
            return path.split(marker, 1)[0]
    return ""


def simple_name_of_fqn(fqn: str) -> str:
    base = fqn.split("$", 1)[0]
    return base.rsplit(".", 1)[-1]


def build_metadata(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in rows:
        url = (r.get("url") or "").strip()
        if not url:
            continue
        m = COMMIT_URL_RE.match(url)
        if not m:
            continue
        if (r.get("type_name") or "").strip() in SKIP_TYPES:
            continue
        paths, fqns = parse_paths_and_classes(r.get("parameter_data", ""))
        if not paths and not fqns:
            continue

        rec = out.setdefault(
            url,
            {
                "commit_url": url,
                "owner": m.group("owner"),
                "repo": m.group("repo"),
                "sha": m.group("sha"),
                "_modules": defaultdict(
                    lambda: {
                        "test_classes": set(),
                        "production_globs": set(),
                        "test_paths": set(),
                    }
                ),
            },
        )

        # Collect (path, fqn) pairs by inferring module from path; if no path
        # accompanies a fqn, fall back to root module.
        path_by_simple_name: dict[str, str] = {}
        for p in paths:
            base = Path(p).stem  # filename without extension
            path_by_simple_name.setdefault(base, p)

        for p in paths:
            module = module_from_path(p)
            rec["_modules"][module]["test_paths"].add(p)

        # Augment fqns with FQNs derived from paths when the className field
        # is missing or absent (some RefactorHub annotations do not record it).
        path_derived_fqns: set[str] = set()
        for p in paths:
            derived = _path_to_fqn(p)
            if derived and derived not in fqns:
                path_derived_fqns.add(derived)
        all_fqns = fqns | path_derived_fqns

        for fqn in all_fqns:
            simple = simple_name_of_fqn(fqn)
            associated_path = path_by_simple_name.get(simple)
            if associated_path:
                module = module_from_path(associated_path)
            else:
                module = next(iter(rec["_modules"].keys()), "")
            entry = rec["_modules"][module]
            entry["test_classes"].add(fqn)
            for glob in fqn_to_production_globs(fqn):
                entry["production_globs"].add(glob)

    # Finalize: convert sets/defaultdicts to lists/dicts.
    final: dict[str, dict] = {}
    for url, rec in out.items():
        modules_list = []
        for mod, info in rec["_modules"].items():
            modules_list.append(
                {
                    "module_path": mod,
                    "test_classes": sorted(info["test_classes"]),
                    "production_globs": sorted(info["production_globs"]),
                    "test_paths": sorted(info["test_paths"]),
                }
            )
        modules_list.sort(key=lambda x: x["module_path"])
        final[url] = {
            "commit_url": rec["commit_url"],
            "owner": rec["owner"],
            "repo": rec["repo"],
            "sha": rec["sha"],
            "modules": modules_list,
        }
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--commit-url", help="emit JSON for one commit")
    ap.add_argument("--output", type=Path, help="write all metadata to JSON file")
    args = ap.parse_args()

    with args.csv.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    metadata = build_metadata(rows)

    if args.commit_url:
        rec = metadata.get(args.commit_url.strip())
        if not rec:
            print(f"[error] no metadata for commit_url {args.commit_url}", file=sys.stderr)
            return 1
        json.dump(rec, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    if args.output:
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"[done] {len(metadata)} commits -> {args.output}", file=sys.stderr)
        return 0

    json.dump(metadata, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
