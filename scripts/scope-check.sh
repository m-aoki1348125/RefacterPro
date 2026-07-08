#!/usr/bin/env bash
# scope-check.sh -- verify every changed/added file is covered by the approved fileset (gate G5).
#
# Usage: scope-check.sh <start_sha> <fileset_file>
#   Fileset file format: one entry per line; an exact repo-relative path, or a
#   directory prefix ending with '/'. Blank lines and lines starting with '#'
#   are ignored; trailing '#' comments are stripped.
#   Orchestrator-owned paths (.refactor/ledger.md, .refactor/waves/, .refactor/logs/)
#   are always allowed. Any other change under .refactor/ is a violation:
#   workers must never touch workflow state (this also catches golden-manifest
#   tampering before G6 does).
# Exit 0 = all changes in scope. Exit 1 = violations (listed on stdout).

set -u

START_SHA="${1:?usage: scope-check.sh <start_sha> <fileset_file>}"
FILESET_FILE="${2:?usage: scope-check.sh <start_sha> <fileset_file>}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: not inside a git repository" >&2
  exit 2
}
cd "$REPO_ROOT"
[ -f "$FILESET_FILE" ] || {
  echo "FATAL: fileset file not found: $FILESET_FILE" >&2
  exit 2
}

# Changed files (committed/staged/unstaged vs start_sha) plus untracked files.
changed="$({
  git diff --name-only "$START_SHA" --
  git ls-files --others --exclude-standard
} | sort -u)"

violations=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in
  .refactor/ledger.md | .refactor/waves/* | .refactor/logs/*) continue ;;
  esac
  allowed=0
  while IFS= read -r entry; do
    entry="${entry%%#*}"
    entry="$(printf '%s' "$entry" | sed 's/[[:space:]]*$//')"
    [ -z "$entry" ] && continue
    case "$entry" in
    */)
      case "$f" in "$entry"*)
        allowed=1
        break
        ;;
      esac
      ;;
    *)
      if [ "$f" = "$entry" ]; then
        allowed=1
        break
      fi
      ;;
    esac
  done <"$FILESET_FILE"
  if [ "$allowed" -eq 0 ]; then
    echo "OUT-OF-SCOPE: $f"
    violations=$((violations + 1))
  fi
done <<EOF
$changed
EOF

if [ "$violations" -eq 0 ]; then
  echo "scope-check: OK (all changes within approved fileset)"
  exit 0
else
  echo "scope-check: $violations file(s) outside approved fileset"
  exit 1
fi
