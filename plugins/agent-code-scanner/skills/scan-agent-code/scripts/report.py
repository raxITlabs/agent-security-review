#!/usr/bin/env python3
"""Turn ast-grep scan JSON into a grouped, prioritized security report.

Reads ast-grep `--json` output (a pretty array or `--json=stream` lines) from a
file argument or stdin, groups findings by severity then component, and surfaces
the architectural fix that each rule's message already carries.

With --gate it exits 1 when any error-severity finding is present, so it can act
as a CI gate.
"""
import argparse
import json
import sys
from collections import defaultdict

SEV_ORDER = ["error", "warning", "info", "hint"]


def load(src):
    raw = (sys.stdin.read() if src in (None, "-") else open(src).read()).strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)              # pretty / compact array
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        return [json.loads(line) for line in raw.splitlines() if line.strip()]  # stream


def field(f, *names, default=""):
    for n in names:
        if f.get(n) not in (None, ""):
            return f[n]
    return default


def comp_and_shift(f):
    meta = f.get("metadata") or {}
    rid = field(f, "ruleId", "rule_id")
    shift = meta.get("shift") or (rid.split(".")[0] if "." in rid else "")
    return (meta.get("component") or "other"), shift


def loc(f):
    start = (f.get("range") or {}).get("start") or {}
    return f"{field(f, 'file', default='?')}:{start.get('line', '?')}:{start.get('column', '?')}"


def split_fix(message):
    for marker in ("Architectural fix:", "Fix:"):
        if marker in message:
            detect, fix = message.split(marker, 1)
            return detect.strip(), fix.strip()
    return message.strip(), ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json", nargs="?", default="-", help="ast-grep JSON file, or - for stdin")
    ap.add_argument("--gate", action="store_true", help="exit 1 if any error-severity finding")
    args = ap.parse_args()

    findings = load(args.json)
    counts = defaultdict(int)
    by_sev = defaultdict(lambda: defaultdict(list))
    for f in findings:
        sev = field(f, "severity", default="info").lower()
        comp, _ = comp_and_shift(f)
        by_sev[sev][comp].append(f)
        counts[sev] += 1

    total = sum(counts.values())
    if total == 0:
        print("## Security scan: no findings\n\nNo rules matched. Nothing to fix.")
        return 0

    summary = " · ".join(f"{counts[s]} {s}" for s in SEV_ORDER if counts[s])
    print(f"## Security scan: {total} finding(s) — {summary}\n")

    for sev in SEV_ORDER:
        if sev not in by_sev:
            continue
        print(f"### {sev.upper()} ({counts[sev]})\n")
        for comp in sorted(by_sev[sev]):
            for f in by_sev[sev][comp]:
                rid = field(f, "ruleId", "rule_id", default="(rule)")
                comp_, shift = comp_and_shift(f)
                detect, fix = split_fix(field(f, "message"))
                tag = "/".join(x for x in (comp_, shift) if x and x != "other")
                print(f"- **{rid}**" + (f"  `{tag}`" if tag else ""))
                print(f"  - {loc(f)}")
                if detect:
                    print(f"  - {detect}")
                if fix:
                    print(f"  - Fix: {fix}")
        print()

    if args.gate:
        if counts["error"]:
            print(f"Gate: FAILED — {counts['error']} error-severity finding(s).")
            return 1
        print("Gate: passed — no error-severity findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
