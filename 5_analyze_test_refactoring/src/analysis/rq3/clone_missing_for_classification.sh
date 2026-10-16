#!/usr/bin/env bash
# R3-15 follow-up: shallow-clone every repo referenced by a
# diff_unavailable row in no_refactor_classification.csv so the
# classifier can compute git diff stats.
#
# Output: continues populating /tmp/pit_pipeline_v2/repos so subsequent
# runs of classify_no_refactor_commits.py see the diffs.
#
# Idempotent: skips repos that already exist.
set -uo pipefail

REPOS_DIR=${REPOS_DIR:-/tmp/pit_pipeline_v2/repos}
PYTHON=${PYTHON:-/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/.venv/bin/python}
CSV=${CSV:-/Users/horikawa/Dev/Research-repo/InvestigatingTheImpactOfTestSpecificRefactoring/5_analyze_test_refactoring/src/analysis/rq3/no_refactor_classification.csv}

mkdir -p "$REPOS_DIR"

# Distinct (owner, repo) for diff_unavailable rows.
TODO=$($PYTHON -c "
import csv
seen=set()
for r in csv.DictReader(open('$CSV')):
    if r['category']!='diff_unavailable': continue
    key=(r['owner'],r['repo'])
    if key in seen: continue
    seen.add(key)
    print(f\"{r['owner']}/{r['repo']}\")
")

i=0
total=$(echo "$TODO" | wc -l | tr -d ' ')
echo "[plan] $total unique repos to clone"
while IFS= read -r line; do
  i=$((i+1))
  [[ -z "$line" ]] && continue
  owner=${line%%/*}
  repo=${line#*/}
  dest="$REPOS_DIR/${owner}__${repo}"
  if [[ -d "$dest/.git" ]]; then
    echo "[$i/$total] cached: $owner/$repo"
    continue
  fi
  echo "[$i/$total] cloning: $owner/$repo"
  git clone --filter=blob:none --no-tags "https://github.com/$owner/$repo.git" "$dest" \
    > "$dest.log" 2>&1 || echo "  clone failed (see $dest.log)"
done <<<"$TODO"

echo "[done]"
