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
# Fixtures that can't carry inline comment tags (e.g. JSON config) use a sidecar
# `<fixture>.expected.json` mapping {ruleId: exact-count} for that one file.
#
# This pins the true-positive / false-positive boundary, so a future rule edit
# that re-broadens or re-breaks a pattern fails CI here.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORPUS="$REPO_ROOT/fixtures/precision"
SGCONFIG="$REPO_ROOT/sgconfig.yml"

command -v ast-grep >/dev/null 2>&1 || { echo "ERROR: ast-grep not installed"; exit 1; }

# Pass findings to Python via a TEMP FILE, not an env var. On Linux a single env
# string is capped at 128 KB (MAX_ARG_STRLEN), so the full-corpus JSON blew up as
# "Argument list too long" in CI (macOS has no such cap, so it passed locally).
FINDINGS_FILE="$(mktemp)"
trap 'rm -f "$FINDINGS_FILE"' EXIT
ast-grep scan --json --config "$SGCONFIG" "$CORPUS" > "$FINDINGS_FILE" 2>/dev/null || true

FINDINGS_FILE="$FINDINGS_FILE" CORPUS="$CORPUS" python3 - <<'PY'
import json, os, sys, glob

_raw = open(os.environ["FINDINGS_FILE"], encoding="utf-8").read().strip()
findings = json.loads(_raw) if _raw else []

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

# Sidecar-expectations mode: <fixture>.expected.json -> {ruleId: exact count on
# that file}. For fixtures (e.g. JSON config) that can't hold inline tags.
def counts_for(name):
    c = {}
    for (n, s, e, rid) in spans:
        if n == name:
            c[rid] = c.get(rid, 0) + 1
    return c

for exp_path in sorted(glob.glob(os.path.join(os.environ["CORPUS"], "*.expected.json"))):
    fixture = os.path.basename(exp_path)[: -len(".expected.json")]
    expected = json.load(open(exp_path))
    actual = counts_for(fixture)
    for rid, want in expected.items():
        checked += 1
        got = actual.get(rid, 0)
        if got != want:
            fails.append(f"  {fixture}  expected {want}x {rid}, got {got}")
    # also flag unexpected findings of config-rule ids not listed
    for rid, got in actual.items():
        if rid not in expected:
            checked += 1
            fails.append(f"  {fixture}  unexpected {got}x {rid} (not in .expected.json)")

for path in sorted(glob.glob(os.path.join(os.environ["CORPUS"], "*"))):
    name = os.path.basename(path)
    if name.endswith(".expected.json") or os.path.isdir(path):
        continue
    for i, text in enumerate(open(path, encoding="utf-8", errors="ignore"), start=1):
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
print("all precision expectations met")
PY
