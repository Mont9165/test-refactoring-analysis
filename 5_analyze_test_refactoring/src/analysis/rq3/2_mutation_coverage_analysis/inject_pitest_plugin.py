"""Inject the pitest plugin into a project build script.

For Maven (pom.xml): inject a `<plugin>` block under `<build><plugins>`.
For Gradle (build.gradle / build.gradle.kts): append a `pitest { }` block
plus the plugin coordinate.

Reverting is done by the caller via `git checkout --`, not by this script.

Why namespace-aware string editing instead of ElementTree.write:
- ET reformats the entire pom (line endings, comments, attribute order),
  which makes `git diff` noisy and breaks `git checkout --` semantics for
  callers that want to revert.
- The injected block is appended *just before* `</plugins>` inside `<build>`,
  preserving everything else byte-for-byte.

If `<build>` exists but `<plugins>` is missing, we add it. If `<build>` is
missing entirely, we add `<build><plugins>...</plugins></build>` before
`</project>`.

Usage:
    python inject_pitest_plugin.py <pom_path> --framework junit5
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PIT_VERSION = "1.20.6"
PIT_JUNIT5_PLUGIN_VERSION = "1.2.3"
PIT_THREADS = "6"
PIT_HEAP = "10G"

# JDK 8 fallback line: PIT 1.15.x is the last that supports JDK 8 / Java 11+
# is required by 1.16+. Pair with the matching junit5-plugin version.
PIT_VERSION_JDK8 = "1.15.0"
PIT_JUNIT5_PLUGIN_VERSION_JDK8 = "1.2.0"


def make_plugin_block(framework: str, indent: str,
                       pit_version: str = PIT_VERSION,
                       junit5_plugin_version: str = PIT_JUNIT5_PLUGIN_VERSION) -> str:
    """Build the <plugin> block. `indent` is the string indent for `<plugin>` itself.

    Settings tuned per project's other-repo experience:
    - PIT 1.20.6 (better JDK 17/21 ASM support; bug fixes since 1.15.x).
    - --add-opens flags — required by Mockito and reflection-heavy frameworks
      (Spring Boot, JPA) under JDK 17+; fixes minion crashes seen on camunda.
    - -Xmx10G — large modules need more heap; default ~2G OOMs on big test suites.
    - threads=6 — substantially faster mutation analysis on multi-core hosts.
    - exportLineCoverage=true — PIT writes its own linecoverage.xml in the
      report dir, which we parse as a JaCoCo fallback when `mvn jacoco:report`
      fails (typical when -Dtest=<glob> aborts due to env / DB dependencies).
    - Multiple output formats (HTML/XML/CSV) for downstream tooling.
    """
    inner = indent + "  "
    deeper = inner + "  "
    deeper2 = deeper + "  "
    deps = ""
    if framework == "junit5":
        deps = (
            f"{inner}<dependencies>\n"
            f"{deeper}<dependency>\n"
            f"{deeper2}<groupId>org.pitest</groupId>\n"
            f"{deeper2}<artifactId>pitest-junit5-plugin</artifactId>\n"
            f"{deeper2}<version>{junit5_plugin_version}</version>\n"
            f"{deeper}</dependency>\n"
            f"{inner}</dependencies>\n"
        )
    config = (
        f"{inner}<configuration>\n"
        f"{deeper}<outputFormats>\n"
        f"{deeper2}<format>HTML</format>\n"
        f"{deeper2}<format>XML</format>\n"
        f"{deeper2}<format>CSV</format>\n"
        f"{deeper}</outputFormats>\n"
        f"{deeper}<exportLineCoverage>true</exportLineCoverage>\n"
        f"{deeper}<threads>{PIT_THREADS}</threads>\n"
        f"{deeper}<jvmArgs>\n"
        f"{deeper2}<arg>--add-opens=java.base/java.lang=ALL-UNNAMED</arg>\n"
        f"{deeper2}<arg>--add-opens=java.base/java.util=ALL-UNNAMED</arg>\n"
        f"{deeper2}<arg>--add-opens=java.base/java.time=ALL-UNNAMED</arg>\n"
        f"{deeper2}<arg>--add-opens=java.base/java.lang.reflect=ALL-UNNAMED</arg>\n"
        f"{deeper2}<arg>-Xmx{PIT_HEAP}</arg>\n"
        f"{deeper}</jvmArgs>\n"
        f"{inner}</configuration>\n"
    )
    return (
        f"{indent}<plugin>\n"
        f"{inner}<groupId>org.pitest</groupId>\n"
        f"{inner}<artifactId>pitest-maven</artifactId>\n"
        f"{inner}<version>{pit_version}</version>\n"
        f"{deps}"
        f"{config}"
        f"{indent}</plugin>\n"
    )


def inject(pom_text: str, framework: str,
            pit_version: str = PIT_VERSION,
            junit5_plugin_version: str = PIT_JUNIT5_PLUGIN_VERSION) -> str:
    """Insert the plugin block immediately before </plugins> (or create the
    enclosing <build>/<plugins> if missing). Indent is matched dynamically to
    whatever leading whitespace the existing closing tag has, so the result
    looks the same as if a developer had typed it.
    """
    # Case 1: existing <plugins> ... </plugins>
    m = re.search(r"\n([ \t]*)</plugins>", pom_text)
    if m:
        plugins_indent = m.group(1)
        plugin = make_plugin_block(framework, plugins_indent + "  ",
                                    pit_version, junit5_plugin_version)
        return pom_text[: m.start()] + "\n" + plugin + plugins_indent + "</plugins>" + pom_text[m.end():]

    # Case 2: <build> exists but no <plugins>
    m = re.search(r"\n([ \t]*)</build>", pom_text)
    if m:
        build_indent = m.group(1)
        plugins_indent = build_indent + "  "
        plugin = make_plugin_block(framework, plugins_indent + "  ",
                                    pit_version, junit5_plugin_version)
        block = (
            "\n"
            f"{plugins_indent}<plugins>\n"
            f"{plugin}"
            f"{plugins_indent}</plugins>\n"
            f"{build_indent}"
        )
        return pom_text[: m.start()] + block + "</build>" + pom_text[m.end():]

    # Case 3: no <build> — insert before </project>
    m = re.search(r"\n([ \t]*)</project>", pom_text)
    if m:
        project_indent = m.group(1)
        build_indent = project_indent + "  "
        plugins_indent = build_indent + "  "
        plugin = make_plugin_block(framework, plugins_indent + "  ",
                                    pit_version, junit5_plugin_version)
        block = (
            "\n"
            f"{build_indent}<build>\n"
            f"{plugins_indent}<plugins>\n"
            f"{plugin}"
            f"{plugins_indent}</plugins>\n"
            f"{build_indent}</build>\n"
            f"{project_indent}"
        )
        return pom_text[: m.start()] + block + "</project>" + pom_text[m.end():]

    raise SystemExit("[error] could not locate insertion point in pom (no </project>)")


PIT_GRADLE_PLUGIN_VERSION = "1.15.0"  # info.solidsoft.pitest gradle plugin (compatible with PIT 1.20.6)


def make_gradle_plugin_id_line(kotlin_dsl: bool) -> str:
    """The single line that registers the pitest plugin id+version."""
    if kotlin_dsl:
        return f'    id("info.solidsoft.pitest") version "{PIT_GRADLE_PLUGIN_VERSION}"\n'
    return f"    id 'info.solidsoft.pitest' version '{PIT_GRADLE_PLUGIN_VERSION}'\n"


def make_gradle_pitest_config(framework: str, kotlin_dsl: bool) -> str:
    """The pitest { ... } DSL block; appended at end of script.

    Bridges -PtargetClasses / -PtargetTests CLI properties into the plugin
    config (the info.solidsoft.pitest plugin doesn't auto-read project
    properties). Without this bridge, `./gradlew :mod:pitest -PtargetClasses=...`
    would fail with "property 'targetClasses' doesn't have a configured value".
    """
    junit5_dep = ""
    if framework == "junit5":
        if kotlin_dsl:
            junit5_dep = f'    junit5PluginVersion.set("{PIT_JUNIT5_PLUGIN_VERSION}")\n'
        else:
            junit5_dep = f'    junit5PluginVersion = "{PIT_JUNIT5_PLUGIN_VERSION}"\n'
    if kotlin_dsl:
        return (
            "\n// pitest configuration injected by inject_pitest_plugin.py\n"
            "pitest {\n"
            f'    pitestVersion.set("{PIT_VERSION}")\n'
            + junit5_dep +
            f'    threads.set({PIT_THREADS})\n'
            '    outputFormats.set(setOf("HTML", "XML", "CSV"))\n'
            '    exportLineCoverage.set(true)\n'
            '    timestampedReports.set(false)\n'
            "    val tc = (project.findProperty(\"targetClasses\") as String?)\n"
            "        ?.split(\",\")?.map { it.trim() }?.filter { it.isNotEmpty() } ?: listOf(\"*\")\n"
            "    val tt = (project.findProperty(\"targetTests\") as String?)\n"
            "        ?.split(\",\")?.map { it.trim() }?.filter { it.isNotEmpty() } ?: listOf(\"*\")\n"
            "    targetClasses.set(tc)\n"
            "    targetTests.set(tt)\n"
            '    jvmArgs.set(listOf(\n'
            '        "--add-opens=java.base/java.lang=ALL-UNNAMED",\n'
            '        "--add-opens=java.base/java.util=ALL-UNNAMED",\n'
            '        "--add-opens=java.base/java.time=ALL-UNNAMED",\n'
            '        "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",\n'
            '        "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",\n'
            '        "--add-opens=java.management/sun.management=ALL-UNNAMED",\n'
            f'        "-Xmx{PIT_HEAP}"\n'
            '    ))\n'
            "}\n"
        )
    return (
        "\n// pitest configuration injected by inject_pitest_plugin.py\n"
        "pitest {\n"
        f"    pitestVersion = '{PIT_VERSION}'\n"
        + junit5_dep +
        f"    threads = {PIT_THREADS}\n"
        "    outputFormats = ['HTML', 'XML', 'CSV']\n"
        "    exportLineCoverage = true\n"
        "    timestampedReports = false\n"
        "    targetClasses = (project.hasProperty('targetClasses')\n"
        "        ? project.property('targetClasses').toString().split(',').collect { it.trim() }.findAll { it }\n"
        "        : ['*'])\n"
        "    targetTests = (project.hasProperty('targetTests')\n"
        "        ? project.property('targetTests').toString().split(',').collect { it.trim() }.findAll { it }\n"
        "        : ['*'])\n"
        "    jvmArgs = [\n"
        "        '--add-opens=java.base/java.lang=ALL-UNNAMED',\n"
        "        '--add-opens=java.base/java.util=ALL-UNNAMED',\n"
        "        '--add-opens=java.base/java.time=ALL-UNNAMED',\n"
        "        '--add-opens=java.base/java.lang.reflect=ALL-UNNAMED',\n"
        "        '--add-opens=java.base/sun.nio.ch=ALL-UNNAMED',\n"
        "        '--add-opens=java.management/sun.management=ALL-UNNAMED',\n"
        f"        '-Xmx{PIT_HEAP}'\n"
        "    ]\n"
        "}\n"
    )


def find_matching_brace(text: str, open_idx: int) -> int:
    """Return the index of the `}` matching the `{` at `open_idx`.

    Robust to: line comments (// ...\\n), block comments (/* ... */), single-quoted
    strings ('...'), double-quoted strings ("..."), Kotlin/Groovy triple-quoted
    strings ('''...''' / \"\"\"...\"\"\"), and Groovy GString interpolation
    (${ ... }) which can itself contain `{`/`}`. Tokenises with a small state
    machine; only counts braces while in CODE mode.

    Raises ValueError if the input is malformed or no match is found.
    """
    if text[open_idx] != "{":
        raise ValueError(f"open_idx does not point at '{{' (got {text[open_idx]!r})")

    CODE, LINE_COMMENT, BLOCK_COMMENT, STRING_DQ, STRING_SQ, TRIPLE_DQ, TRIPLE_SQ = range(7)
    state = CODE
    depth = 0
    # When we enter `${ ... }` interpolation we push (resume_state, depth_marker)
    # so a matching `}` can switch back to the right string mode.
    interp: list[tuple[int, int]] = []

    i = open_idx
    n = len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state == CODE:
            if ch == "/" and nxt == "/":
                state = LINE_COMMENT; i += 2; continue
            if ch == "/" and nxt == "*":
                state = BLOCK_COMMENT; i += 2; continue
            if ch == '"' and text[i:i+3] == '"""':
                state = TRIPLE_DQ; i += 3; continue
            if ch == "'" and text[i:i+3] == "'''":
                state = TRIPLE_SQ; i += 3; continue
            if ch == '"':
                state = STRING_DQ; i += 1; continue
            if ch == "'":
                state = STRING_SQ; i += 1; continue
            if ch == "{":
                depth += 1; i += 1; continue
            if ch == "}":
                if interp and depth == interp[-1][1] + 1:
                    # closing the `{` we entered for ${ ... }; resume the string
                    resume_state, _ = interp.pop()
                    state = resume_state
                    depth -= 1
                    i += 1
                    continue
                depth -= 1
                i += 1
                if depth == 0:
                    return i - 1
                continue
            i += 1; continue
        if state == LINE_COMMENT:
            if ch == "\n":
                state = CODE
            i += 1; continue
        if state == BLOCK_COMMENT:
            if ch == "*" and nxt == "/":
                state = CODE; i += 2; continue
            i += 1; continue
        if state in (STRING_DQ, TRIPLE_DQ):
            if ch == "\\":
                i += 2; continue
            if ch == "$" and nxt == "{":
                interp.append((state, depth))
                state = CODE
                depth += 1   # account for the `{` we're consuming
                i += 2
                continue
            if state == STRING_DQ and ch == '"':
                state = CODE; i += 1; continue
            if state == TRIPLE_DQ and text[i:i+3] == '"""':
                state = CODE; i += 3; continue
            i += 1; continue
        if state in (STRING_SQ, TRIPLE_SQ):
            if ch == "\\":
                i += 2; continue
            if state == STRING_SQ and ch == "'":
                state = CODE; i += 1; continue
            if state == TRIPLE_SQ and text[i:i+3] == "'''":
                state = CODE; i += 3; continue
            i += 1; continue
        i += 1

    raise ValueError("unmatched '{'")


def inject_gradle(build_path: Path, framework: str) -> None:
    """Inject the pitest plugin into a build.gradle / build.gradle.kts.

    Strategy:
    1. If the script already references info.solidsoft.pitest, skip.
    2. Find the first top-level `plugins { ... }` block. If found, insert the
       `id 'info.solidsoft.pitest' version '...'` line inside it (just before
       the matching `}`), then append the `pitest { ... }` config block at EOF.
    3. If no `plugins {` exists, append a fresh `plugins { id ... }` block plus
       the `pitest { ... }` config block at EOF.
    """
    text = build_path.read_text(encoding="utf-8")
    if "info.solidsoft.pitest" in text:
        return
    kotlin = build_path.suffix == ".kts"
    plugin_line = make_gradle_plugin_id_line(kotlin)
    pitest_block = make_gradle_pitest_config(framework, kotlin)

    # Search for the first `plugins {` at the start of a line, skipping over
    # `pluginManagement { ... }` (a different DSL block in settings.gradle).
    m = re.search(r"^[ \t]*plugins\s*\{", text, re.MULTILINE)
    if m:
        try:
            close_idx = find_matching_brace(text, m.end() - 1)
            new_text = (
                text[:close_idx]
                + plugin_line
                + text[close_idx:]
                + pitest_block
            )
            build_path.write_text(new_text, encoding="utf-8")
            return
        except ValueError:
            # Fallback: brace match failed; append fresh block. Worse than merge
            # (may collide on Kotlin DSL), but better than aborting.
            pass

    if kotlin:
        fresh = f'\nplugins {{\n{plugin_line}}}\n'
    else:
        fresh = f"\nplugins {{\n{plugin_line}}}\n"
    build_path.write_text(text + fresh + pitest_block, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build_path", type=Path,
                    help="pom.xml, build.gradle, or build.gradle.kts")
    ap.add_argument("--framework", required=True,
                    choices=("junit5", "junit4", "testng", "unknown"))
    ap.add_argument("--pit-version", default=PIT_VERSION,
                    help=f"PIT version to inject into pom (default {PIT_VERSION})")
    ap.add_argument("--junit5-version", default=PIT_JUNIT5_PLUGIN_VERSION,
                    help=f"pitest-junit5-plugin version (default {PIT_JUNIT5_PLUGIN_VERSION})")
    args = ap.parse_args()
    if not args.build_path.exists():
        print(f"[error] build file not found: {args.build_path}", file=sys.stderr)
        return 1
    name = args.build_path.name.lower()
    if name == "pom.xml":
        text = args.build_path.read_text(encoding="utf-8")
        if "<artifactId>pitest-maven</artifactId>" in text:
            print("[skip] pitest-maven already present", file=sys.stderr)
            return 0
        args.build_path.write_text(
            inject(text, args.framework, args.pit_version, args.junit5_version),
            encoding="utf-8",
        )
        print(f"[done] injected pitest-maven {args.pit_version} (framework={args.framework}) into {args.build_path}", file=sys.stderr)
    elif name in ("build.gradle", "build.gradle.kts"):
        inject_gradle(args.build_path, args.framework)
        print(f"[done] injected pitest gradle plugin (framework={args.framework}) into {args.build_path}", file=sys.stderr)
    else:
        print(f"[error] unsupported build file: {args.build_path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
