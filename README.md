<p align="center">
  <img src="assets/hero.png" alt="agent-security-review — catch insecure agent architecture" width="640">
</p>

<h1 align="center">agent-security-review</h1>

<p align="center">
  <a href="https://ast-grep.github.io/">ast-grep</a> rules that catch insecure patterns in AI-agent code — before they ship.<br>
  <strong><!-- rules:count -->45 rules · 8 components<!-- /rules:count --> · Python &amp; TypeScript · vendor-neutral</strong>
</p>

<p align="center">
  <a href="https://github.com/raxITlabs/agent-security-review/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/raxITlabs/agent-security-review/ci.yml?branch=main&style=flat-square&labelColor=000&label=CI" alt="CI"></a>
  <img src="https://img.shields.io/badge/Claude_Code-plugin-000?style=flat-square&logo=claude&logoColor=white" alt="Claude Code plugin">
  <a href="https://ast-grep.github.io/"><img src="https://img.shields.io/badge/powered_by-ast--grep-000?style=flat-square" alt="powered by ast-grep"></a>
  <!-- rules:badge --><a href="docs/RULES.md"><img src="https://img.shields.io/badge/rules-45-000?style=flat-square&labelColor=000" alt="45 rules"></a><!-- /rules:badge -->
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-000?style=flat-square" alt="MIT license"></a>
</p>

---

## What it catches

| Component | Catches |
|---|---|
| **agent** | unbounded loops, denial-of-wallet, God-Agent sprawl, Rule-of-Two violations |
| **identity** | hardcoded credentials, plaintext DB connections, ambient identity / Confused Deputy |
| **control-flow** | LLM output reaching sinks or control flow, secrets in logs, ungated tool dispatch |
| **mcp** | tool poisoning, prompt injection in tool descriptions, SSRF, missing allowlists |
| **memory** | shared-store poisoning, tainted-read exfiltration, unauthorized writes |
| **skills** | lethal-trifecta tool combos, permission bypass, missing descriptions |
| **gateway** | unauthenticated endpoints, gateway bypass, missing policy engine |

→ **[Full rule catalog](docs/RULES.md)**

## Quick start

```bash
brew install ast-grep                              # one-time
ast-grep scan --config sgconfig.yml /path/to/code  # scan a directory
ast-grep scan --config sgconfig.yml --json .       # JSON output
```

Run against the bundled test corpus: `./scripts/run-fixtures.sh`

## Use it in Claude Code

Install the scanner as a Claude Code skill, then just ask *"security-review my agent code"* — Claude fetches the latest rules, runs the scan, and reports findings with fixes.

**As a plugin** (recommended):

```
/plugin marketplace add raxITlabs/agent-security-review
/plugin install agent-security@raxitlabs
```

**Via [skills.sh](https://skills.sh)** (works across Claude Code, Cursor, Copilot, and 20+ agents):

```bash
npx skills add raxITlabs/agent-security-review
```

**Or one-line install** (standalone skill):

```bash
curl -fsSL https://raw.githubusercontent.com/raxITlabs/agent-security-review/main/install.sh | bash
```

All routes pull the latest rules from this repo at scan time (with an offline fallback) and need [ast-grep](https://ast-grep.github.io/) (`brew install ast-grep`). Skill source: [`skills/agent-security-review/`](skills/agent-security-review/).

## Docs

- **[Rule catalog](docs/RULES.md)** — every rule, its severity, and what it flags
- **[Frameworks](docs/FRAMEWORKS.md)** — Scope / Sign / Stop, MAESTRO 7-layer, and source references
- **[Contributing](docs/CONTRIBUTING.md)** — repo layout, rule schema, how to add a rule
- **[Release flow](docs/RELEASE.md)** — how merged rules reach the scanners

## License

[MIT](LICENSE) © raxIT Labs. We run these rules in production and welcome contributions — see **[Contributing](docs/CONTRIBUTING.md)**.
