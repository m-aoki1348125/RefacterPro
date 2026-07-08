#!/usr/bin/env bash
# wave-gate.sh -- deterministic machine gates (G1-G6, G8) for refactor-pro waves.
#
# Usage: wave-gate.sh <start_sha> <fileset_file> [max_diff_lines]
#   Run from anywhere inside the target repo. Reads .refactor/gates.env.
#   Exit 0 = all machine gates PASS. Non-zero = at least one gate FAIL.
#   Full command logs are written to .refactor/logs/gate-<timestamp>/.
#   G7 (adversarial LLM verification) is NOT part of this script by design:
#   machine gates must stay deterministic. The orchestrator runs G7 afterwards.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

START_SHA="${1:?usage: wave-gate.sh <start_sha> <fileset_file> [max_diff_lines]}"
FILESET_FILE="${2:?usage: wave-gate.sh <start_sha> <fileset_file> [max_diff_lines]}"
MAX_LINES_OVERRIDE="${3:-}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: not inside a git repository" >&2
  exit 2
}
cd "$REPO_ROOT"

GATES_ENV=".refactor/gates.env"
[ -f "$GATES_ENV" ] || {
  echo "FATAL: $GATES_ENV not found (run /refactor-init first)" >&2
  exit 2
}

# Defaults; gates.env overrides.
BUILD_CMD=""
TYPECHECK_CMD=""
CHAR_TEST_CMD=""
GATE_TEST_CMD=""
LINT_COUNT_CMD=""
LINT_MAX_ERRORS=0
PROTECTED_PATHS=""
GOLDEN_MANIFEST=".refactor/golden.sha256"
MAX_DIFF_LINES=1500
# shellcheck disable=SC1090
. "$GATES_ENV"

MAX_LINES="${MAX_LINES_OVERRIDE:-$MAX_DIFF_LINES}"

LOG_DIR=".refactor/logs/gate-$(date +%Y%m%dT%H%M%S)"
mkdir -p "$LOG_DIR"

FAILED=0

run_cmd_gate() { # $1=gate id, $2=label, $3=command (empty => SKIP)
  local id="$1" label="$2" cmd="$3"
  if [ -z "$cmd" ]; then
    echo "$id $label: SKIP (not configured)"
    return 0
  fi
  local log="$LOG_DIR/$id.log"
  if bash -c "$cmd" >"$log" 2>&1; then
    echo "$id $label: PASS"
  else
    echo "$id $label: FAIL (log: $log)"
    tail -n 20 "$log" | sed 's/^/    /'
    FAILED=1
  fi
}

# G1 build
run_cmd_gate "G1" "build" "$BUILD_CMD"

# G2 typecheck
run_cmd_gate "G2" "typecheck" "$TYPECHECK_CMD"

# G3 tests -- characterization tests are mandatory at execution time.
if [ -z "$CHAR_TEST_CMD" ]; then
  echo "G3a char-test: FAIL (CHAR_TEST_CMD is empty; characterization tests are required -- run /refactor-safety-net)"
  FAILED=1
else
  run_cmd_gate "G3a" "char-test" "$CHAR_TEST_CMD"
fi
run_cmd_gate "G3b" "gate-test" "$GATE_TEST_CMD"

# G4 lint ratchet: LINT_COUNT_CMD must print an integer error count.
if [ -z "$LINT_COUNT_CMD" ]; then
  echo "G4 lint: SKIP (not configured)"
else
  lint_log="$LOG_DIR/G4.log"
  lint_count="$(bash -c "$LINT_COUNT_CMD" 2>"$lint_log" | tail -n 1 | tr -d '[:space:]')"
  if printf '%s' "$lint_count" | grep -Eq '^[0-9]+$' && [ "$lint_count" -le "$LINT_MAX_ERRORS" ]; then
    echo "G4 lint: PASS ($lint_count <= baseline $LINT_MAX_ERRORS)"
  else
    echo "G4 lint: FAIL (count='$lint_count', baseline=$LINT_MAX_ERRORS, log: $lint_log)"
    FAILED=1
  fi
fi

# G5 scope
if bash "$SCRIPT_DIR/scope-check.sh" "$START_SHA" "$FILESET_FILE" >"$LOG_DIR/G5.log" 2>&1; then
  echo "G5 scope: PASS"
else
  echo "G5 scope: FAIL (log: $LOG_DIR/G5.log)"
  sed 's/^/    /' "$LOG_DIR/G5.log"
  FAILED=1
fi

# G6 golden
if bash "$SCRIPT_DIR/golden-check.sh" "$START_SHA" >"$LOG_DIR/G6.log" 2>&1; then
  echo "G6 golden: PASS"
else
  echo "G6 golden: FAIL (log: $LOG_DIR/G6.log)"
  sed 's/^/    /' "$LOG_DIR/G6.log"
  FAILED=1
fi

# G8 size: total changed lines (insertions + deletions) vs wave limit.
# Untracked (newly created) files are invisible to `git diff`, so count their
# lines separately -- otherwise workers could smuggle unlimited new code.
shortstat="$(git diff --shortstat "$START_SHA" 2>/dev/null)"
ins="$(printf '%s' "$shortstat" | grep -Eo '[0-9]+ insertion' | grep -Eo '[0-9]+' || echo 0)"
del="$(printf '%s' "$shortstat" | grep -Eo '[0-9]+ deletion' | grep -Eo '[0-9]+' || echo 0)"
untracked=0
while IFS= read -r uf; do
  [ -f "$uf" ] || continue
  case "$uf" in .refactor/logs/*) continue ;; esac
  untracked=$((untracked + $(wc -l <"$uf")))
done <<EOF
$(git ls-files --others --exclude-standard)
EOF
total=$((${ins:-0} + ${del:-0} + untracked))
if [ "$total" -le "$MAX_LINES" ]; then
  echo "G8 size: PASS ($total <= $MAX_LINES changed lines)"
else
  echo "G8 size: FAIL ($total > $MAX_LINES changed lines)"
  FAILED=1
fi

if [ "$FAILED" -eq 0 ]; then
  echo "RESULT: ALL MACHINE GATES PASS (run G7 verifier next)"
  exit 0
else
  echo "RESULT: GATE FAILURE (logs: $LOG_DIR)"
  exit 1
fi
