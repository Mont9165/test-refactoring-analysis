# RefactoringMiner 3.0.0 Audit Pipeline (Major-Revision Analyses)

Scripts that reproduce every RefactoringMiner-based number added in the
major revision of the paper (sensitivity of RM on test files, co-occurrence
in adjacent commits, and the no-refactoring residue audit).

## Why this pipeline exists

The original data-collection pipeline persisted only aggregate counts per
commit. The revision analyses require per-detection JSON output, so
RefactoringMiner 3.0.0 (the version used in the study) is re-run per commit
with `-json`.

**Pitfall this pipeline works around:** RefactoringMiner uses JGit, which
cannot read `blob:none` partial clones — it silently returns *empty* output
(no error). `rm_runner.py` therefore materializes the blobs of both snapshots
(`sha^` and `sha`) with git-CLI checkouts before invoking RM. If you modify
the cloning strategy, verify JSONs are non-empty before trusting results.

## Setup

Requirements: Python 3.10+, git, Java 17+ (RM 3.0.0 runs on 17/21).

```bash
export RM300_WORK=./work          # clones + JSON cache live here (~tens of GB)
curl -sL -o rm300.zip https://github.com/tsantalis/RefactoringMiner/releases/download/3.0.0/RefactoringMiner-3.0.0.zip
unzip rm300.zip -d "$RM300_WORK"
```

## Pipeline

```bash
# Step 1 — run RM 3.0.0 on all needed commits (idempotent; several hours):
#   158 RQ3 commits + up to 3 first-parent ancestors each + the
#   no-test-refactoring commits from the annotation export (~825 JSONs).
python run_all_commits.py --audits

# Step 2 — sensitivity-sample statistics (paper Section 4.3.2):
#   kappa=0.81, precision 0.88 (44/50), Wilson [0.76,0.94];
#   43/50 reproduced identically by 3.0.0, precision unchanged 0.88 (38/43).
python compare_sample_50.py

# Step 2b — detection pool (1,756 test-file detections) and the stratified
# sample CSV, using the project's own flattening script:
python ../rq1/rm_sensitivity/sample_rm_detections.py \
    --rm-json-dir "$RM300_WORK/json" \
    --output-flat outputs/all_test_file_detections_300.csv \
    --output-sample outputs/resample_300_50.csv \
    --per-type 3 --total-cap 50 --seed 42

# Step 3 — residue audit on the canonical 208-commit set (paper Section 9.1):
#   122/208 (58.7%) with test-file general refactorings vs 72 in the original
#   run; remaining 86: 64.0% / 20.9% / 15.1%.
python residue_audit_208.py

# Step 4 — co-occurrence in adjacent commits (major revision; superseded in
# the minor revision by step 6):
#   123/158 (77.8%) same commit; +18 ancestor-only -> 141/158 (89.2%).
# The existing script reads fixed cache paths; point them at this cache:
ln -s "$RM300_WORK/json"  /tmp/rm_sensitivity/json
ln -s "$RM300_WORK/repos" /tmp/pit_pipeline_v2/repos
python ../rq1/multi_commit_cooccurrence.py --window 3

# Step 5 — per-commit diff classification consumed by step 3
# (regenerates rq3/no_refactor_classification.csv):
python ../rq3/classify_no_refactor_commits.py

# Step 6 — adjacent-window audit with following commits and a random
# baseline (minor revision, Comment 3-10; paper Section 9.2). Full clones,
# one worker per repository; writes adjacent_windows.csv to $RM300_WORK.
python adjacent_window_audit.py --workers 16
# Adds the three commits after the same random baseline anchor
# (writes adjacent_windows_v2.csv; copy it to outputs/).
python baseline_following.py
# Window sizes 1-3, preceding and following, against the baseline.
# Drops blackduck 238654e and neo4j 33e64d6, which no longer contain a test
# refactoring after the minor-revision catalogue changes (158 -> 156).
python window_size_sensitivity.py
```

## Paper-number map

| Number in the paper | Script |
|---|---|
| kappa 0.81, precision 0.88 (44/50), CI [0.76, 0.94]; 43/50 identical under 3.0.0, 0.88 (38/43) | `compare_sample_50.py` |
| 1,756 test-file detections (pool) | step 2b |
| 123/158 (77.8%), +18 -> 141/158 (89.2%) | `../rq1/multi_commit_cooccurrence.py` |
| 208 = 366-158; 122 (58.7%) vs 72; 86 = 64.0/20.9/15.1% | `residue_audit_208.py` |
| Section 9.2 (minor revision): preceding 55.1% / following 57.1% of 156 commits vs baseline 32.5% / 35.1% (151 pairs); Wilcoxon p=0.002 and p<0.001, r=0.36 and 0.44; windows of 1 and 2 commits p<=0.002 | `window_size_sensitivity.py` |

## Provenance of the original RQ1 cells (do not confuse with the audit files)

Table 4's cells derive from joining the two ORIGINAL per-commit CSVs on
`commit_id`:

- `../rq1/output/test/all_commits_test_refactoring.csv`
- `../rq1/output/general/all_commits_refactoring.csv`

Neither = both counts zero (136 commits); general-only = 72; the audit set
208 = 72 + 136. Implementation: `../rq1/analyze_relationship_general_vs_test.py`;
summary: `../rq1/results/analysis_report.txt`. Commit URLs come from
`2_sampling_test_refactor_commits/result/sampling_test_commits.csv`.
`../rq3/no_refactor_classification.csv` (212 rows) is the FOLLOW-UP AUDIT
table keyed on the annotation export, NOT the original 136-commit set.
Table 4 is the canonical RQ1 result and is not modified by these audits.

## Committed outputs (for record; all regenerable)

- `outputs/comparison.csv` — per-detection 3.0.0 reproduction status of the
  50-item validated sample (exact / desc-match / different / absent).
- `outputs/all_test_file_detections_300.csv` — the 1,756-detection pool.
- `outputs/resample_300_50.csv` — stratified 50-sample from the 3.0.0 pool
  (drawn during the revision; ultimately not used for the reported numbers,
  kept for provenance).
- `outputs/adjacent_windows_v2.csv` — per-commit RM counts for the same
  commit, the three preceding and three following commits, and the
  preceding and following baseline windows (158 rows; -1 = RM failure).

## Related analyses elsewhere in the repository

- Mutation score / coverage (paper Section 6.3): `../rq3/2_mutation_coverage_analysis/`
  (`run_pit_jacoco.sh` -> `aggregate_results.py` -> `run_stats.py`; exact
  midrank Wilcoxon, outputs in `final_data/stats_tierA.csv`).
- Rater agreement for the sensitivity sample: `../rq1/rm_sensitivity/compute_rm_sensitivity_kappa.py`.
- Dataset characterization (paper Section 4.2.3): `../dataset_characterization/`
  (`characterize_projects.py`, `compare_rq3_vs_seart.py`; metrics retrieved April 2026).
- Motivation-coding agreement (kappa=0.93): `../rq4_socio_technical/compute_motivation_kappa.py`.
- Change-pattern figures (Figures 4-5): `../rq3/descriptive_analysis/regen_change_patterns_158.py`.
- Taxonomy saturation: `../rq2/saturation/compute_saturation.py`.
