#!/usr/bin/env bash
# golden-check.sh -- verify protected paths and golden masters are untouched (gate G6).
#
# Usage: golden-check.sh <start_sha>
#   Reads .refactor/gates.env:
#     PROTECTED_PATHS  space-separated repo-relative paths/dirs (characterization
#                      tests, golden master dirs). Must show no diff vs start_sha,
#                      no staged/unstaged changes, no untracked additions.
#     GOLDEN_MANIFEST  shasum -a 256 manifest (paths relative to repo root).
#                      The manifest itself must be unchanged since start_sha, and
#                      every listed file must match its recorded checksum.
# Exit 0 = intact. Exit 1 = tampering detected. Exit 2 = usage/environment error.

set -u

START_SHA="${1:?usage: golden-check.sh <start_sha>}"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: not inside a git repository" >&2
  exit 2
}
cd "$REPO_ROOT"

GATES_ENV=".refactor/gates.env"
[ -f "$GATES_ENV" ] || {
  echo "FATAL: $GATES_ENV not found" >&2
  exit 2
}
PROTECTED_PATHS=""
GOLDEN_MANIFEST=".refactor/golden.sha256"
# shellcheck disable=SC1090
. "$GATES_ENV"

fail=0

# 1. Protected paths untouched (committed diff + working tree + untracked).
if [ -n "$PROTECTED_PATHS" ]; then
  # shellcheck disable=SC2086
  touched="$({
    git diff --name-only "$START_SHA" -- $PROTECTED_PATHS
    git ls-files --others --exclude-standard -- $PROTECTED_PATHS
  } | sort -u)"
  if [ -n "$touched" ]; then
    echo "PROTECTED PATH MODIFIED:"
    printf '%s\n' "$touched" | sed 's/^/    /'
    fail=1
  fi
else
  echo "note: PROTECTED_PATHS is empty (no protected paths configured)"
fi

# 2 + 3. Manifest unchanged, and all golden checksums match.
if [ -f "$GOLDEN_MANIFEST" ]; then
  if [ -n "$(git diff --name-only "$START_SHA" -- "$GOLDEN_MANIFEST")" ]; then
    echo "MANIFEST MODIFIED: $GOLDEN_MANIFEST"
    fail=1
  fi
  if command -v shasum >/dev/null 2>&1; then
    SHACMD="shasum -a 256"
  elif command -v sha256sum >/dev/null 2>&1; then
    SHACMD="sha256sum"
  else
    echo "FATAL: neither shasum nor sha256sum available" >&2
    exit 2
  fi
  if ! $SHACMD --check --status "$GOLDEN_MANIFEST" 2>/dev/null; then
    echo "GOLDEN CHECKSUM MISMATCH:"
    $SHACMD --check "$GOLDEN_MANIFEST" 2>&1 | grep -v ': OK$' | sed 's/^/    /'
    fail=1
  fi
else
  echo "note: golden manifest not found ($GOLDEN_MANIFEST) -- checksum verification skipped"
fi

if [ "$fail" -eq 0 ]; then
  echo "golden-check: OK"
  exit 0
else
  echo "golden-check: TAMPERING DETECTED"
  exit 1
fi
