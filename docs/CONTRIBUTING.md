# Contributing

## Repo structure

```
rules/
  agent/         General agent architecture rules
  identity/      Auth / capability / Confused Deputy rules (Sign)
  control-flow/  Reference monitor / composition rules (Stop)
  mcp/           MCP-specific patterns
  memory/        Memory architecture rules (Brooks's Dropbox pattern)
  skills/        Claude / Cursor skill rules
  gateway/       Gateway / middleware rules

fixtures/
  manifest.yaml  Test fixture corpus + expected findings per rule

scripts/
  run-fixtures.sh           Clone fixtures, run all rules, compare to expected
  validate-rules.sh         Lint rule YAML
  generate-manifest.py      Produce manifest.json for S3 upload
```

## Add a new rule

1. Pick the right folder (`mcp/`, `memory/`, etc.).
2. Create `rule-name.yml` following the schema below.
3. Add the rule to `fixtures/manifest.yaml` with expected output for at least one fixture.
4. Run `./scripts/run-fixtures.sh` locally — it should pass.
5. Open a PR.

## Rule schema

```yaml
id: <component>.<rule-name>      # e.g., scope.rule-of-two-violation
language: python                  # or javascript, typescript, go
severity: error                   # error | warning | info
message: |-
  What the rule detected. Architectural fix: explain how to address.

metadata:
  shift: scope                    # scope | sign | stop  (Kill the God Agent framework)
  component: agent                # agent | identity | control-flow | mcp | memory | skills | gateway
  maestro_layer: L1               # L1-L7 (CSA MAESTRO framework, optional)
  framework: meta-rule-of-two     # source framework
  references:
    - https://ai.meta.com/blog/practical-ai-agent-security/

rule:
  # ast-grep pattern matcher
  pattern: ...
```

See [Frameworks](FRAMEWORKS.md) for what `shift` and `maestro_layer` mean.

### Positive-evidence rules (`scope.pos.*` / `sign.pos.*`)

Most rules are **detectors** — they fire on a missing or broken control. A few
are **positive-evidence** rules that fire when a recommended control *is* present
(a sandboxed executor, an explicit token/loop budget), so a downstream consumer
can mint deterministic "Verified" from presence rather than inferring safety from
a detector *not* firing. Mark these by putting `pos` after the shift prefix in the
id — `scope.pos.smolagents-code-agent-sandboxed` — mirroring the `artifact.pos.*`
convention the artifact linter already emits, and set `severity: info`. (This is a
proposed convention introduced with the framework-coverage rules; the shift prefix
is unchanged, so `count-rules.py` and `validate-rules.sh` treat them normally.)

## Test corpus

`./scripts/run-fixtures.sh` clones each fixture from `fixtures/manifest.yaml`, runs the full rule pack, and reports per-fixture findings vs expected. Every rule must have at least one fixture with expected output.
