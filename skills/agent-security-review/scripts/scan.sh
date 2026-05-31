#!/usr/bin/env bash
# Scan a target with the agent-security-review pack and emit ast-grep JSON.
#
# Usage:  scan.sh <path-to-code> [--pin <sha|tag>] [--include-tests]
# Output: ast-grep JSON findings on STDOUT.
# Exit:   ast-grep's code (1 when any error-severity rule matches) is preserved.
#
# By default, test / eval / example / fixture directories are excluded: a finding
# in a test is rarely the shipped attack surface, and the pack's heuristic rules
# (env-var reads, ungated calls) fire there constantly, drowning real signal.
# Pass --include-tests to scan everything.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGET="."
PIN="main"
INCLUDE_TESTS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --pin) PIN="${2:-main}"; shift 2 ;;
    --include-tests) INCLUDE_TESTS=1; shift ;;
    *)     TARGET="$1"; shift ;;
  esac
done

# Default-excluded non-shipping directories (override with --include-tests).
GLOBS=()
if [ "$INCLUDE_TESTS" -eq 0 ]; then
  for pat in '**/test/**' '**/tests/**' '**/__tests__/**' '**/evals/**' \
             '**/eval/**' '**/examples/**' '**/example/**' '**/fixtures/**' \
             '**/samples/**' '**/*_test.py' '**/test_*.py' '**/*.test.ts' \
             '**/*.spec.ts'; do
    GLOBS+=(--globs "!$pat")
  done
  echo "scan.sh: excluding test/eval/example dirs (use --include-tests to scan them)" >&2
fi

if ! command -v ast-grep >/dev/null 2>&1; then
  {
    echo "ast-grep CLI not found. Install one of:"
    echo "  brew install ast-grep | npm i -g @ast-grep/cli | pip install ast-grep-cli | cargo install ast-grep --locked"
  } >&2
  exit 127
fi

ROOT="$(bash "${SKILL_DIR}/scripts/fetch_rules.sh" "$PIN")"
if [ ! -f "${ROOT}/sgconfig.yml" ]; then
  echo "scan.sh: no usable ruleset at ${ROOT}" >&2
  exit 1
fi

# --include-metadata so the report can group by component / architectural shift.
ast-grep scan --config "${ROOT}/sgconfig.yml" --json --include-metadata ${GLOBS[@]+"${GLOBS[@]}"} "$TARGET"
