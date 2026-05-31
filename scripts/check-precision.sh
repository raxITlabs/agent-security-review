#!/usr/bin/env bash
# Precision regression check for the heuristic rules that are prone to false
# positives or that were silently broken (credentials, module-scope env secrets,
# tool dispatch, RAG, and the decorator-anchored MCP / gateway / principal rules).
#
# Unlike run-fixtures.sh (which clones whole repos and compares per-rule totals),
# this asserts behaviour at the line level on a small hand-written corpus:
#
#   # EXPECT_MATCH            -> some rule must fire covering this line
#   # EXPECT_NONE             -> NO rule may fire covering this line
#   # EXPECT_MATCH:rule-id    -> that specific rule must fire covering this line
#   # EXPECT_NONE:rule-id     -> that specific rule must NOT fire covering this line
#
# "Covering" means the finding's start..end range includes the tagged line — a
# finding on a decorated function spans the whole `decorated_definition`, so the
# tag can sit on the relevant body line. The `:rule-id` form lets one function be
# asserted per-rule when several rules evaluate it (e.g. a URL-validated tool that
# is SSRF-safe but still lacks a principal param).
#
# This pins the true-positive / false-positive boundary, so a future rule edit
# that re-broadens or re-breaks a pattern fails CI here.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORPUS="$REPO_ROOT/fixtures/precision"
SGCONFIG="$REPO_ROOT/sgconfig.yml"

command -v ast-grep >/dev/null 2>&1 || { echo "ERROR: ast-grep not installed"; exit 1; }

findings_json="$(ast-grep scan --json --config "$SGCONFIG" "$CORPUS" 2>/dev/null || true)"

FINDINGS_JSON="$findings_json" CORPUS="$CORPUS" python3 - <<'PY'
import json, os, sys, glob

findings = json.loads(os.environ["FINDINGS_JSON"] or "[]")

# Each finding covers an inclusive 1-based line range [start, end].
spans = []  # (basename, start, end, ruleId)
for f in findings:
    name = os.path.basename(f.get("file", ""))
    rng = f.get("range") or {}
    s = (rng.get("start") or {}).get("line")
    e = (rng.get("end") or {}).get("line", s)
    if s is None:
        continue
    spans.append((name, s + 1, e + 1, f.get("ruleId", "")))

def rules_covering(name, line):
    return {rid for (n, s, e, rid) in spans if n == name and s <= line <= e}

fails, checked = [], 0
for path in sorted(glob.glob(os.path.join(os.environ["CORPUS"], "*"))):
    name = os.path.basename(path)
    for i, text in enumerate(open(path, encoding="utf-8"), start=1):
        stripped = text.rstrip()
        # Find a trailing marker, optionally scoped to a rule id.
        marker = None
        for tag in ("EXPECT_MATCH", "EXPECT_NONE"):
            idx = stripped.rfind(tag)
            if idx == -1:
                continue
            rest = stripped[idx + len(tag):]
            # accept "" (line end) or ":rule-id" at the very end of the line
            if rest == "" or (rest.startswith(":") and " " not in rest):
                marker = (tag, rest[1:] if rest.startswith(":") else None)
                break
        if marker is None:
            continue
        tag, rid = marker
        checked += 1
        covering = rules_covering(name, i)
        if rid:
            got = rid in covering
        else:
            got = len(covering) > 0
        scope = f" [{rid}]" if rid else ""
        if tag == "EXPECT_MATCH" and not got:
            fails.append(f"  {name}:{i}  EXPECT_MATCH{scope} but no such finding  -> {text.strip()}")
        if tag == "EXPECT_NONE" and got:
            hitlist = rid or ",".join(sorted(covering))
            fails.append(f"  {name}:{i}  EXPECT_NONE{scope} but matched by {hitlist}  -> {text.strip()}")

print(f"precision corpus: {checked} tagged assertions checked, {len(fails)} failure(s)")
if fails:
    print("\n".join(fails))
    sys.exit(1)
print("✓ all precision expectations met")
PY
