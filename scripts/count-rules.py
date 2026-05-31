#!/usr/bin/env python3
"""Single source of truth for "how many rules are in the pack".

The count is derived ONLY from the files under ``rules/`` — there is no number to
hand-edit anywhere. README.md and docs/RULES.md carry marker pairs that this
script fills in:

    <!-- rules:count -->N rules · M components<!-- /rules:count -->
    <!-- rules:breakdown -->...a per-component table...<!-- /rules:breakdown -->

Usage:
    python scripts/count-rules.py            # rewrite the marked regions in place
    python scripts/count-rules.py --check    # verify they're current; exit 1 if stale

CI runs ``--check`` on every PR, so adding a rule without refreshing the counts
fails fast instead of silently drifting (which is how we ended up with three
different numbers — 29, 39, and reality — in the first place).

No third-party deps, so it runs in CI without a pip install. Shift is read from
the rule ``id:`` prefix (``scope.`` / ``sign.`` / ``stop.``); component is the
rule's parent directory.
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / "rules"
TARGETS = ["README.md", "docs/RULES.md"]
SHIFTS = ("scope", "sign", "stop")


def collect():
    """Return (total, {component: count}, {shift: count}) from the rule files."""
    files = sorted(RULES_DIR.rglob("*.yml"))
    by_component: dict[str, int] = {}
    by_shift = {s: 0 for s in SHIFTS}
    for f in files:
        by_component[f.parent.name] = by_component.get(f.parent.name, 0) + 1
        for line in f.read_text(errors="ignore").splitlines():
            if line.startswith("id:"):
                prefix = line.split(":", 1)[1].strip().split(".", 1)[0]
                if prefix in by_shift:
                    by_shift[prefix] += 1
                break
    return len(files), by_component, by_shift


def render_count(total, by_component):
    return f"{total} rules · {len(by_component)} components"


def render_badge(total, by_component):
    # Static shields.io badge — the number is baked in by this script (no live
    # endpoint to 404), so it stays correct the same way the text counts do.
    url = (f"https://img.shields.io/badge/rules-{total}-000"
           f"?style=flat-square&labelColor=000")
    return f'<a href="docs/RULES.md"><img src="{url}" alt="{total} rules"></a>'


def render_breakdown(total, by_component, by_shift):
    rows = ["| Component | Rules |", "|---|---|"]
    rows += [f"| `{c}` | {by_component[c]} |" for c in sorted(by_component)]
    rows.append(f"| **Total** | **{total}** |")
    shift_line = " · ".join(f"{s}: {by_shift[s]}" for s in SHIFTS)
    return "\n".join(rows) + f"\n\nBy architectural shift — {shift_line}."


def replace_region(text, key, payload):
    open_m, close_m = f"<!-- rules:{key} -->", f"<!-- /rules:{key} -->"
    pattern = re.compile(re.escape(open_m) + r".*?" + re.escape(close_m), re.DOTALL)
    return pattern.subn(f"{open_m}{payload}{close_m}", text)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="verify the marked regions are current; exit 1 if stale")
    args = ap.parse_args()

    total, by_component, by_shift = collect()
    payloads = {
        "count": render_count(total, by_component),
        "badge": render_badge(total, by_component),
        "breakdown": "\n" + render_breakdown(total, by_component, by_shift) + "\n",
    }

    stale = []
    for rel in TARGETS:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = path.read_text()
        new = text
        for key, payload in payloads.items():
            new, _ = replace_region(new, key, payload)
        if new != text:
            (stale.append(rel) if args.check else (path.write_text(new), print(f"updated {rel}")))

    print(f"rules: {total}  components: {len(by_component)}  "
          f"({', '.join(f'{k}={v}' for k, v in sorted(by_component.items()))})")

    if args.check and stale:
        print(f"\nSTALE counts in: {', '.join(stale)}\n"
              f"Run: python scripts/count-rules.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
