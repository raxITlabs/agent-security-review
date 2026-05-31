# Precision fixture for the 3 over-broad "blanket" rules that produced ~50% of all
# findings in the cross-framework audit, mostly as false positives.
# Tags are rule-scoped: EXPECT_MATCH:rule-id / EXPECT_NONE:rule-id.

import os, requests, httpx, boto3
from agents import function_tool
from langchain_core.tools import tool

# ───────────────────────── policy-gate (scoped to side-effecting tools) ─────────────────────────
# A tool that actually does something dangerous (network / state change) with no
# authz gate is the real ungated-dispatch risk → SHOULD fire.
@function_tool
def transfer_funds(to: str, amount: int) -> str:
    return requests.post(f"https://bank/api/pay", json={"to": to, "amt": amount}).text  # EXPECT_MATCH:stop.openai-agents-tool-without-policy-gate

# A pure read-only / compute tool with no side effect is NOT the lethal pattern —
# flagging every such tool as an error was the dominant false positive.
@function_tool
def add(a: int, b: int) -> int:
    return a + b                                          # EXPECT_NONE:stop.openai-agents-tool-without-policy-gate

# A side-effecting tool that DOES gate on a principal/authz is mitigated → no fire.
@tool
def delete_record(record_id: str, ctx) -> str:
    authorize(ctx, "delete", record_id)
    return db.execute("DELETE FROM t WHERE id=%s", record_id)  # EXPECT_NONE:stop.openai-agents-tool-without-policy-gate

# Identity threaded via framework context (RunContextWrapper) is the idiomatic
# OpenAI-Agents auth path — must not be a false positive.
@function_tool
def send_report(wrapper: RunContextWrapper, body: str) -> str:
    return requests.post("https://api/report", json={"b": body}).text  # EXPECT_NONE:stop.openai-agents-tool-without-policy-gate

# ───────────────────────── a2a-communication (must be agent-bound) ─────────────────────────
# Real A2A: posting to an agent/run/task endpoint with no auth → SHOULD fire.
def call_peer_agent(state):
    return requests.post("https://peer/agent/run", json={"task": state})  # EXPECT_MATCH:sign.a2a-communication-without-auth

# Generic telemetry / webhook POST is NOT agent impersonation — the old rule
# mislabeled every unauthenticated POST as A2A. Must not fire.
def send_telemetry(metrics):
    return requests.post("https://metrics.example.com/ingest", json=metrics)  # EXPECT_NONE:sign.a2a-communication-without-auth

# Authenticated A2A call is mitigated → no fire.
def call_peer_authed(state, token):
    return requests.post("https://peer/agent/run", json={"task": state}, headers={"Authorization": token})  # EXPECT_NONE:sign.a2a-communication-without-auth
