---
name: agent-security-review
description: Scan AI-agent, LLM, MCP-server, or tool-calling code for security vulnerabilities using the raxIT agent-security-review pack (ast-grep), then triage the findings with a concrete fix for each. Use this whenever the user wants to security-review, audit, harden, or "check before shipping" any agentic code — for example "review my agent for security issues", "is my MCP server safe", "audit my LangChain / OpenAI Agents / CrewAI / LlamaIndex tool code", "scan my agent for prompt injection", or "find vulnerabilities in my tool definitions". It catches hardcoded credentials, prompt-injection sinks, unbounded loops / denial-of-wallet, ungated tool dispatch, MCP tool poisoning and SSRF, memory poisoning and data exfiltration, lethal-trifecta skill permissions, and missing gateway auth. The pack is agent-specific: if the target turns out NOT to be agentic code, this skill says so plainly and scopes out instead of inventing issues. Rules are pulled live from GitHub so the checks stay current. Reach for this even when the user doesn't say "ast-grep" or "scan" but clearly wants their agent or LLM code reviewed for security.
argument-hint: "[path-to-code]"
---

# Agent security review

Run the raxIT **agent-security-review** pack (an [ast-grep](https://ast-grep.github.io/) ruleset) against AI-agent / LLM / MCP code, then turn the matches into a prioritized report with the architectural fix for each finding.

This deliberately pairs two things: a **deterministic scanner** (fast, reproducible, consistent) and **your own review** (catches what patterns can't). Treat the scanner as a **floor, not a ceiling** — ast-grep matches fixed patterns, so it reliably finds the shapes it knows but silently misses variants and whole classes it has no rule for. A report that only repeats scanner output will quietly miss real, obvious vulnerabilities. Your job is to run the scanner *and* read the code, then produce a report the user can trust.

One thing this pack is **not**: a general-purpose SAST tool. Every rule targets an *agent* failure mode — prompt injection, tool dispatch, agent loops, MCP, memory, agent identity. That focus is the point, and it means the most important judgment call you make is **whether the target is even an agentic codebase** (see step 3). On a plain library or a model-training repo, a clean scan is the *correct* answer, not a gap to paper over.

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

Resolve the target path first: if the skill was invoked as `/agent-security-review <path>`, the path is `$ARGUMENTS`. If `$ARGUMENTS` is empty, use the path the user named, or the current directory (`.`) as the default.

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path-to-code> > findings.json
```

`scan.sh` fetches the latest rules from GitHub (`main`), caches them locally, and falls back to the bundled copy in `references/rules-vendored/` if GitHub is unreachable. It writes ast-grep's JSON findings to stdout.

For a **reproducible** scan (CI, audits), pin a commit or tag so the result can't drift:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path-to-code> --pin <sha-or-tag> > findings.json
```

### 3. Decide what kind of codebase this is — *before* you write findings

This step exists because the pack is agent-specific. Forcing an agent-security narrative onto code that has no agents produces a confident, useless report — the worst outcome. So classify the target first, then scope the review to match. Use what you can see: dependencies (`pyproject.toml` / `requirements.txt` / `package.json`), imports, and the actual entry points — not the repo's marketing.

Sort the target into one of three buckets:

- **Agentic** — it builds or runs an agent / LLM app / MCP server / tool-calling system. Signals: an agent framework (LangChain/LangGraph, OpenAI Agents SDK, CrewAI, LlamaIndex, AutoGen/AG2, Anthropic SDK with tools), an MCP server/client, a tool/function dispatch loop, retrieval + generation, or prompts assembled from untrusted input. → **Full review.** Every component applies; do the scan *and* the manual pass.

- **AI-adjacent, not an agent** — it touches LLMs but isn't an agent: a model-training / fine-tuning library, an inference kernel, an eval harness, a thin SDK wrapper, a prompt-template collection. → **Scoped review.** State plainly that the agent ruleset mostly doesn't apply and *why*. Report only what genuinely transfers (hardcoded secrets, `eval`/`exec` on external input, SSRF, unsafe deserialization of model files are universal). Do **not** manufacture agent-architecture findings (no "missing gateway auth" on a library that has no gateway).

- **Not AI at all** — a plain library, CLI, web app, or data pipeline with no LLM/agent surface. → **Out of scope.** Say so in two sentences, note that the scan found nothing agent-specific (it won't have), and suggest a general SAST tool (Semgrep, CodeQL, Bandit) instead. Stop. A short honest "this isn't what the pack is for" beats a padded report every time.

When you're genuinely unsure, say which bucket you picked and why, and let the user redirect. Misclassifying *down* (treating an agent as a library) is worse than asking.

### 4. Turn findings into a report

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/report.py findings.json          # or:  ... | uv run ${CLAUDE_SKILL_DIR}/scripts/report.py -
```

`report.py` groups the scanner's matches by severity and surfaces the "Architectural fix:" each rule carries. That's the deterministic floor. Now make the report worth trusting:

- **Read the code yourself for what the rules miss** — *but only for agentic and AI-adjacent targets.* This is the highest-value step for real agent code: the scanner found the patterns it knows; you should independently check the classes pattern rules under-cover. Look for: hardcoded secrets in any form, prompt-injection text planted in tool/skill descriptions, LLM/tool output reaching a dangerous sink (`eval`, SQL, shell, `unsafe`/raw-HTML rendering), SSRF and path traversal, secrets written to logs, unbounded agent loops, and tool dispatch with no authorization. If you find one the scanner didn't, include it and label it **manual**.
- **Scope the manual pass to the attack surface.** On a large repo you cannot (and should not) read everything. Read the entry points and the trust boundaries — where external/LLM/tool input enters and where it reaches a sink — and say what you did *not* cover. An honest, bounded pass beats an unbounded one that runs out of budget halfway.
- **Judge and dedupe.** ast-grep over-flags too. If a finding is a false positive in context, drop it and say why in one line. A padded report is worse than a short honest one. The rules lean on name/shape heuristics, so a few false-positive classes recur — discount them unless the surrounding code proves otherwise:
  - **Test, eval, and example code** (`tests/`, `evals/`, `examples/`, `conftest.py`): an env-var read or ungated call in a test isn't shipped attack surface. Note it, don't rank it as a real finding.
  - **Non-secret config that looks secret-shaped** — e.g. `CORS_ALLOW_ORIGINS`, a release tag, a feature flag flagged as a "module-scope secret." Check the *name and value*, not just the `X = os.environ[...]` shape.
  - **Placeholder/empty literals** — `api_key = ""` or a bare prefix like `"hf_"` is not a hardcoded credential.
  - **Framework-label mismatch** — a rule message may name the wrong SDK (e.g. says OpenAI Agents `@function_tool` when the code is LangChain `@tool`). The *risk class* is usually still right; correct the attribution and move on.
- **Mind the exit codes.** `scan.sh` and `report.py` both exit non-zero when an error-severity finding exists — that's the gate working, not a crash. Don't report a successful scan as a tool failure.
- **Stay balanced.** Call out the controls the code gets *right* — it tells the user the report read the code, not just the scanner output.

#### Required report structure

Use this exact skeleton so every report is consistent and skimmable. Lead with the verdict and the applicability call; put the table before the prose.

```
# Agent Security Review — <target>

**Applicability:** <Agent ✓ (full ruleset) | AI-adjacent (scoped) | Not an agent app (out of scope)> — <one clause why>
**Verdict:** <one line — e.g. "1 high, 3 medium; fix H1 before deploy" or "No agent-security issues; not an agentic codebase">
**Scope of this review:** ast-grep (<N> rules) — <X> matches · manual pass: <files/areas read, or "n/a — out of scope">

<!-- If "Not an agent app": write 2–3 sentences on why the pack doesn't apply + what (if anything) universal was checked, then STOP. No findings table of invented issues. -->

## Findings
| # | Sev | Rule / class | Location | Source | Confidence |
|---|-----|--------------|----------|--------|------------|
| H1 | 🔴 high | prompt-injection-sink | report.py:74 | manual | high |
| M1 | 🟠 med | sign.mcp-tool-without-allowlist | agents.py:148 | scanner | med |

Legend — Severity: 🔴 high/error · 🟠 medium/warning · 🟡 low/info. Source: scanner | manual.

## Details
<one block per finding, ordered by severity>
### H1 · prompt-injection-sink · report.py:74
- **What:** the actual data flow in *this* code (e.g. scraped page → LLM synthesis → `st.markdown(unsafe_allow_html=True)`)
- **Why it matters:** concrete impact tied to their threat model
- **Fix:** the architectural change, not just a patch
- **Coverage note:** scanner matched | scanner missed (pack blind spot worth a rule)

## What's solid
- controls the code gets right (keep the report honest and balanced)

## Coverage & gaps
- what the scan covered, what the manual pass covered, what was **not** looked at, and known pack blind spots

## Priority actions
1. highest-impact fix first …
```

For an out-of-scope target the report is just the header block plus the short explanation — that *is* a complete, correct report.

### CI / gate mode

To fail a pipeline only on real problems:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scan.sh <path> > findings.json
uv run ${CLAUDE_SKILL_DIR}/scripts/report.py findings.json --gate    # exits 1 if any error-severity finding
```

## Why the rules are pulled from GitHub

The pack grows — new agent frameworks, new attack classes. Pulling `main` on each run means every scan uses the newest checks without re-installing the skill, and the repo stays the single source of truth. The local cache plus the bundled fallback keep it working offline and on the network-less Claude API; `--pin` keeps a given scan reproducible when freshness matters less than determinism. ast-grep rules are declarative YAML (data, not executable code), so fetching them at runtime is low-risk.

## What it catches

Across seven components — **agent** (unbounded loops, denial-of-wallet, God-Agent sprawl, Rule-of-Two), **identity** (hardcoded credentials, plaintext DB, ambient identity / Confused Deputy), **control-flow** (LLM output to sinks/control flow, secrets in logs, ungated tool dispatch), **mcp** (tool poisoning, prompt injection in tool descriptions, SSRF, missing allowlists), **memory** (shared-store poisoning, tainted-read exfiltration, unauthorized writes), **skills** (lethal-trifecta tool combos, permission bypass, missing descriptions), and **gateway** (unauthenticated endpoints, gateway bypass, missing policy engine). Python and TypeScript today; the pack is expanding.

The exact, current rule count lives in the catalog — don't quote a hardcoded number, link the catalog: https://github.com/raxITlabs/agent-security-review/blob/main/docs/RULES.md

## Notes

- A clean scan is a real result. On agentic code, report "no scanner findings" and still do the manual pass. On non-agent code, "no findings" is the *expected* answer — don't invent issues to fill the page.
- `report.py` tolerates both the pretty array and the streaming (`--json=stream`) shapes, and reads from a file or stdin.
- The rule message is the explanation and `metadata` (with `--include-metadata`, which `scan.sh` sets) carries the component and architectural shift — no external lookup needed.
