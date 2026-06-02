# How agent-security-review works

This pack scans AI-agent / LLM / MCP code and, for every issue, tells you the
**design change** that removes the whole class of problem — not a one-line patch.

The core idea: most scanners answer *"where is the bug?"* This one answers
*"what about the architecture let this bug exist, and what shift removes it?"*

---

## The thesis: Scope / Sign / Stop

Every rule is tagged with one of three architectural shifts. They are the spine of
the pack.

```
                 an agent gets hijacked / prompt-injected
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                          ▼
   ┌─────────┐               ┌─────────┐                ┌─────────┐
   │  SCOPE  │               │  SIGN   │                │  STOP   │
   └─────────┘               └─────────┘                └─────────┘
   shrink what it            establish WHO              gate what
   CAN do                    is acting                  HAPPENS
   • bound loops             • per-task identity        • monitor before
   • split God-Agents        • no ambient creds           tool dispatch
   • cap tool breadth        • signed A2A calls         • no LLM output
   • attribute RAG data      • authed gateways            into sinks
   • avoid lethal combos     • secrets from a vault     • moderation
```

| Shift | Question it forces | Example fixes |
|-------|--------------------|---------------|
| **Scope** | Can the agent even reach this? | bound the loop, split the God-Agent, namespace memory |
| **Sign**  | Who is acting, with what authority? | per-task credentials, authed endpoint, vaulted secrets |
| **Stop**  | What stops a bad action mid-flight? | reference monitor before dispatch, no raw LLM output to SQL/shell |

Current pack: **46 rules across 8 components** (agent, identity, control-flow, mcp,
memory, skills, gateway, config) — Python & TypeScript. Mapping to the
lethal-trifecta / Meta Rule-of-Two, DeepMind CaMeL, and Cedar reference-monitor
work is in [`FRAMEWORKS.md`](FRAMEWORKS.md).

---

## How a scan runs

The engine is [ast-grep](https://ast-grep.github.io/) — it matches the code's
**syntax tree**, not regex over text. So it sees real structure: a decorated
function, a tool dict, a call with or without a given keyword argument.

```
  your repo
     │
     ▼
  fetch rules ──────────►  live from GitHub main (offline fallback)
     │
     ▼
  scope the scan ───────►  skip tests/ evals/ examples/ by default
     │
     ▼
  ast-grep scan ────────►  match all 46 rules against the syntax tree
     │
     ▼
  + markdown pre-pass ──►  scan-markdown.sh covers .cursorrules / SKILL.md
     │                     (ast-grep has no markdown parser)
     ▼
  report.py ────────────►  group by severity, show the architectural fix,
     │                     print a confidence summary
     ▼
  triaged report
```

A clean scan is the **deterministic floor**. The skill that wraps it also has the
model read the code for what fixed patterns can't see — and first **classify
whether the repo is even an agent**. On a non-agent repo it scopes out instead of
inventing findings.

---

## Worked example: a vulnerable LLM agent

Example repo:
[`damn-vulnerable-llm-agent`](https://github.com/ReversecLabs/damn-vulnerable-llm-agent)
— a LangChain banking agent built intentionally insecure.

```bash
ast-grep scan --config sgconfig.yml --include-metadata --json ./dvla
# → 4 findings: 2 error, 2 warning
```

These are the **actual findings** (real rule output, not illustrative):

### Finding 1 — LLM output reaches a SQL sink  ·  STOP  ·  error

```
transaction_db.py:62
    cursor.execute(f"SELECT * FROM Transactions WHERE userId = '{str(userId)}'")
transaction_db.py:76
    cursor.execute(f"SELECT userId,username FROM Users WHERE userId = {str(user_id)}")
```

**Why:** an agent tool runs an f-string SQL query built from a value the LLM
controls. A prompt-injected model can rewrite the query → data exfiltration.

```
  point-patch scanner says:   "escape this string"        ← fixes one line
  architectural fix (Stop):   "the agent must never reach  ← kills the class
                               a raw SQL sink — use params
                               + a reference monitor at
                               the tool boundary"
```

### Finding 2 — God-Agent tool sprawl  ·  SCOPE  ·  warning

```
tools.py:22   get_current_user_tool      = Tool(name='GetCurrentUser', ...)
tools.py:40   get_recent_transactions... = Tool(name='GetUserTransactions', ...)
```

**Why:** many powerful tools on one agent. The more it can do from one context,
the larger the blast radius when hijacked.

**Architectural fix (Scope):** split into specialized agents, each with a narrow
tool list — so a compromise of one can't reach everything.

---

## The report

`report.py` turns raw matches into a prioritized, honest summary:

```
## Security scan: 4 finding(s) — 2 error · 2 warning

_Confidence: 2 high · 2 medium. Low-confidence findings are heuristic — triage first._

### ERROR (2)
- stop.llm-output-to-dangerous-sink   control-flow/stop
  - transaction_db.py:62  — LLM-driven SQL sink
  - Fix: parameterized queries + reference monitor at the tool boundary

### WARNING (2)
- scope.god-agent-tool-count   agent/scope
  - tools.py:22 — God-Agent tool sprawl
  - Fix: split into specialized agents with narrow tool lists
```

---

## Why precision protects the thesis

Architectural guidance is high-stakes: tell someone to re-architect a false
positive and they learn to ignore you. So the pack guards its own credibility:

| Guardrail | Prevents |
|-----------|----------|
| **Applicability gate** | inventing "missing gateway auth" on a training library with no gateway |
| **Confidence tiers** | a heuristic "maybe" reading like a "must" |
| **Generalized, not repo-shaped** | rules keyed to one repo's literals — they key on portable signals (canonical names, call shapes, sink kinds), validated across LangChain / LangGraph / OpenAI Agents / CrewAI / Bedrock / MCP |
| **Router-aware auth** | flagging centrally-authenticated routes — the gateway rule learned `APIRouter(dependencies=...)` after a scale test on a large agent platform showed ~40% of its hits were that pattern |

---

## Try it

```bash
brew install ast-grep                            # the engine
npx skills add raxITlabs/agent-security-review   # install the skill
# then in Claude Code, just ask:  "security-review my agent"
```

Or run the rules directly:

```bash
ast-grep scan --config sgconfig.yml --json /path/to/agent
```

- Full rule catalog → [`RULES.md`](RULES.md)
- Scope / Sign / Stop + framework mapping → [`FRAMEWORKS.md`](FRAMEWORKS.md)

> Findings above are real output from an ast-grep 0.42.2 scan of
> `damn-vulnerable-llm-agent`, not illustrative examples.
