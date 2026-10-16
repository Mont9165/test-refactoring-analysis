#!/usr/bin/env bash
# Run RefactoringMiner 3.0.10 on every distinct commit_url in
# file_level_wide.csv. Outputs one JSON per commit under <output-dir>/<sha>.json.
# Reuses cloned repos from /tmp/pit_pipeline_v2/repos when available.
#
# Usage:
#   ./run_rm.sh [WORK_DIR=/tmp/rm_sensitivity] [REPOS_DIR=/tmp/pit_pipeline_v2/repos]
#
set -uo pipefail

WORK_DIR=${WORK_DIR:-/tmp/rm_sensitivity}
REPOS_DIR=${REPOS_DIR:-/tmp/pit_pipeline_v2/repos}
RM_BIN=${RM_BIN:-/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/5_analyze_test_refactoring/src/analysis/rq1/RefactoringMiner/tools/RefactoringMiner-3.0.10/bin/RefactoringMiner}
CANONICAL_CSV=${CANONICAL_CSV:-/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/5_analyze_test_refactoring/src/analysis/rq3/1_analyze_testsmell_diff/file_level_wide.csv}
RM_TIMEOUT=${RM_TIMEOUT:-600}
PYTHON=${PYTHON:-/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/.venv/bin/python}

JSON_DIR="$WORK_DIR/json"
LOG_DIR="$WORK_DIR/log"
mkdir -p "$JSON_DIR" "$LOG_DIR" "$REPOS_DIR"

if command -v gtimeout >/dev/null 2>&1; then TBIN=gtimeout
elif command -v timeout >/dev/null 2>&1; then TBIN=timeout
else TBIN=""; fi
run_with_timeout() {
  local secs=$1; shift
  if [[ -n "$TBIN" ]]; then "$TBIN" "$secs" "$@"; else "$@"; fi
}

# Distinct commit URLs (bash 3 compatible).
COMMITS=()
while IFS= read -r line; do
  COMMITS+=("$line")
done < <($PYTHON -c "
import csv,sys
seen=set()
for r in csv.DictReader(open('$CANONICAL_CSV', encoding='utf-8-sig')):
    u=r.get('commit_url','').strip()
    if u and u not in seen:
        seen.add(u); print(u)
")

TOTAL=${#COMMITS[@]}
echo "[plan] $TOTAL commits"
ok=0; fail=0; skipped=0
i=0
for url in "${COMMITS[@]}"; do
  i=$((i+1))
  # Parse owner/repo/sha from URL.
  owner=$(echo "$url" | sed -E 's#https://github.com/([^/]+)/([^/]+)/commit/.*#\1#')
  repo=$(echo "$url" | sed -E 's#https://github.com/([^/]+)/([^/]+)/commit/.*#\2#')
  sha=$(echo "$url" | sed -E 's#https://github.com/[^/]+/[^/]+/commit/([0-9a-f]+).*#\1#')
  out_json="$JSON_DIR/$sha.json"
  log_file="$LOG_DIR/$sha.log"

  if [[ -s "$out_json" ]]; then
    skipped=$((skipped+1))
    continue
  fi

  repo_dir="$REPOS_DIR/${owner}__${repo}"
  if [[ ! -d "$repo_dir/.git" ]]; then
    echo "[$i/$TOTAL] cloning $owner/$repo"
    git clone --filter=blob:none --no-tags "https://github.com/$owner/$repo.git" "$repo_dir" 2>>"$log_file" \
      || { echo "  clone failed"; fail=$((fail+1)); continue; }
  fi
  ( cd "$repo_dir" && git fetch --depth=2 origin "$sha" >/dev/null 2>&1 || true )

  echo "[$i/$TOTAL] RM on $owner/$repo @ ${sha:0:8}"
  if run_with_timeout "$RM_TIMEOUT" "$RM_BIN" -c "$repo_dir" "$sha" -json "$out_json" >"$log_file" 2>&1; then
    ok=$((ok+1))
  else
    fail=$((fail+1))
    echo "  RM failed (see $log_file)"
  fi
done

echo "[done] ok=$ok fail=$fail skipped=$skipped (out of $TOTAL) -> $JSON_DIR"
