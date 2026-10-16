#!/usr/bin/env bash
# Generalized PIT + JaCoCo runner for one commit_url.
#
# For the given commit_url:
#   1. Resolve metadata (owner, repo, sha, modules with test/production globs).
#   2. Clone the repo (cached) under $WORK_DIR/repos/<owner>__<repo>.
#   3. For both sides (parent SHA = "before", refactor SHA = "after"):
#        a. Detect test framework from the (first) module pom.
#        b. Inject pitest-maven plugin block (with framework-appropriate dep).
#        c. mvn install (skip tests) for the module.
#        d. JaCoCo: prepare-agent test report, scoped to the test classes.
#        e. PIT: mutationCoverage scoped to production globs and test classes.
#        f. Copy mutations.xml + jacoco.xml to $RESULTS_DIR/<sha>/.
#        g. git checkout -- <pom> to revert the injection.
#   4. Append a row to $RESULTS_DIR/run_log.csv with status flags.
#
# Inputs (env or args):
#   COMMIT_URL       (required)  full GitHub commit URL.
#   WORK_DIR         (default /tmp/pit_pipeline)
#   RESULTS_DIR      (default $WORK_DIR/results)
#   REFACTORING_CSV  (default $REPO_ROOT/4_manual_inspection/src/refactoring_data_2025-02-19.csv)
#   HELPERS_DIR      (default this script's dir)
#   PIT_TIMEOUT      (default 600 seconds per side)
#   DOCKER_IMG       (default maven:3.9.9-eclipse-temurin-17)
#
# Usage:
#   COMMIT_URL=https://github.com/apache/jspwiki/commit/62857b9... ./run_pit_jacoco.sh
#   ./run_pit_jacoco.sh https://github.com/apache/jspwiki/commit/62857b9...
#
set -uo pipefail

COMMIT_URL=${1:-${COMMIT_URL:?commit_url required}}
HELPERS_DIR=${HELPERS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}
REPO_ROOT=${REPO_ROOT:-$(cd "$HELPERS_DIR/../../../../.." && pwd)}
WORK_DIR=${WORK_DIR:-/tmp/pit_pipeline}
RESULTS_DIR=${RESULTS_DIR:-$WORK_DIR/results}
REFACTORING_CSV=${REFACTORING_CSV:-$REPO_ROOT/4_manual_inspection/src/refactoring_data_2025-02-19.csv}
PIT_TIMEOUT=${PIT_TIMEOUT:-600}
JACOCO_TIMEOUT=${JACOCO_TIMEOUT:-600}
DOCKER_IMG=${DOCKER_IMG:-maven:3.9.9-eclipse-temurin-17}
# Prefer the project venv's python (3.9+) over system python3 (often 3.6 on macOS).
if [[ -z "${PYTHON:-}" ]]; then
  if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    PYTHON="$REPO_ROOT/.venv/bin/python"
  else
    PYTHON=python3
  fi
fi
# Wall-time wrapper. macOS lacks GNU `timeout`; fall back to `gtimeout` (coreutils)
# or to a no-op if neither exists. Long-running PIT runs are still bounded by
# the per-mutation timeout PIT enforces internally.
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN=timeout
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN=gtimeout
else
  TIMEOUT_BIN=""
fi
run_with_timeout() {
  local secs=$1; shift
  if [[ -n "$TIMEOUT_BIN" ]]; then
    "$TIMEOUT_BIN" "$secs" "$@"
  else
    "$@"
  fi
}
PIT_VERSION=1.20.6
PIT_VERSION_JDK8=1.15.0     # PIT 1.15.x is the last line that supports JDK 8.
JACOCO_VERSION=0.8.12

# Layer 2: image selection by detected JDK version.
DOCKER_IMG_JDK21=${DOCKER_IMG_JDK21:-maven:3.9.9-eclipse-temurin-21}
DOCKER_IMG_JDK17=${DOCKER_IMG_JDK17:-maven:3.9.9-eclipse-temurin-17}
DOCKER_IMG_JDK11=${DOCKER_IMG_JDK11:-maven:3.9.9-eclipse-temurin-11}
DOCKER_IMG_JDK8=${DOCKER_IMG_JDK8:-maven:3.8.8-eclipse-temurin-8}

# MAVEN_OPTS with --add-opens helps old plugins (findbugs:3.0.2, jaxb1) running
# under JDK 9+ that hit "module java.base does not opens X to unnamed module"
# errors. NOTE: --add-opens does not exist in JDK 8 — passing it to a JDK 8
# JVM produces "Unrecognized option" and Maven fails to start. Apply only when
# the running JDK is 9 or newer.
MVN_OPTS_ADDOPENS_JDK9PLUS="--add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
MVN_OPTS_ADDOPENS_JDK8=""   # JDK 8 has neither modules nor --add-opens.

# Layer 1: skip flags. INSTALL_SKIP_FLAGS includes -Djacoco.skip (we don't need
# coverage from the install phase). MEASURE_SKIP_FLAGS does NOT include it,
# because jacoco:report and pitest must actually run. Both include skips for
# git-commit-id (2.0.4 fails on JGit/git repo format mismatch), shade-plugin
# fail-fast options, dependency-check that always wants the network, etc.
# Layer 13: aggregate of all skip / override flags discovered by per-commit
# debugging across Phase E and Phase F manual tuning. Goals:
#   - kill quality-gate plugins (rat/enforcer/license/checkstyle/spotbugs/findbugs/pmd/spotless/detekt)
#   - skip docs / signing / staging / release deployment
#   - blanket-override compilerArgument so projects with -Werror still build
#   - skip frontend-maven-plugin / npm / yarn / node bootstrapping
#   - skip git-commit-id (2.0.4 incompatible with newer git repo formats)
#   - skip dependency-check (network-dependent)
#   - skip maven-shade-plugin's create-source-jar
INSTALL_SKIP_FLAGS="-Drat.skip=true -Denforcer.skip=true -Dlicense.skip=true \
  -Dcheckstyle.skip=true -Dspotbugs.skip=true -Dfindbugs.skip=true \
  -Danimal.sniffer.skip=true -Dpmd.skip=true \
  -Dmaven.javadoc.skip=true -DskipITs=true -Dformat.skip=true \
  -Dspotless.check.skip=true -Dspotless.apply.skip=true \
  -Djacoco.skip=true -Dgpg.skip=true \
  -Dmaven.gitcommitid.skip=true -Dgit-commit-id.skip=true \
  -Ddependency-check.skip=true -Ddetekt.skip=true \
  -Dmdep.analyze.skip=true -Drevapi.skip=true \
  -Dmaven.enforcer.skip=true \
  -Dmaven.deploy.skip=true -DskipNexusStagingDeployMojo=true \
  -Dmaven.compiler.compilerArgument= -Dmaven.compiler.showWarnings=false \
  -Dskip.npm=true -Dfrontend.skip=true -Dskip.installnodenpm=true \
  -Dskip.yarn=true \
  -Dmaven.source.skip=true \
  -Dmaven.test.skip.exec=true"
MEASURE_SKIP_FLAGS="-Drat.skip=true -Denforcer.skip=true -Dlicense.skip=true \
  -Dcheckstyle.skip=true -Dspotbugs.skip=true -Dfindbugs.skip=true \
  -Danimal.sniffer.skip=true -Dpmd.skip=true \
  -Dmaven.javadoc.skip=true -DskipITs=true -Dformat.skip=true \
  -Dspotless.check.skip=true -Dspotless.apply.skip=true \
  -Dgpg.skip=true \
  -Dmaven.gitcommitid.skip=true -Dgit-commit-id.skip=true \
  -Ddependency-check.skip=true -Ddetekt.skip=true \
  -Dmdep.analyze.skip=true -Drevapi.skip=true \
  -Dmaven.enforcer.skip=true \
  -Dmaven.deploy.skip=true -DskipNexusStagingDeployMojo=true \
  -Dmaven.compiler.compilerArgument= -Dmaven.compiler.showWarnings=false \
  -Dskip.npm=true -Dfrontend.skip=true -Dskip.installnodenpm=true \
  -Dskip.yarn=true \
  -Dmaven.source.skip=true"

mkdir -p "$WORK_DIR/repos" "$RESULTS_DIR"
RUN_LOG="$RESULTS_DIR/run_log.csv"
if [[ ! -s "$RUN_LOG" ]]; then
  # Schema v2: adds recovery_layer_used and jdk_version columns. Old run_log.csv
  # files are read with their original schema by aggregate_results.py; the
  # absence of these columns is treated as recovery_layer_used=none.
  echo "commit_url,sha,side,build_ok,jacoco_ok,pit_ok,scope,framework,recovery_layer_used,jdk_version,error" >"$RUN_LOG"
fi

log() { echo "[$(date '+%H:%M:%S')] $*" >&2; }

# --- Resolve metadata via extract_refactored_paths.py -----------------------
META_JSON=$($PYTHON "$HELPERS_DIR/extract_refactored_paths.py" \
  --csv "$REFACTORING_CSV" --commit-url "$COMMIT_URL")
if [[ -z "$META_JSON" ]]; then
  log "no metadata for $COMMIT_URL"
  exit 2
fi

# Parse JSON via Python (jq might not be present on host).
read -r OWNER REPO SHA NUM_MODULES < <($PYTHON -c "
import json,sys
d = json.loads(sys.stdin.read())
print(d['owner'], d['repo'], d['sha'], len(d['modules']))
" <<<"$META_JSON")
log "metadata: owner=$OWNER repo=$REPO sha=$SHA modules=$NUM_MODULES"

if [[ "$NUM_MODULES" == "0" ]]; then
  log "no modules in metadata; skipping"
  exit 2
fi

# --- Clone (cached) ---------------------------------------------------------
REPO_DIR="$WORK_DIR/repos/${OWNER}__${REPO}"
if [[ ! -d "$REPO_DIR" ]]; then
  log "cloning https://github.com/$OWNER/$REPO.git"
  git clone --filter=blob:none --no-tags "https://github.com/$OWNER/$REPO.git" "$REPO_DIR" >/dev/null 2>&1 \
    || { log "clone failed"; exit 3; }
fi

# Discard any prior pom edits that may linger across runs.
( cd "$REPO_DIR" && git checkout -- . >/dev/null 2>&1 || true )

# Fetch shallow so the requested SHA and its parent are available.
( cd "$REPO_DIR" && git fetch --depth=2 origin "$SHA" >/dev/null 2>&1 || true )

# Resolve parent SHA after fetch.
PARENT_SHA=$( cd "$REPO_DIR" && git rev-parse "${SHA}^" 2>/dev/null )
if [[ -z "$PARENT_SHA" ]]; then
  log "could not resolve parent SHA"
  exit 3
fi
log "parent_sha=$PARENT_SHA"

# Use the FIRST module for the smoke test (multi-module aggregation is a follow-up).
FIRST_MODULE=$($PYTHON -c "
import json,sys
d = json.loads(sys.stdin.read())
m = d['modules'][0]
print(m['module_path'])
print(','.join(m['test_classes']))
print(','.join(m['production_globs']))
" <<<"$META_JSON")
MODULE_PATH=$(echo "$FIRST_MODULE" | sed -n '1p')
TEST_CLASSES=$(echo "$FIRST_MODULE" | sed -n '2p')
PRODUCTION_GLOBS=$(echo "$FIRST_MODULE" | sed -n '3p')
log "module=$MODULE_PATH test_classes=$TEST_CLASSES production_globs=$PRODUCTION_GLOBS"

if [[ -z "$MODULE_PATH" ]]; then
  MODULE_DIR="$REPO_DIR"
else
  MODULE_DIR="$REPO_DIR/$MODULE_PATH"
fi
# Decide build system: prefer Maven (pom.xml) → Gradle (build.gradle / .kts).
# Detection is per-side because some commits change/move build files between
# parent and refactor SHAs; we re-detect below in the loop.
detect_build_file() {
  local d="$1"
  if [[ -f "$d/pom.xml" ]]; then echo "$d/pom.xml maven"; return; fi
  if [[ -f "$d/build.gradle" ]]; then echo "$d/build.gradle gradle"; return; fi
  if [[ -f "$d/build.gradle.kts" ]]; then echo "$d/build.gradle.kts gradle"; return; fi
  echo " unknown"
}

write_log() {
  local side=$1 sha=$2 build_ok=$3 jacoco_ok=$4 pit_ok=$5 scope=$6 fw=$7 \
        recovery_layer=$8 jdk_version=$9 err=${10}
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s"\n' \
    "$COMMIT_URL" "$sha" "$side" "$build_ok" "$jacoco_ok" "$pit_ok" "$scope" \
    "$fw" "$recovery_layer" "$jdk_version" "${err//\"/\"\"}" \
    >>"$RUN_LOG"
}

# --- Per-commit isolated Maven local repo (-P 2 safe, plus parent-pom cache
#     reuse across before/after of THIS commit). Cleaned up at end of commit.
M2_LOCAL="/tmp/m2-${OWNER}__${REPO}__${SHA:0:10}"
mkdir -p "$M2_LOCAL"
cleanup_m2() { rm -rf "$M2_LOCAL"; }
trap cleanup_m2 EXIT

# --- Main loop --------------------------------------------------------------
for SIDE in before after; do
  if [[ "$SIDE" == "after" ]]; then
    TARGET_SHA=$SHA
  else
    TARGET_SHA=$PARENT_SHA
  fi

  build_ok=false jacoco_ok=false pit_ok=false fw=unknown bs=unknown err=""
  recovery_layer=none jdk_v=unknown

  out="$RESULTS_DIR/$TARGET_SHA"
  mkdir -p "$out/pit" "$out/jacoco"

  ( cd "$REPO_DIR" && git checkout -- . >/dev/null 2>&1 || true )
  if ! ( cd "$REPO_DIR" && git checkout -q "$TARGET_SHA" ); then
    err="checkout failed"
    write_log "$SIDE" "$TARGET_SHA" false false false narrow unknown none unknown "$err"
    continue
  fi

  read BUILD_FILE BUILD_SYSTEM <<<"$(detect_build_file "$MODULE_DIR")"
  bs="$BUILD_SYSTEM"
  if [[ "$BUILD_SYSTEM" == "unknown" ]]; then
    # No build file in the requested module dir — try the repo root as a
    # fallback (some commits store the only pom at the root).
    read BUILD_FILE BUILD_SYSTEM <<<"$(detect_build_file "$REPO_DIR")"
    bs="$BUILD_SYSTEM"
    if [[ "$BUILD_SYSTEM" == "unknown" ]]; then
      err="no pom or build.gradle in $MODULE_DIR or $REPO_DIR"
      write_log "$SIDE" "$TARGET_SHA" false false false narrow unknown none unknown "$err"
      continue
    fi
  fi

  fw=$($PYTHON "$HELPERS_DIR/detect_framework.py" "$BUILD_FILE" 2>/dev/null | awk '{print $1}')
  [[ -z "$fw" ]] && fw=unknown
  jdk_v=$($PYTHON "$HELPERS_DIR/detect_jdk_version.py" "$BUILD_FILE" 2>/dev/null)
  [[ -z "$jdk_v" ]] && jdk_v=unknown

  # Layer 2: image selection. For Maven, the build JVM matters because the
  # source/target compatibility settings in the pom force javac to that level.
  # For Gradle, source/target compatibility is just a bytecode target — the
  # build JVM can be newer. So for Gradle projects we default to JDK 17 (which
  # also makes the info.solidsoft.pitest plugin work — it requires JDK 11+),
  # falling back to older JDKs only when the wrapper rejects them (Layer 2 in
  # the Gradle branch).
  pit_version_to_use="$PIT_VERSION"
  if [[ "$BUILD_SYSTEM" == "gradle" ]]; then
    INSTALL_IMG="$DOCKER_IMG_JDK17"
    RUN_IMG="$DOCKER_IMG_JDK17"
    MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK9PLUS"
  else
    case "$jdk_v" in
      5|6|7|8)      INSTALL_IMG="$DOCKER_IMG_JDK8";  RUN_IMG="$DOCKER_IMG_JDK8"
                    pit_version_to_use="$PIT_VERSION_JDK8"
                    MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK8" ;;
      9|10|11)      INSTALL_IMG="$DOCKER_IMG_JDK11"; RUN_IMG="$DOCKER_IMG_JDK11"
                    MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK9PLUS" ;;
      21|22|23|24)  INSTALL_IMG="$DOCKER_IMG_JDK21"; RUN_IMG="$DOCKER_IMG_JDK21"
                    MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK9PLUS" ;;
      *)            INSTALL_IMG="$DOCKER_IMG_JDK17"; RUN_IMG="$DOCKER_IMG_JDK17"
                    MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK9PLUS" ;;
    esac
  fi

  log "[$SIDE $TARGET_SHA] build_system=$BUILD_SYSTEM framework=$fw jdk=$jdk_v pit=$pit_version_to_use install_img=${INSTALL_IMG##*:} run_img=${RUN_IMG##*:} build_file=$BUILD_FILE"

  inject_args=("$BUILD_FILE" --framework "$fw" --pit-version "$pit_version_to_use")
  if [[ "$pit_version_to_use" == "$PIT_VERSION_JDK8" ]]; then
    inject_args+=(--junit5-version "1.2.0")
  fi
  $PYTHON "$HELPERS_DIR/inject_pitest_plugin.py" "${inject_args[@]}" >&2 || true

  if [[ "$BUILD_SYSTEM" == "maven" ]]; then
    mvn_pl_install=""
    mvn_pl_run=""
    if [[ -n "$MODULE_PATH" ]]; then
      mvn_pl_install="-pl $MODULE_PATH -am"
      mvn_pl_run="-pl $MODULE_PATH"
    fi

    M2_FLAG="-Dmaven.repo.local=/m2"

    # Attempt 1: default flags, JDK image picked above.
    # IMPORTANT: -U forces SNAPSHOT update on every fetch. Without it, a
    # transient resolution failure on the first attempt is CACHED in the
    # local /m2 as a negative entry, and subsequent attempts (including
    # the later PIT/JaCoCo phases) won't retry. -U bypasses this cache.
    log "[$SIDE $TARGET_SHA] mvn install (attempt 1, $INSTALL_IMG)"
    if docker run --rm \
        -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$INSTALL_IMG" \
        bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B -U $M2_FLAG $mvn_pl_install -DskipTests install" \
        >"$out/build.log" 2>&1; then
      build_ok=true
    fi

    # Attempt 2 (Layer 1): retry with skip flags (kills quality-gate plugins).
    if ! $build_ok; then
      log "[$SIDE $TARGET_SHA] mvn install (attempt 2 — Layer 1 skip flags)"
      if docker run --rm \
          -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$INSTALL_IMG" \
          bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B -U $M2_FLAG $INSTALL_SKIP_FLAGS $mvn_pl_install -DskipTests install" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer1_skip_flags"
      fi
    fi

    # Attempt 3 (Layer 4): SNAPSHOT parent recovery.
    if ! $build_ok && grep -q "Non-resolvable parent POM" "$out/build.log"; then
      log "[$SIDE $TARGET_SHA] mvn install (attempt 3 — Layer 4 SNAPSHOT recovery)"
      if docker run --rm \
          -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$INSTALL_IMG" \
          bash -c "mvn -B -U $M2_FLAG $INSTALL_SKIP_FLAGS -N -DskipTests install ; \
                   mvn -B -U $M2_FLAG $INSTALL_SKIP_FLAGS $mvn_pl_install -DskipTests install" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer4_snapshot_recovery"
      fi
    fi

    # Attempt 4 (Layer 2 JDK fallback): if we were on JDK 17 and got a removed-API
    # NoClassDefFoundError, retry under JDK 11.
    if ! $build_ok && [[ "$INSTALL_IMG" == "$DOCKER_IMG_JDK17" ]] \
        && grep -qE "NoClassDefFoundError|cannot find symbol.*javax\.(annotation|xml\.bind|xml\.ws|activation)" "$out/build.log"; then
      log "[$SIDE $TARGET_SHA] mvn install (attempt 4 — Layer 2 JDK 11 fallback)"
      if docker run --rm \
          -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$DOCKER_IMG_JDK11" \
          bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B $M2_FLAG $INSTALL_SKIP_FLAGS $mvn_pl_install -DskipTests install" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer2_jdk11"
        INSTALL_IMG="$DOCKER_IMG_JDK11"
        RUN_IMG="$DOCKER_IMG_JDK11"
      fi
    fi

    # Attempt 5 (Layer 7 JDK 21 fallback): transitive dep compiled with newer
    # JDK, OR pom requires --release 21/19/etc. that the current javac doesn't
    # support. Triggers:
    # - "class file has wrong version 65.0" (JDK 21 transitive)
    # - "release version N not supported" (pom forces newer javac)
    if ! $build_ok \
        && grep -qE "class file has wrong version (61|62|63|64|65|66|67|68)\.0|release version (18|19|20|21|22|23|24) not supported" "$out/build.log"; then
      log "[$SIDE $TARGET_SHA] mvn install (attempt 5 — Layer 7 JDK 21 fallback)"
      if docker run --rm \
          -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$DOCKER_IMG_JDK21" \
          bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS_JDK9PLUS'; mvn -B $M2_FLAG $INSTALL_SKIP_FLAGS $mvn_pl_install -DskipTests install" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer7_jdk21"
        INSTALL_IMG="$DOCKER_IMG_JDK21"
        RUN_IMG="$DOCKER_IMG_JDK21"
        MVN_OPTS_ADDOPENS="$MVN_OPTS_ADDOPENS_JDK9PLUS"
        # PIT 1.20.6 supports JDK 21
      fi
    fi

    if $build_ok; then
      JACOCO_TEST_FILTER=$($PYTHON -c "
import sys
print(','.join(t.rsplit('.', 1)[-1] for t in sys.argv[1].split(',') if t))
" "$TEST_CLASSES")

      log "[$SIDE $TARGET_SHA] jacoco (-Dtest=$JACOCO_TEST_FILTER) on $RUN_IMG"
      if run_with_timeout "$JACOCO_TIMEOUT" docker run --rm \
          -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$RUN_IMG" \
          bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B -U $M2_FLAG $MEASURE_SKIP_FLAGS $mvn_pl_run org.jacoco:jacoco-maven-plugin:$JACOCO_VERSION:prepare-agent test org.jacoco:jacoco-maven-plugin:$JACOCO_VERSION:report -Dtest='$JACOCO_TEST_FILTER' -Dmaven.test.failure.ignore=true -Djacoco.haltOnFailure=false" \
          >"$out/jacoco.log" 2>&1; then
        found=$(find "$MODULE_DIR" -path '*/target/site/jacoco/jacoco.xml' -print -quit 2>/dev/null)
        if [[ -n "$found" ]]; then cp "$found" "$out/jacoco/"; jacoco_ok=true; fi
      fi
      # Layer 12: If JaCoCo produced no XML with the -Dtest filter (filter
      # matched nothing or test compile failed), retry without -Dtest so all
      # tests in the module run. Larger scope but non-empty coverage.
      if ! $jacoco_ok; then
        log "[$SIDE $TARGET_SHA] jacoco fallback: drop -Dtest filter (Layer 12)"
        if run_with_timeout "$JACOCO_TIMEOUT" docker run --rm \
            -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$RUN_IMG" \
            bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B -U $M2_FLAG $MEASURE_SKIP_FLAGS $mvn_pl_run org.jacoco:jacoco-maven-plugin:$JACOCO_VERSION:prepare-agent test org.jacoco:jacoco-maven-plugin:$JACOCO_VERSION:report -Dmaven.test.failure.ignore=true -Djacoco.haltOnFailure=false" \
            >>"$out/jacoco.log" 2>&1; then
          found=$(find "$MODULE_DIR" -path '*/target/site/jacoco/jacoco.xml' -print -quit 2>/dev/null)
          if [[ -n "$found" ]]; then
            cp "$found" "$out/jacoco/"
            jacoco_ok=true
            recovery_layer="${recovery_layer}+layer12_jacoco_unfiltered"
          fi
        fi
      fi

      # IMPORTANT: when invoking PIT via CLI plugin coordinate, the pom-block's
      # <configuration> is IGNORED. All settings must come from -D system
      # properties. Without -DoutputFormats=...,XML the run produces only HTML
      # and the find for mutations.xml fails — silently breaks pit_ok.
      # IMPORTANT: PIT's -DjvmArgs expects COMMA-separated args (each becomes
      # a separate JVM argument). Space-separated is interpreted as a single
      # opaque string by PIT and causes "Unrecognized option" on minion JVM.
      # Also JDK 8 does NOT support --add-opens (introduced in JDK 9), so for
      # JDK 8 we omit them.
      if [[ "$RUN_IMG" == "$DOCKER_IMG_JDK8" ]]; then
        pit_jvm_args="-Xmx4G"
      else
        pit_jvm_args="--add-opens=java.base/java.lang=ALL-UNNAMED,--add-opens=java.base/java.util=ALL-UNNAMED,--add-opens=java.base/java.time=ALL-UNNAMED,--add-opens=java.base/java.lang.reflect=ALL-UNNAMED,--add-opens=java.base/sun.nio.ch=ALL-UNNAMED,--add-opens=java.management/sun.management=ALL-UNNAMED,-Xmx10G"
      fi

      run_pitest_maven() {
        local globs=$1
        local label=$2
        local threads=${3:-6}
        log "[$SIDE $TARGET_SHA] pitest ($pit_version_to_use, $label glob, threads=$threads) on $RUN_IMG"
        run_with_timeout "$PIT_TIMEOUT" docker run --rm \
            -v "$REPO_DIR:/work" -v "$M2_LOCAL:/m2" -w /work "$RUN_IMG" \
            bash -c "export MAVEN_OPTS='$MVN_OPTS_ADDOPENS'; mvn -B -U $M2_FLAG $MEASURE_SKIP_FLAGS $mvn_pl_run org.pitest:pitest-maven:$pit_version_to_use:mutationCoverage \
              -DtargetClasses='$globs' \
              -DtargetTests='$TEST_CLASSES' \
              -DoutputFormats=HTML,XML,CSV \
              -DexportLineCoverage=true \
              -Dthreads=$threads \
              -DjvmArgs='$pit_jvm_args' \
              -DtimestampedReports=false" \
            >"$out/pit.log" 2>&1
        return $?
      }

      run_pitest_maven "$PRODUCTION_GLOBS" "narrow"
      pit_rc=$?
      # Layer 9: MINION_DIED → retry single-threaded for stability.
      if [[ $pit_rc -ne 0 ]] \
          && grep -q "MINION_DIED\|coverage generator minion" "$out/pit.log" 2>/dev/null; then
        log "[$SIDE $TARGET_SHA] pitest MINION_DIED detected; Layer 9 retry threads=1"
        run_pitest_maven "$PRODUCTION_GLOBS" "narrow-st" 1
        pit_rc=$?
      fi
      # Layer 8: "Skipping project because: ...no production code" — the target
      # module is a test-only / integration-test module. Retry without -pl so
      # PIT runs against the whole repo, scoped only by targetClasses.
      if grep -q "Project has either no tests or no production code" "$out/pit.log" 2>/dev/null; then
        log "[$SIDE $TARGET_SHA] pitest 'no production code' on module; retry without -pl"
        BROAD_GLOBS=$($PYTHON -c "
import sys, re
tcs = sys.argv[1].split(',')
pkgs = set()
for t in tcs:
    if '.' not in t: continue
    pkg = t.rsplit('.', 1)[0]
    pkg = re.sub(r'\.tests?$', '', pkg)
    pkgs.add(pkg + '.**')
print(','.join(sorted(pkgs)))
" "$TEST_CLASSES")
        saved_pl_run="$mvn_pl_run"
        mvn_pl_run=""
        run_pitest_maven "$BROAD_GLOBS" "all-modules"
        mvn_pl_run="$saved_pl_run"
      fi
      # If narrow glob produced 0 mutations (jitwatch-class case), broaden:
      # 1) take each test class's package
      # 2) strip `.test` / `.tests` suffix if present (test code often lives
      #    under `<group>.test.<x>` while production is under `<group>.<x>`)
      # 3) climb one level up
      # 4) glob recursively with `.**` (matches all subpackages, PIT syntax)
      if [[ $pit_rc -ne 0 ]] || ! find "$MODULE_DIR" -path '*/target/pit-reports/mutations.xml' -print -quit 2>/dev/null | grep -q .; then
        if grep -q "No mutations found\|Created 0 mutation test units" "$out/pit.log" 2>/dev/null; then
          BROAD_GLOBS=$($PYTHON -c "
import sys, re
tcs = sys.argv[1].split(',')
pkgs = set()
for t in tcs:
    if '.' not in t: continue
    pkg = t.rsplit('.', 1)[0]
    pkg = re.sub(r'\.tests?$', '', pkg)   # strip .test or .tests
    pkgs.add(pkg + '.**')                 # recursive glob
    if '.' in pkg:
        pkgs.add(pkg.rsplit('.', 1)[0] + '.**')   # climb one level
print(','.join(sorted(pkgs)))
" "$TEST_CLASSES")
          log "[$SIDE $TARGET_SHA] pitest 0 mutations from narrow glob; retry with package-broad: $BROAD_GLOBS"
          run_pitest_maven "$BROAD_GLOBS" "broad"
          # Layer 11: still 0 mutations → use the absolute broadest (everything).
          if grep -q "No mutations found\|Created 0 mutation test units" "$out/pit.log" 2>/dev/null; then
            log "[$SIDE $TARGET_SHA] pitest 0 mutations from package-broad; Layer 11 retry with **"
            run_pitest_maven "**" "all"
          fi
        fi
      fi
      found=$(find "$MODULE_DIR" -path '*/target/pit-reports/mutations.xml' -print -quit 2>/dev/null)
      if [[ -n "$found" ]]; then cp "$found" "$out/pit/"; pit_ok=true; fi
      cov=$(find "$MODULE_DIR" -path '*/target/pit-reports/linecoverage.xml' -print -quit 2>/dev/null)
      if [[ -n "$cov" ]]; then cp "$cov" "$out/pit/"; fi
    else
      err="install failed"
    fi
  elif [[ "$BUILD_SYSTEM" == "gradle" ]]; then
    # Gradle path: PIT exportLineCoverage produces linecoverage.xml; we don't
    # also run a separate JaCoCo phase. Module addressed by Gradle path syntax (":mod").
    GRADLE_MODULE=":${MODULE_PATH//\//:}"
    [[ "$GRADLE_MODULE" == ":" ]] && GRADLE_MODULE=""
    GRADLE_HOME_VOL="-v $HOME/.gradle:/root/.gradle"

    # Attempt 1: default JDK image (JDK 17 unless we detected older).
    log "[$SIDE $TARGET_SHA] gradle assemble (attempt 1, $RUN_IMG)"
    if run_with_timeout "$JACOCO_TIMEOUT" docker run --rm \
        -v "$REPO_DIR:/work" $GRADLE_HOME_VOL -w /work "$RUN_IMG" \
        bash -c "[[ -x ./gradlew ]] && chmod +x ./gradlew; ./gradlew $GRADLE_MODULE:assemble --no-daemon" \
        >"$out/build.log" 2>&1; then
      build_ok=true
    fi

    # Attempt 2 (Layer 2 JDK 11 fallback): old wrapper rejects JDK 17.
    if ! $build_ok && [[ "$RUN_IMG" != "$DOCKER_IMG_JDK11" ]] \
        && grep -qE "Could not determine java version|requires Gradle.*older|Unsupported class file major version" "$out/build.log"; then
      log "[$SIDE $TARGET_SHA] gradle assemble (attempt 2 — Layer 2 JDK 11 fallback)"
      if run_with_timeout "$JACOCO_TIMEOUT" docker run --rm \
          -v "$REPO_DIR:/work" $GRADLE_HOME_VOL -w /work "$DOCKER_IMG_JDK11" \
          bash -c "[[ -x ./gradlew ]] && chmod +x ./gradlew; ./gradlew $GRADLE_MODULE:assemble --no-daemon" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer2_jdk11"
        RUN_IMG="$DOCKER_IMG_JDK11"
      fi
    fi

    # Attempt 3 (Layer 2 JDK 8 fallback): wrapper too old even for JDK 11.
    # Reinject the plugin with the JDK 8 PIT version since we'll change tooling.
    if ! $build_ok && [[ "$RUN_IMG" != "$DOCKER_IMG_JDK8" ]] \
        && grep -qE "Could not determine java version" "$out/build.log"; then
      log "[$SIDE $TARGET_SHA] gradle assemble (attempt 3 — Layer 2 JDK 8 fallback)"
      ( cd "$REPO_DIR" && git checkout -- "$BUILD_FILE" >/dev/null 2>&1 || true )
      $PYTHON "$HELPERS_DIR/inject_pitest_plugin.py" \
        "$BUILD_FILE" --framework "$fw" \
        --pit-version "$PIT_VERSION_JDK8" --junit5-version "1.2.0" >&2 || true
      if run_with_timeout "$JACOCO_TIMEOUT" docker run --rm \
          -v "$REPO_DIR:/work" $GRADLE_HOME_VOL -w /work "$DOCKER_IMG_JDK8" \
          bash -c "[[ -x ./gradlew ]] && chmod +x ./gradlew; ./gradlew $GRADLE_MODULE:assemble --no-daemon" \
          >>"$out/build.log" 2>&1; then
        build_ok=true
        recovery_layer="layer2_jdk8"
        RUN_IMG="$DOCKER_IMG_JDK8"
      fi
    fi

    if $build_ok; then
      log "[$SIDE $TARGET_SHA] pitest (gradle) on $RUN_IMG"
      if run_with_timeout "$PIT_TIMEOUT" docker run --rm \
          -v "$REPO_DIR:/work" $GRADLE_HOME_VOL -w /work "$RUN_IMG" \
          bash -c "./gradlew $GRADLE_MODULE:pitest --no-daemon \
            -PtargetClasses='$PRODUCTION_GLOBS' \
            -PtargetTests='$TEST_CLASSES'" \
          >"$out/pit.log" 2>&1; then
        found=$(find "$MODULE_DIR" -path '*/build/reports/pitest/mutations.xml' -print -quit 2>/dev/null)
        if [[ -n "$found" ]]; then cp "$found" "$out/pit/"; pit_ok=true; fi
        cov=$(find "$MODULE_DIR" -path '*/build/reports/pitest/linecoverage.xml' -print -quit 2>/dev/null)
        if [[ -n "$cov" ]]; then cp "$cov" "$out/pit/"; fi
      fi
    else
      err="gradle assemble failed"
    fi
  else
    err="unknown build system"
  fi

  ( cd "$REPO_DIR" && git checkout -- . >/dev/null 2>&1 || true )
  write_log "$SIDE" "$TARGET_SHA" "$build_ok" "$jacoco_ok" "$pit_ok" narrow \
            "$fw($bs)" "$recovery_layer" "$jdk_v" "$err"
done

log "done. log=$RUN_LOG"
