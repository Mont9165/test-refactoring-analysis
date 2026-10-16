"""Detect the JDK version a Maven / Gradle module needs to compile.

Used by run_pit_jacoco.sh to pick the right Docker image:
  - 8       → eclipse-temurin:8 (Maven install only); PIT runs under JDK 17
  - 11      → eclipse-temurin:11 end-to-end
  - 17      → maven:3.9.9-eclipse-temurin-17 (default)
  - unknown → fall back to default (JDK 17)

For Maven, parses (in priority order):
  - <maven.compiler.release>
  - <maven.compiler.source>
  - <maven.compiler.target>
  - <source> inside maven-compiler-plugin
  - parent pom (one level up only)
For Gradle, parses:
  - sourceCompatibility = JavaVersion.VERSION_X
  - sourceCompatibility = "X"
  - targetCompatibility = ...
  - java { sourceCompatibility = ... }

The script prints a single line: "8" / "11" / "17" / "21" / "unknown".
The caller can map "8" → "eclipse-temurin:8-jdk-alpine" etc.

Usage:
    python detect_jdk_version.py <pom_or_gradle_path>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


# Map property values like "1.8", "8", "11", "17", "21" → canonical "8" "11" ...
def normalise(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    # Gradle JavaVersion enum: VERSION_1_8 / VERSION_11 / VERSION_17 / VERSION_HIGHER...
    m = re.match(r"VERSION_1_(\d+)$", s)   # VERSION_1_8 -> 8
    if m:
        return m.group(1)
    m = re.match(r"VERSION_(\d+)$", s)     # VERSION_11 -> 11
    if m:
        return m.group(1)
    s = re.sub(r"^1\.", "", s)             # "1.8" -> "8"
    if s.isdigit():
        return s
    return None


def detect_pom(pom_path: Path) -> str | None:
    """Return canonical version (e.g. '8') or None if undetected."""
    try:
        text = pom_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    # Strip XML namespaces for robust XPath.
    text_no_ns = re.sub(r' xmlns(:\w+)?="[^"]*"', "", text)

    # Try parsing as XML (some poms have BOMs or stray declarations).
    try:
        root = ET.fromstring(text_no_ns)
    except ET.ParseError:
        # Fallback: regex-based extraction.
        return _detect_pom_regex(text)

    # Common property names.
    properties = root.find("properties")
    if properties is not None:
        for tag in ("maven.compiler.release",
                    "maven.compiler.target",
                    "maven.compiler.source",
                    "java.version",
                    "release.compile",
                    "jdk.version"):
            el = properties.find(tag)
            if el is not None and el.text:
                v = normalise(el.text)
                if v:
                    return v

    # maven-compiler-plugin <configuration>
    for plugin in root.iter("plugin"):
        aid = plugin.find("artifactId")
        if aid is None or aid.text != "maven-compiler-plugin":
            continue
        cfg = plugin.find("configuration")
        if cfg is None:
            continue
        for tag in ("release", "target", "source"):
            el = cfg.find(tag)
            if el is not None and el.text:
                v = normalise(el.text)
                if v:
                    return v

    return None


def _detect_pom_regex(text: str) -> str | None:
    """Last-resort regex fallback when XML parsing fails."""
    for pat in (
        r"<maven\.compiler\.release>([^<]+)</maven\.compiler\.release>",
        r"<maven\.compiler\.target>([^<]+)</maven\.compiler\.target>",
        r"<maven\.compiler\.source>([^<]+)</maven\.compiler\.source>",
        r"<java\.version>([^<]+)</java\.version>",
        r"<release>([^<]+)</release>",
        r"<target>([^<]+)</target>",
        r"<source>([^<]+)</source>",
    ):
        m = re.search(pat, text)
        if m:
            v = normalise(m.group(1))
            if v:
                return v
    return None


def detect_gradle(build_path: Path) -> str | None:
    try:
        text = build_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    for pat in (
        r"sourceCompatibility\s*[=:]\s*(?:JavaVersion\.)?[\"']?([\w._]+)[\"']?",
        r"targetCompatibility\s*[=:]\s*(?:JavaVersion\.)?[\"']?([\w._]+)[\"']?",
        r"languageVersion\s*[=:]\s*JavaLanguageVersion\.of\s*\(\s*(\d+)\s*\)",
        r"jvmTarget\s*[=:]\s*[\"']?([\w._]+)[\"']?",
    ):
        m = re.search(pat, text)
        if m:
            v = normalise(m.group(1))
            if v:
                return v
    return None


def detect(path: Path) -> str:
    name = path.name.lower()
    v: str | None
    if name == "pom.xml":
        v = detect_pom(path)
        # If the module pom doesn't say, climb to the parent dir's pom.
        if v is None:
            parent_pom = path.parent.parent / "pom.xml"
            if parent_pom.exists() and parent_pom != path:
                v = detect_pom(parent_pom)
    elif name in ("build.gradle", "build.gradle.kts"):
        v = detect_gradle(path)
    else:
        v = None
    return v or "unknown"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: detect_jdk_version.py <pom_or_gradle_path>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print("unknown")
        return 0
    print(detect(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
