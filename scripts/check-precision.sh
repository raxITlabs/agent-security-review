#!/usr/bin/env bash
# Precision regression check for the heuristic rules that were prone to false
# positives (credentials, module-scope env secrets, tool dispatch, RAG).
#
# Unlike run-fixtures.sh (which clones whole repos and compares per-rule totals),
# this asserts behaviour line-by-line on a small hand-written corpus: every line
# tagged `EXPECT_MATCH` must produce a finding, every `EXPECT_NONE` must not.
# That pins the exact true-positive / false-positive boundary, so a future rule
# edit that re-broadens a pattern fails CI here.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORPUS="$REPO_ROOT/fixtures/precision"
SGCONFIG="$REPO_ROOT/sgconfig.yml"

command -v ast-grep >/dev/null 2>&1 || { echo "ERROR: ast-grep not installed"; exit 1; }

findings_json="$(ast-grep scan --json --config "$SGCONFIG" "$CORPUS" 2>/dev/null || true)"

FINDINGS_JSON="$findings_json" CORPUS="$CORPUS" python3 - <<'PY'
import json, os, re, sys, glob

findings = json.loads(os.environ["FINDINGS_JSON"] or "[]")
hit = set()  # (basename, line) that produced at least one finding
for f in findings:
    name = os.path.basename(f.get("file", ""))
    line = (f.get("range") or {}).get("start", {}).get("line")
    if line is not None:
        hit.add((name, line + 1))  # ast-grep lines are 0-based

fails = []
checked = 0
for path in sorted(glob.glob(os.path.join(os.environ["CORPUS"], "*"))):
    name = os.path.basename(path)
    for i, text in enumerate(open(path, encoding="utf-8"), start=1):
        # An assertion is a trailing marker comment (e.g. `... # EXPECT_MATCH`),
        # not prose. Match only when the marker is the last token on the line, so
        # the file's own header comments documenting the convention don't count.
        stripped = text.rstrip()
        want_match = stripped.endswith("EXPECT_MATCH")
        want_none = stripped.endswith("EXPECT_NONE")
        if not (want_match or want_none):
            continue
        checked += 1
        got = (name, i) in hit
        if want_match and not got:
            fails.append(f"  {name}:{i}  EXPECT_MATCH but no finding  -> {text.strip()}")
        if want_none and got:
            fails.append(f"  {name}:{i}  EXPECT_NONE but matched (false positive)  -> {text.strip()}")

print(f"precision corpus: {checked} tagged lines checked, {len(fails)} failure(s)")
if fails:
    print("\n".join(fails))
    sys.exit(1)
print("✓ all precision expectations met")
PY
