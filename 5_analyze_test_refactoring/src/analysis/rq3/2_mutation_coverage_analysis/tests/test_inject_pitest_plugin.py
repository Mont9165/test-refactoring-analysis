"""Unit tests for inject_pitest_plugin.find_matching_brace and inject_gradle.

Run with:
    cd 5_analyze_test_refactoring/src/analysis/rq3/2_mutation_coverage_analysis
    python tests/test_inject_pitest_plugin.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from inject_pitest_plugin import find_matching_brace, inject_gradle


def assert_match(label: str, script: str) -> None:
    """Assert that find_matching_brace returns the index of the script's last `}`."""
    open_idx = script.index("{")
    close_idx = find_matching_brace(script, open_idx)
    expected = script.rindex("}")
    if close_idx != expected:
        print(f"FAIL [{label}]: matcher returned {close_idx}, expected {expected}")
        print(f"  script: {script!r}")
        print(f"  matched substring: {script[open_idx:close_idx+1]!r}")
        sys.exit(1)
    print(f"PASS [{label}]")


def test_brace_matcher() -> None:
    # Fixture 1: plain Groovy plugins block
    assert_match("groovy_plain", "plugins { id 'java' }")

    # Fixture 2: Kotlin DSL plugins block
    assert_match("kotlin_plain", 'plugins { id("java") version "1.0" }')

    # Fixture 3: block comment containing braces
    assert_match("block_comment_braces", "plugins { id 'java' /* { } */ }")

    # Fixture 4: line comment containing braces
    assert_match("line_comment_braces", "plugins { id 'java' // { fake }\n }")

    # Fixture 5: nested closure inside plugins block
    assert_match("nested_closure",
                 "plugins {\n  id 'java' apply { from 'foo' }\n}")

    # Fixture 6: Groovy GString with interpolation containing `{`
    # Note: keep it parseable: use ${'{'} to put a literal `{` inside the string.
    assert_match("gstring_interp",
                 'plugins { id "${"{".substring(0,1)}foo" }')

    # Fixture 7: triple-quoted Kotlin string
    assert_match("kotlin_triple_string",
                 'plugins {\n  id("foo")\n  // doc: """ a } b """ ignored\n}')

    # Fixture 8: single-quoted string with brace
    assert_match("single_quote_brace",
                 "plugins { id 'java { fake brace }' }")


def test_inject_gradle_into_existing_plugins() -> None:
    """Layer 3: merge into existing plugins {} block instead of appending duplicate."""
    script = (
        "// build.gradle.kts\n"
        "plugins {\n"
        '    id("java")\n'
        '    id("maven-publish")\n'
        "}\n"
        "\n"
        "dependencies {\n"
        '    testImplementation("junit:junit:4.13.2")\n'
        "}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "build.gradle.kts"
        p.write_text(script)
        inject_gradle(p, "junit5")
        result = p.read_text()
        # The new plugin id should be inside the FIRST plugins {} block
        plugins_block = result[result.index("plugins {"):result.index("dependencies {")]
        assert "info.solidsoft.pitest" in plugins_block, \
            f"plugin id not merged into existing plugins block:\n{result}"
        # There should be exactly ONE `plugins {` line at the top level
        assert result.count("plugins {") == 1, \
            f"expected 1 plugins block, got {result.count('plugins {')}:\n{result}"
        # The `pitest { ... }` config block should be appended
        assert "pitest {" in result
        assert "junit5PluginVersion" in result
    print("PASS [inject_gradle_into_existing_plugins]")


def test_inject_gradle_no_existing_plugins() -> None:
    """Edge case: script has no plugins {} block — append a fresh one."""
    script = (
        "apply plugin: 'java'\n"
        "dependencies {\n"
        "    testImplementation 'junit:junit:4.13.2'\n"
        "}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "build.gradle"
        p.write_text(script)
        inject_gradle(p, "junit4")
        result = p.read_text()
        assert "info.solidsoft.pitest" in result
        assert "plugins {" in result
        assert "pitest {" in result
    print("PASS [inject_gradle_no_existing_plugins]")


def test_inject_gradle_idempotent() -> None:
    """Re-running on an already-injected script should be a no-op."""
    script = (
        "plugins {\n"
        "    id 'java'\n"
        "    id 'info.solidsoft.pitest' version '1.15.0'\n"
        "}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "build.gradle"
        p.write_text(script)
        inject_gradle(p, "junit5")
        assert p.read_text() == script, "injection should be a no-op when already present"
    print("PASS [inject_gradle_idempotent]")


if __name__ == "__main__":
    test_brace_matcher()
    test_inject_gradle_into_existing_plugins()
    test_inject_gradle_no_existing_plugins()
    test_inject_gradle_idempotent()
    print("\nAll tests passed.")
