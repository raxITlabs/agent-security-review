#!/usr/bin/env bash
# Resolve the agent-code-scanner-rules pack: fetch latest from GitHub, cache it,
# and fall back to the bundled vendored copy when there is no network.
#
# Prints the resolved rules-root (the directory containing sgconfig.yml) to STDOUT.
# All diagnostics go to STDERR so callers can capture the path cleanly:
#     ROOT="$(bash fetch_rules.sh [<pin>])"
#
# pin: a branch (default "main"), tag, or commit SHA. Immutable pins are cached
# forever; "main" is refreshed once it is older than RULES_TTL_HOURS (default 6).
set -uo pipefail

OWNER="raxITlabs"
REPO="agent-code-scanner-rules"
PIN="${1:-${RULES_PIN:-main}}"
TTL_HOURS="${RULES_TTL_HOURS:-6}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="${SKILL_DIR}/.cache/${PIN}"
VENDORED="${SKILL_DIR}/references/rules-vendored"
MARKER="${CACHE}/.fetched_at"

log() { printf 'fetch_rules: %s\n' "$*" >&2; }

fetch() {
  local url tmp
  url="https://codeload.github.com/${OWNER}/${REPO}/tar.gz/${PIN}"
  tmp="$(mktemp -d)"
  # One request, no git dependency; --strip-components drops the top repo dir.
  if curl -fsSL --max-time 45 "$url" | tar -xz -C "$tmp" --strip-components=1 2>/dev/null \
     && [ -f "${tmp}/sgconfig.yml" ]; then
    rm -rf "$CACHE"; mkdir -p "$(dirname "$CACHE")"; mv "$tmp" "$CACHE"
    date -u +%FT%TZ > "$MARKER" 2>/dev/null || true
    return 0
  fi
  rm -rf "$tmp"; return 1
}

need_fetch=false
if [ ! -f "${CACHE}/sgconfig.yml" ]; then
  need_fetch=true
elif [ "$PIN" = "main" ] && [ -n "$(find "$MARKER" -mmin "+$((TTL_HOURS * 60))" 2>/dev/null)" ]; then
  need_fetch=true   # mutable ref and cache is stale -> refresh
fi

if $need_fetch; then
  if fetch; then
    log "using freshly fetched rules (${PIN})"
  elif [ -f "${CACHE}/sgconfig.yml" ]; then
    log "fetch failed; using stale cache (${PIN})"
  else
    log "fetch failed and no cache; using bundled vendored fallback"
    echo "$VENDORED"; exit 0
  fi
else
  log "using cached rules (${PIN})"
fi

echo "$CACHE"
