#!/usr/bin/env bash
# Markdown / prompt-surface injection pre-pass.
#
# ast-grep has no markdown parser, so prompt-injection text planted in the agent
# *prompt surface* — .cursorrules, .cursor/rules/*.mdc, SKILL.md, AGENTS.md,
# CLAUDE.md, copilot-instructions.md — is structurally invisible to the rule pack.
# This is exactly the Cursor/Claude-Code blind spot the coverage audit found.
#
# This helper greps those files for imperative override phrases and emits findings
# in the SAME JSON shape ast-grep uses, so report.py can consume them unchanged.
#
# Usage:  scan-markdown.sh <path-to-code>
# Output: JSON array of findings on STDOUT (empty array if none).
set -uo pipefail

TARGET="${1:-.}"

# Files that are part of the model's instruction/prompt surface.
NAME_GLOBS=(
  -iname '.cursorrules'
  -o -iname '*.mdc'
  -o -iname 'SKILL.md'
  -o -iname 'AGENTS.md'
  -o -iname 'CLAUDE.md'
  -o -iname 'copilot-instructions.md'
  -o -iname '.windsurfrules'
)

# Imperative override phrases — the same class the MCP tool-description rule looks
# for, applied to the markdown prompt surface.
PHRASE='ignore (all )?previous|ignore (the )?above|disregard (all|previous|prior)|you are now|new instructions|system prompt|exfiltrat|send .* to (http|attacker|evil)|override (the )?rules|do not tell the user|without (asking|confirmation)'

python3 - "$TARGET" "$PHRASE" <<'PY' "${NAME_GLOBS[@]}"
import json, os, re, subprocess, sys

target, phrase = sys.argv[1], sys.argv[2]
name_globs = sys.argv[3:]  # passed through to `find`

# Collect candidate files via find (portable, respects the name globs).
cmd = ["find", target, "-type", "f", "("] + name_globs + [")"]
try:
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
except Exception:
    out = ""
files = [f for f in out.splitlines() if f.strip()]

rx = re.compile(phrase, re.IGNORECASE)
findings = []
for path in files:
    try:
        lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    except Exception:
        continue
    for i, line in enumerate(lines):
        if rx.search(line):
            findings.append({
                "ruleId": "scope.prompt-injection-in-instruction-file",
                "severity": "warning",
                "file": path,
                "range": {"start": {"line": i, "column": 0},
                           "end": {"line": i, "column": len(line)}},
                "lines": line.strip()[:200],
                "message": (
                    "Imperative override phrase in an agent instruction / prompt-surface "
                    "file (.cursorrules / *.mdc / SKILL.md / AGENTS.md / CLAUDE.md). These "
                    "files are injected into the model's context, so an attacker who can edit "
                    "one can plant instructions.\n"
                    "Architectural fix: treat instruction files as code — review changes, keep "
                    "them describing purpose, not commanding the model to override safety (Shift 1)."
                ),
                "metadata": {"shift": "scope", "component": "config", "confidence": "low"},
            })

json.dump(findings, sys.stdout, indent=2)
PY
