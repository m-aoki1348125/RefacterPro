#!/usr/bin/env bash
# setup.sh -- prepare an isolated test repository from sample-legacy for E2E runs.
#
# Copies sample-legacy/ into a fresh directory (outside this plugin repo, so the
# workflow agents cannot read e2e/answer-key.md) and initializes it as a git repo.
#
# Usage: setup.sh [target_dir]
#   Default target: a fresh temp directory. Prints the target path on stdout.

set -eu

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../sample-legacy" && pwd)"
TARGET="${1:-$(mktemp -d /tmp/refactor-pro-e2e.XXXXXX)}"

mkdir -p "$TARGET"
cp -R "$SRC/." "$TARGET/"
# Strip bytecode caches from previous local runs; the test repo must start
# without ignore rules so the workflow's Phase-0 hygiene step gets exercised.
find "$TARGET" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cd "$TARGET"
git init -q
git config user.email "e2e@refactor-pro.local"
git config user.name "refactor-pro-e2e"
git add -A
git commit -qm "Import ORDSYS/85 legacy codebase"

echo "$TARGET"
