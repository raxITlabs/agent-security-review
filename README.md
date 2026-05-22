<p align="center">
  <img src="assets/hero.png" alt="agent-code-scanner-rules — scan agent code, flag insecure patterns" width="640">
</p>

<h1 align="center">agent-code-scanner-rules</h1>

<p align="center">
  <a href="https://ast-grep.github.io/">ast-grep</a> rules that catch insecure patterns in AI-agent code — before they ship.<br>
  <strong>39 rules · 7 components · Python &amp; TypeScript · vendor-neutral</strong>
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

→ **[Full catalog of all 39 rules](docs/RULES.md)**

## Quick start

```bash
brew install ast-grep                              # one-time
ast-grep scan --config sgconfig.yml /path/to/code  # scan a directory
ast-grep scan --config sgconfig.yml --json .       # JSON output
```

Run against the bundled test corpus: `./scripts/run-fixtures.sh`

## Docs

- **[Rule catalog](docs/RULES.md)** — all 39 rules, severity, and what each one flags
- **[Frameworks](docs/FRAMEWORKS.md)** — Scope / Sign / Stop, MAESTRO 7-layer, and source references
- **[Contributing](docs/CONTRIBUTING.md)** — repo layout, rule schema, how to add a rule
- **[Release flow](docs/RELEASE.md)** — how merged rules reach the scanners

## License

Proprietary — internal raxIT use. Rules can be redistributed under raxIT scanner output license.
