"""Detect test framework + build system from a project file.

Build system: Maven (pom.xml) or Gradle (build.gradle / build.gradle.kts).
Test framework: junit5 / junit4 / testng / unknown.

For Maven, walks the pom and any parent poms in the same repo. For Gradle,
greps the build script (and root build script if available) for known
dependency coordinates.

Usage:
    python detect_framework.py /abs/path/to/module/pom.xml
    # prints "<framework> <build_system>"
    # e.g. "junit5 maven", "junit4 gradle", "unknown gradle"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

POM_NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _strip_ns(text: str) -> str:
    return re.sub(r"\{[^}]+\}", "", text)


def iter_dependencies(pom_path: Path):
    try:
        tree = ET.parse(pom_path)
    except ET.ParseError:
        return
    root = tree.getroot()
    for dep in root.iter():
        if _strip_ns(dep.tag) != "dependency":
            continue
        gid = aid = ver = None
        for child in dep:
            tag = _strip_ns(child.tag)
            text = (child.text or "").strip() if child.text else ""
            if tag == "groupId":
                gid = text
            elif tag == "artifactId":
                aid = text
            elif tag == "version":
                ver = text
        if gid and aid:
            yield gid, aid, ver


def parent_pom_path(pom_path: Path) -> Path | None:
    """Return the local-filesystem location of the <parent> pom, if any."""
    try:
        tree = ET.parse(pom_path)
    except ET.ParseError:
        return None
    root = tree.getroot()
    for child in root:
        if _strip_ns(child.tag) != "parent":
            continue
        rel_path = None
        for sub in child:
            if _strip_ns(sub.tag) == "relativePath":
                rel_path = (sub.text or "").strip() if sub.text else ""
        # default relative path is "../pom.xml" if not specified
        if rel_path is None:
            rel_path = "../pom.xml"
        if not rel_path:
            return None
        candidate = (pom_path.parent / rel_path).resolve()
        if candidate.is_dir():
            candidate = candidate / "pom.xml"
        if candidate.exists() and candidate != pom_path:
            return candidate
        return None
    return None


def detect(pom_path: Path, max_depth: int = 5) -> str:
    visited: set[Path] = set()
    current: Path | None = pom_path.resolve()
    found_junit5 = found_junit4 = found_testng = False
    for _ in range(max_depth):
        if current is None or current in visited or not current.exists():
            break
        visited.add(current)
        for gid, aid, _ver in iter_dependencies(current):
            if gid == "org.junit.jupiter" and aid.startswith("junit-jupiter"):
                found_junit5 = True
            elif gid == "org.junit" and aid.startswith("junit-bom"):
                found_junit5 = True
            elif gid == "junit" and aid == "junit":
                found_junit4 = True
            elif gid == "org.testng" and aid == "testng":
                found_testng = True
        current = parent_pom_path(current)
    if found_junit5:
        return "junit5"
    if found_junit4:
        return "junit4"
    if found_testng:
        return "testng"
    return "unknown"


def detect_gradle(build_path: Path, max_depth: int = 5) -> str:
    """Detect test framework from a Gradle build script (and its parent if any)."""
    found_junit5 = found_junit4 = found_testng = False
    visited: set[Path] = set()
    current: Path | None = build_path.resolve()
    for _ in range(max_depth):
        if current is None or current in visited or not current.exists():
            break
        visited.add(current)
        try:
            text = current.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            break
        if re.search(r"org\.junit\.jupiter|junit-jupiter|useJUnitPlatform", text):
            found_junit5 = True
        if re.search(r"junit:junit:4|['\"]junit:junit['\"]", text):
            found_junit4 = True
        if re.search(r"testng", text, re.IGNORECASE):
            found_testng = True
        # Walk to project root build script
        parent_build = current.parent.parent
        candidates = [
            parent_build / "build.gradle",
            parent_build / "build.gradle.kts",
        ]
        next_path: Path | None = None
        for c in candidates:
            if c.exists() and c.resolve() not in visited:
                next_path = c
                break
        current = next_path
    if found_junit5:
        return "junit5"
    if found_junit4:
        return "junit4"
    if found_testng:
        return "testng"
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build_path", type=Path,
                    help="path to pom.xml, build.gradle, or build.gradle.kts")
    args = ap.parse_args()
    if not args.build_path.exists():
        print(f"[error] build file not found: {args.build_path}", file=sys.stderr)
        return 1
    name = args.build_path.name.lower()
    if name == "pom.xml":
        framework = detect(args.build_path)
        build_system = "maven"
    elif name in ("build.gradle", "build.gradle.kts"):
        framework = detect_gradle(args.build_path)
        build_system = "gradle"
    else:
        # Default: try pom-style parsing (shouldn't happen)
        framework = detect(args.build_path)
        build_system = "unknown"
    print(f"{framework} {build_system}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
