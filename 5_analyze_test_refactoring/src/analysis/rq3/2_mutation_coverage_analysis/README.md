# A1: Mutation Score & Line/Branch Coverage (Reviewer AE-2 / R4-1)

Goal: complement test-smell-based quality assessment with mutation score (PIT) and
JaCoCo line/branch coverage, comparing pre- and post-refactor commits.

## Inputs
- Canonical commit list: `../1_analyze_testsmell_diff/file_level_wide.csv`
  → 158 distinct `commit_url` values (the RQ3 RM-validated set).
- Per-commit test files of interest: derived from RefactorHub annotation
  `parameter_data` field (`location.path`) in
  `../../../../../4_manual_inspection/src/refactoring_data_2025-02-19.csv`.

## Pipeline
1. **`select_buildable_subset.py`** — clones each repo (shallow), checks out the
   refactor SHA *and* its parent, runs `mvn -B -DskipTests test-compile` on both,
   writes `buildable_commits.csv` listing only those that compile on both sides.
2. **`run_pit_jacoco.sh <repo_dir> <sha>`** — invokes
   `mvn -B -DskipTests test`, then PIT (`org.pitest:pitest-maven:1.15.8:mutationCoverage`)
   and JaCoCo (`org.jacoco:jacoco-maven-plugin:0.8.12:report`) without modifying the
   project's `pom.xml` (uses CLI plugin invocation). Writes raw XML/HTML reports
   under `output/<sha>/`.
3. **`aggregate_results.py`** — parses `mutations.xml` and `jacoco.xml`, produces
   `mutation_coverage_results.csv`:
     `commit_url, project, sha, side, build_ok, tests_passed,
      mutation_score, killed, survived, no_coverage,
      line_cov, branch_cov, instruction_cov`.
   Columns are emitted twice per commit (`side` ∈ {before, after}) so paired
   analysis is straightforward in pandas.
4. Statistical comparison reuses the Wilcoxon + Vargha-Delaney pipeline already
   in `../../../test.py` — point it at the new CSV.

## Constraints / Assumptions
- Maven projects only (Gradle handled in a follow-up pass; flag as `build_system`
  in `buildable_commits.csv`).
- We do not modify project source. PIT is invoked via plugin coordinates so
  pre-existing `<plugins>` blocks are not touched.
- Subset target: ~30–60 commits where both sides build *and* mvn test passes.
  Quality > quantity.

## Open decisions (raise with Au-san before running)
- PIT mutators: default vs. `STRONGER`?
- Test scope filter: only the test files annotated as refactored, or full module?
- Time budget per commit (PIT can take >30 min on large modules) — propose 10 min cap.
