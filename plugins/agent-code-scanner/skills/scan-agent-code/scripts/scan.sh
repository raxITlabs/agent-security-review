#!/usr/bin/env bash
# Scan a target with the agent-code-scanner-rules pack and emit ast-grep JSON.
#
# Usage:  scan.sh <path-to-code> [--pin <sha|tag>]
# Output: ast-grep JSON findings on STDOUT.
# Exit:   ast-grep's code (1 when any error-severity rule matches) is preserved.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGET="."
PIN="main"
while [ $# -gt 0 ]; do
  case "$1" in
    --pin) PIN="${2:-main}"; shift 2 ;;
    *)     TARGET="$1"; shift ;;
  esac
done

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
ast-grep scan --config "${ROOT}/sgconfig.yml" --json --include-metadata "$TARGET"
