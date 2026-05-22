---
name: scan-agent-code
description: Scan AI-agent, LLM, MCP-server, or tool-calling code for security vulnerabilities using the raxIT agent-code-scanner-rules pack (ast-grep), then triage the findings with a concrete fix for each. Use this whenever the user wants to security-review, audit, harden, or "check before shipping" any agentic code — for example "review my agent for security issues", "is my MCP server safe", "audit my LangChain / OpenAI Agents / CrewAI / LlamaIndex tool code", "scan my agent for prompt injection", or "find vulnerabilities in my tool definitions". It catches hardcoded credentials, prompt-injection sinks, unbounded loops / denial-of-wallet, ungated tool dispatch, MCP tool poisoning and SSRF, memory poisoning and data exfiltration, lethal-trifecta skill permissions, and missing gateway auth. Rules are pulled live from GitHub so the checks stay current. Reach for this even when the user doesn't say "ast-grep" or "scan" but clearly wants their agent or LLM code reviewed for security.
---

# Scan agent code for security issues

Run the raxIT **agent-code-scanner-rules** pack (an [ast-grep](https://ast-grep.github.io/) ruleset) against AI-agent / LLM / MCP code, then turn the matches into a prioritized report with the architectural fix for each finding.

This deliberately pairs two things: a **deterministic scanner** (fast, reproducible, consistent) and **your own review** (catches what patterns can't). Treat the scanner as a **floor, not a ceiling** — ast-grep matches fixed patterns, so it reliably finds the shapes it knows but silently misses variants and whole classes it has no rule for. A report that only repeats scanner output will quietly miss real, obvious vulnerabilities. Your job is to run the scanner *and* read the code, then produce a report the user can trust.

The rules are **pulled live from GitHub** so the checks stay current as the pack grows, with a bundled copy as an offline fallback. More on why below.

## Workflow

### 1. Make sure ast-grep is installed

The scan needs the `ast-grep` CLI. Check with `command -v ast-grep`. If it's missing, install it with whatever package manager the user has:

- `brew install ast-grep` (macOS)
- `npm i -g @ast-grep/cli`
- `pip install ast-grep-cli` (or `uv tool install ast-grep-cli`)
- `cargo install ast-grep --locked`

Installing software changes the user's machine, so on an unfamiliar or shared setup, say what you're about to run before you run it.

### 2. Scan the target

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path-to-code> > findings.json
```

`scan.sh` fetches the latest rules from `raxITlabs/agent-code-scanner-rules` (`main`), caches them locally, and falls back to the bundled copy in `references/rules-vendored/` if GitHub is unreachable. It writes ast-grep's JSON findings to stdout.

For a **reproducible** scan (CI, audits), pin a commit or tag so the result can't drift:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path-to-code> --pin <sha-or-tag> > findings.json
```

### 3. Turn findings into a report

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/report.py findings.json          # or:  ... | uv run ${CLAUDE_SKILL_DIR}/scripts/report.py -
```

`report.py` groups findings by severity then component and surfaces the "Architectural fix:" each rule already carries. That's the deterministic floor. Now make the report worth trusting:

- **Read the code yourself for what the rules miss.** This is the most important step — the scanner found the patterns it knows, but you should independently check the high-value classes that pattern rules routinely under-cover. At minimum look for: hardcoded secrets in *any* form (the rules only catch some key shapes), prompt-injection text planted in tool/skill descriptions, SQL/command injection, SSRF and path traversal, secrets written to logs, unbounded agent loops, and tool dispatch with no authorization. If you find one the scanner didn't, include it and label it as found by manual review.
- **Note coverage gaps honestly.** When you catch something the scanner missed, say so plainly — it tells the user the pack has a blind spot (useful feedback for the rule authors) and stops the report from implying the scan was exhaustive.
- **Prioritize**: `error` first (these block), then `warning`, then `info`. Lead with whatever is remotely exploitable.
- **Explain in context**: tie each finding to the actual line and why it matters for *their* code, not in the abstract.
- **Judge and dedupe**: ast-grep can also over-flag. If a finding is a false positive in context, say so and why — a padded report is worse than a short honest one.

### CI / gate mode

To fail a pipeline only on real problems:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path> > findings.json
uv run ${CLAUDE_SKILL_DIR}/scripts/report.py findings.json --gate    # exits 1 if any error-severity finding
```

## Why the rules are pulled from GitHub

The pack grows — new agent frameworks, new attack classes. Pulling `main` on each run means every scan uses the newest checks without re-installing the skill, and the repo stays the single source of truth. The local cache plus the bundled fallback keep it working offline and on the network-less Claude API; `--pin` keeps a given scan reproducible when freshness matters less than determinism. ast-grep rules are declarative YAML (data, not executable code), so fetching them at runtime is low-risk.

## What it catches

Hardcoded credentials, plaintext DB connections, ambient identity / Confused Deputy, unbounded agent loops / denial-of-wallet, LLM output reaching dangerous sinks, ungated tool dispatch, secrets in logs, MCP tool poisoning / SSRF, memory poisoning and tainted-read exfiltration, lethal-trifecta skill tool combos, and unauthenticated gateways. Python and TypeScript today; the pack is expanding.

Full catalog: https://github.com/raxITlabs/agent-code-scanner-rules/blob/main/docs/RULES.md

## Notes

- If the scan returns nothing, that's a real result — report "no findings" rather than inventing issues.
- `report.py` tolerates both the pretty array and the streaming (`--json=stream`) shapes, and reads from a file or stdin.
- The rule message is the explanation and `metadata` (with `--include-metadata`, which `scan.sh` sets) carries the component and architectural shift — no external lookup needed.
