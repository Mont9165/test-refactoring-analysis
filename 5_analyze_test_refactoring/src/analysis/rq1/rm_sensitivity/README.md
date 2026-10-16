# A4: RefactoringMiner Sensitivity on Test Files (Reviewer R2-6)

Goal: quantify how often RefactoringMiner 3.0 mis-classifies refactorings in
test files specifically. Reviewer notes RM was designed for production code,
so test-file precision/recall may differ from the headline F-score.

## Input
- Detailed RM detections per detection (one row per detection, not per commit).
  The current pipeline only persists aggregate counts (`../output/{test,
  general}/all_commits_*.csv`), so RM has to be re-run with
  `-json <out>.json` for each commit. Sample command:
    ```bash
    java -jar RefactoringMiner-3.0.10.jar \
        -bc <repo_dir> <parent_sha> <sha> \
        -json <out_dir>/<sha>.json
    ```
- Once detailed JSON files exist, `sample_rm_detections.py` consumes them.

## Pipeline (`sample_rm_detections.py`)
1. Walk `--rm-json-dir`, parse each `<sha>.json` produced by RM.
2. Flatten into one row per detection with the canonical columns
   `commit_url, file_path, rm_type, rm_description, before_loc, after_loc`.
3. Filter to test files heuristically: path contains `/src/test/` *or*
   filename ends with `Test.java`, `Tests.java`, `IT.java`, `ITCase.java`.
4. Stratified random sample (default 5 detections per refactoring type, capped
   at 100 total) → `manual_validation_sample.csv` with empty annotation
   columns: `is_correct (Y/N)`, `correct_type`, `notes`.
5. After manual validation, run `compute_precision.py` (TBD) for per-type
   precision and 95% Wilson CIs.

## Reporting
- Report precision per refactoring type with sample sizes.
- Compare to RM's published F-score baseline; note types with notably lower
  precision in test files (these become the bias cells in TTV).
- If precision in test files is materially lower for the types most relevant
  to RQ1, consider re-running co-occurrence analyses while excluding
  low-precision types as a sensitivity check.
