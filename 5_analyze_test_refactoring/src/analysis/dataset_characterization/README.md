# A3: Dataset Characterization (Reviewer AE-5 / R2-4)

Goal: justify external validity by reporting *what kind* of projects make up
the corpus — domain, testing framework, size, age, activity. Reviewer R2-4
explicitly mentions JUnit / TestNG breakdown.

## Inputs
- `../../../1_collect_test_refactoring_commits/src/main/resources/input/projects_info.csv`
  — 5,483 projects (Project Name, Stars, Forks, Commits) collected via SEART.
- `../rq3/1_analyze_testsmell_diff/file_level_wide.csv` — 158 RQ3 commits to
  flag the analyzed subset.
- GitHub API via `gh` CLI for: topics, license, default branch, age, language
  composition.
- `pom.xml` (or `build.gradle`) of each project — for testing framework
  detection.

## Pipeline (`characterize_projects.py`)
1. Build the union of {SEART corpus, sampled-366 commits' projects, RQ3-158
   subset's projects}, marked by `corpus_role` column.
2. For each project, fetch via `gh api`:
     - `repos/{full_name}` → topics, license, size_kb, created_at, pushed_at,
       default_branch, has_wiki, archived, fork.
     - Optionally `repos/{full_name}/languages` → percent Java / Kotlin / etc.
3. Pull `pom.xml` (or top-level `build.gradle*`) from default branch; detect:
     - `framework_junit4`, `framework_junit5`, `framework_testng`,
       `framework_mockito`, `framework_assertj`, `framework_hamcrest`,
       `framework_spock` (booleans).
4. Output: `project_characteristics.csv`.
5. Companion notebook (or `summarize.py`, follow-up) cross-tabs:
     - Topic frequency (top-20).
     - Framework distribution overall vs. RQ3 subset.
     - Stars / forks / commits histograms.
     - Size and age distributions.

## Talking points (response letter)
- Frame the corpus as "popular Java OSS" with explicit topic / domain
  distribution.
- Compare RQ3-158 subset vs. full SEART corpus to argue subset
  representativeness.
- Limitation: no enterprise or domain-specific (e.g., embedded) Java
  → call out as TTV.

## Rate limit
~5,500 projects × ~3 endpoints = ~16k requests. Run with a token via
`gh auth login` (5,000/h authenticated) and the built-in 1 s pacing; expect
~3 hours wall-time. Resume-friendly.

## Full-sample characterisation (Section 4.2.3 / R2-4, added 2026-07-12)

The Dataset Characterisation paragraph in Section 4.2.3 covers the projects
behind the 370-commit manual-inspection sample (190 project names; note
`google/wycheproof` and `C2SP/wycheproof` are the same repository before and
after a transfer, so the sample spans 189 distinct repositories).

- `count_java_loc.py` — shallow-clones each project's current default branch
  and counts Java SLOC with `scc` (blank/comment lines excluded); test files
  are those under a `test`/`tests`/`testing`/`androidTest`/`it` directory or
  named `*Test(s).java` / `*TestCase.java` / `*IT.java`. Output:
  `java_loc_per_project.csv`. Two repos have no Java at their current HEAD
  (`C2SP/wycheproof`: Java testsuite removed; `typedb/typedb`: rewritten in
  Rust) and are excluded from the SLOC medians.
- `project_domains.csv` — one domain per project (9-category taxonomy).
  Produced by two independent LLM classification passes over repo
  name/description/topics (agreement 171/188, 91%), disagreements adjudicated
  by a third pass; two projects missed by the passes were assigned manually.
  **Author validation recommended before further use.**
- `summarize_sample_projects.py` — reproduces every number in the Section
  4.2.3 paragraph (age/stars/commits at the 2026-04-30 reference date,
  framework adoption from top-level build scripts with overlap and
  lower-bound caveats, SLOC medians, domain distribution).
