# Rule catalog

All 39 rules in the pack, grouped by component. Severity is `error` (block), `warning` (review), or `info`. The `scope` / `sign` / `stop` prefix on each rule ID is its architectural shift — see [Frameworks](FRAMEWORKS.md).

Rules ending in `-ts` are TypeScript variants of a Python rule; `openai-agents-*` rules target the OpenAI Agents SDK.

## Agent architecture — `rules/agent/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `scope.agent-without-bounded-loop` | py | warning | Agent loop with no `max_iterations` / `max_turns` bound — unbounded loop / denial-of-wallet |
| `scope.agent-without-bounded-loop-ts` | ts | warning | Agentic LLM call with no `maxSteps` / `maxToolRoundtrips` cap — unbounded tool loops |
| `scope.openai-agents-runner-without-max-turns` | py | warning | `Runner.run()` with no `max_turns` cap — unbounded agentic loop |
| `scope.llm-call-without-timeout` | py | warning | LLM API call with no timeout — denial-of-wallet from runaway requests |
| `scope.llm-call-without-timeout-ts` | ts | warning | LLM call with no `abortSignal` / timeout — denial-of-wallet from runaway requests |
| `scope.openai-agents-runner-without-timeout` | py | warning | `Runner.run()` with no timeout — denial-of-wallet if the model stalls |
| `scope.god-agent-tool-count` | py | warning | Many tool registrations in one place — God Agent pattern |
| `scope.rule-of-two-violation` | py | error | Meta Rule of Two violated — one module has all three risky properties |

## Identity & credentials — `rules/identity/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `sign.hardcoded-credential-literal` | py | error | Hardcoded credential in source — survives prompt injection because it's baked in |
| `sign.hardcoded-credential-literal-ts` | ts | error | Hardcoded credential in source — survives prompt injection |
| `sign.db-connection-without-tls` | py | error | DB connection without TLS — data in transit is plaintext |
| `sign.shared-client-ambient-identity` | py | warning | Client built at module scope — every tool call shares one ambient identity (Confused Deputy) |
| `sign.env-var-secret-at-module-scope` | py | warning | Env-var secret read at module scope, reused across all tool calls — ambient identity |
| `sign.env-var-secret-at-module-scope-ts` | ts | warning | Env-var secret read at module scope, reused across all requests — ambient identity |
| `sign.tool-without-principal-context` | py | warning | Tool lacks a principal/context/auth parameter — can't do Cedar deny-by-default |
| `sign.openai-agents-instructions-from-untrusted-source` | py | warning | `Agent(instructions=...)` built from a call-site value — untrusted text becomes the system prompt |

## Control flow — `rules/control-flow/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `stop.llm-output-to-control-flow` | py | error | LLM output used directly in control flow — CaMeL violation (untrusted data steers the program) |
| `stop.llm-output-to-dangerous-sink` | py | error | LLM-driven f-string SQL execution — injection sink |
| `stop.tool-dispatcher-without-policy-gate` | py | error | Tool dispatcher invokes by name with no policy gate — injected LLM can call any tool |
| `stop.tool-dispatcher-without-policy-gate-ts` | ts | error | Tool `execute()` handler dispatches with no policy / authorization check |
| `stop.openai-agents-tool-without-policy-gate` | py | error | `@function_tool` dispatches with no policy / authorization check |
| `stop.log-output-with-secrets` | py | error | Log / print interpolates a likely secret — logs become an exfiltration vector |
| `stop.llm-provider-missing-moderation` | py | warning | LLM completion with no input/output moderation — no guardrail layer |
| `stop.llm-provider-missing-moderation-ts` | ts | warning | LLM call with no input/output moderation classifier — no guardrail layer |

## MCP — `rules/mcp/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `scope.mcp-server-without-input-validation` | py | error | MCP tool params reach dangerous sinks unvalidated — tool poisoning / RCE |
| `sign.mcp-client-without-server-allowlist` | py | warning | MCP client connects to a variable server URL with no allowlist — trusts arbitrary servers |
| `sign.mcp-tool-without-allowlist` | py | warning | MCP tool lacks URL/path allowlist — SSRF / path traversal |
| `scope.mcp-prompt-injection-in-tool-description` | py | warning | Imperative phrases in a tool description — injection planted in the prompt surface |

## Memory — `rules/memory/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `scope.shared-memory-no-namespace` | py | error | Shared-store write with no per-agent/tenant namespace — Brooks Dropbox poisoning |
| `stop.memory-tainted-read-flows-to-external` | py | error | Memory read flows to an external request — tainted memory may be exfiltrated |
| `sign.memory-write-no-auth-context` | py | warning | Memory write with no authorization check — any tool call can write |
| `scope.rag-without-source-attribution` | py | warning | RAG result fed to the LLM with no source-attribution metadata |

## Skills — `rules/skills/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `sign.skill-bypasses-permission` | py | error | Skill sets `dangerously-skip-permissions` / `bypassPermissions` — disables the deny-by-default gate |
| `scope.skill-with-dangerous-tool-combo` | py | error | Skill grants filesystem + network + shell — Lethal Trifecta candidate |
| `scope.skill-without-description` | py | info | Skill / tool lacks a description — LLM can't reason about when to call it, defaults to over-use |

## Gateway — `rules/gateway/`

| Rule | Lang | Severity | Flags |
|---|---|---|---|
| `sign.a2a-communication-without-auth` | py | error | Agent-to-agent send with no auth header / signature — agent impersonation |
| `sign.gateway-unauthenticated-endpoint` | py | error | Gateway / MCP endpoint with no auth dependency — anyone can invoke tools |
| `stop.direct-tool-bypasses-gateway` | py | error | Tool invoked directly, bypassing the gateway / reference monitor |
| `stop.gateway-without-policy-engine` | py | warning | Gateway endpoint with no policy engine (Cedar / OPA / AWS Verified Permissions) |
