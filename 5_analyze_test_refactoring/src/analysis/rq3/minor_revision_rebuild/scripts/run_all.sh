#!/bin/bash
# Rebuild the corrected RQ3 dataset (data_fix2) and its outputs (out_fix2) from the repository inputs.
# Order and arguments follow the original session (scratch rq3_recompute/run_all.sh, followup/run_followup.sh,
# and the followup2 commands); only the directories differ. Read-only with respect to the repository:
# every Python call runs with -B / PYTHONDONTWRITEBYTECODE so no __pycache__ is written into the repo.
set -euo pipefail
cd "$(dirname "$0")/.."            # rq3_rebuild/
PY=${PY:-python3}
export PYTHONDONTWRITEBYTECODE=1
mkdir -p intermediate/data_orig intermediate/data_new intermediate/data_fix intermediate/data_fix_mmask \
         data_fix2 out_fix2/figures sensitivity_nan0/data_nan0 sensitivity_nan0/out_nan0

# ---- data ----------------------------------------------------------------------------------------------
$PY -B scripts/make_new_data.py  > intermediate/make_new_data.txt   # data_orig (405-row repo copies), data_new (403 rows: Lambdarize dropped, CEV merged)
$PY -B scripts/verify_flaws.py   > intermediate/verify_flaws.txt    # annotation sides per row -> intermediate/flags_405.pkl
$PY -B scripts/build_fixed.py    > intermediate/build_fixed.txt     # data_fix (382: one-sided out), data_fix_mmask (+ method cells blanked where file NaN)
$PY -B scripts/build_fix2.py     > out_fix2/build_fix2.txt          # data_fix2 = data_fix_mmask minus openjdk/lilliput 7f80683 (379 rows / 145 commits)

# ---- analyses on data_fix2 (followup2 command #93) -----------------------------------------------------
$PY -B scripts/rq3_row_level_tables_nanmissing.py data_fix2 out_fix2 > out_fix2/rq3_row_level_tables.txt          # Tables 7/8
$PY -B scripts/new_types_effect_sizes.py data_fix2 out_fix2 > out_fix2/new_types_effect_sizes.txt 2>&1           # per-type A12
$PY -B scripts/paragraph_after_table8.py out_fix2 data_fix2 > out_fix2/paragraph_after_table8.txt                 # BH + paragraph after Table 8
$PY -B scripts/contradictory_smells.py data_fix2 out_fix2 > out_fix2/contradictory_smells.txt 2>&1               # Spearman pairs
$PY -B scripts/regen_change_patterns_nanmissing.py data_fix2 out_fix2/figures > out_fix2/figures/regen_fix2_log.txt   # Figs 4/5 (n145)
$PY -B scripts/regen_change_patterns_v3.py data_fix2 out_fix2/figures > out_fix2/figures/regen_v3_log.txt
$PY -B scripts/regen_change_patterns_v4.py data_fix2 out_fix2/figures > out_fix2/figures/regen_v4_log.txt             # unmeasured commits shown as Not present (superseded)
$PY -B scripts/regen_change_patterns_v6.py data_fix2 out_fix2/figures > out_fix2/figures/regen_v6_log.txt             # version in the paper (Figures 4 and 5)
$PY -B scripts/regen_change_patterns_presentonly.py data_fix2 out_fix2/figures > out_fix2/figures/regen_presentonly_log.txt  # trial variant
$PY -B scripts/fig_text_claim2.py        > out_fix2/fig_text_claim2.txt

# ---- formerly inline one-off computations ----------------------------------------------------------------
$PY -B scripts/table6_prevalence_fix2.py > out_fix2/table6_prevalence_fix2.txt   # Table 6 (4 categories, present-only) + Sec. 7 prevalence
$PY -B scripts/cev_grouping_fix2.py      > out_fix2/cev_grouping_fix2.txt        # CEV x ECT detail, Grouping Tests median dNOM
$PY -B scripts/eager_lazy_nan_fix2.py    > out_fix2/eager_lazy_nan_fix2.txt      # Eager/Lazy NaN structure
$PY -B scripts/eager_lazy_commits_fix2.py > out_fix2/eager_lazy_commits_fix2.txt
$PY -B scripts/decompose_old_t6.py       > out_fix2/decompose_old_t6.txt          # 403-row cell decomposition (4,771 / 824)
$PY -B scripts/letter_correction_table.py > out_fix2/letter_correction_table.txt # correction table in the round-2 letter

# ---- sensitivity: exclude the 24 but set NaN -> 0 (followup3; not the paper basis) ------------------------
$PY -B scripts/sensitivity_nan0_build.py > sensitivity_nan0/build.txt
$PY -B scripts/rq3_row_level_tables_nanmissing.py sensitivity_nan0/data_nan0 sensitivity_nan0/out_nan0 > sensitivity_nan0/out_nan0/rq3_row_level_tables.txt
$PY -B scripts/new_types_effect_sizes.py sensitivity_nan0/data_nan0 sensitivity_nan0/out_nan0 > sensitivity_nan0/out_nan0/new_types_effect_sizes.txt 2>&1
$PY -B scripts/sensitivity_nan0_compare.py > sensitivity_nan0/compare.txt

# ---- check against the paper -----------------------------------------------------------------------------
$PY -B scripts/check_paper_numbers.py | tee out_fix2/check_paper_numbers.txt
