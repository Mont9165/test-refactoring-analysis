# A2: Taxonomy Saturation Curve (Reviewer AE-6 / R4-5)

Goal: empirically demonstrate that the 37-type catalog is saturated, addressing
the reviewer concern that more annotation might surface more types.

## Inputs
- `../../../../../4_manual_inspection/src/refactoring_data_2025-02-19.csv`
  (col `order_index`, `experiment_title`, `type_name`, `annotator_name`).
- The annotation order is the natural ordering inside each experiment session.
- The CSV has 624 rows = 396 real refactoring + 225 `Non-Refactoring`
  + 3 `Any Refactoring` placeholders. Both placeholder labels must be excluded
  to recover the canonical 37 types — pass
  `--exclude-types 'Non-Refactoring,Any Refactoring'`.
- The 624 export covers 370 commits (185 in each of the two experiments,
  with no overlap; one annotator covers each commit, with consensus held
  later). It is an earlier snapshot of the annotation log; the canonical
  post-consolidation set in `../rq3/1_analyze_testsmell_diff/file_level_wide.csv`
  has 405 distinct (commit, type) pairs across 158 commits.

## Pipeline (`compute_saturation.py`)
1. Sort rows globally by `(experiment_title, order_index)`.
2. For each prefix length k, compute the cumulative number of distinct
   `type_name` values seen.
3. Bootstrap (1,000 resamples of the order) to obtain a 95% CI band for the
   curve and the saturation point (k where derivative drops below 1 new
   type / 100 instances).
4. Emit:
     - `saturation_curve.csv` with columns
       `k, distinct_types, ci_low, ci_high, new_types_in_window_100`.
     - `saturation_curve.png` — main figure.
     - `saturation_per_100_batches.png` — per-100 batch view requested in
       the memo (number of new types found in each 100-instance window).

## Talking points (response letter)
- Current per-window result with both placeholders excluded
  (396 instances → 37 types): **22, 11, 1, 3**.
- Frame as "approaching saturation" rather than "fully saturated" — the last
  window still discovers 3 new types. Use bootstrap CI to argue that under
  randomized order the curve plateaus.
- Acknowledge: saturation is conditional on the sampling frame
  (popular Java OSS, JUnit-style); future work could test other frames.
