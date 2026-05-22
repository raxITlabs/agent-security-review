#!/usr/bin/env bash
# Install the scan-agent-code skill into ~/.claude/skills/ (standalone, no plugin needed).
#
#   curl -fsSL https://raw.githubusercontent.com/raxITlabs/agent-code-scanner-rules/main/install.sh | bash
#
# Optional: pass a branch, tag, or commit SHA to pin a version:
#   curl -fsSL .../install.sh | bash -s -- v0.1.0
set -euo pipefail

REPO="raxITlabs/agent-code-scanner-rules"
REF="${1:-main}"
SRC_SUBDIR="plugins/agent-code-scanner/skills/scan-agent-code"
DEST="$HOME/.claude/skills/scan-agent-code"

echo "Installing scan-agent-code skill from ${REPO}@${REF} ..."

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# One request, no git dependency; --strip-components drops the top repo dir.
curl -fsSL "https://codeload.github.com/${REPO}/tar.gz/${REF}" | tar -xz -C "$tmp" --strip-components=1

src="${tmp}/${SRC_SUBDIR}"
if [ ! -f "${src}/SKILL.md" ]; then
  echo "error: SKILL.md not found in the downloaded archive (${SRC_SUBDIR})" >&2
  exit 1
fi

mkdir -p "$DEST"
# Copy the skill (SKILL.md + scripts/ + references/), excluding any local runtime cache.
( cd "$src" && tar --exclude='./.cache' -cf - . ) | tar -xf - -C "$DEST"

echo "Installed to ${DEST}"
echo
echo "ast-grep is required to run scans. If you don't have it:"
echo "  brew install ast-grep   |   npm i -g @ast-grep/cli   |   pip install ast-grep-cli"
echo
echo "Then in Claude Code, just ask: \"security-review my agent code\" (or /scan-agent-code)."
