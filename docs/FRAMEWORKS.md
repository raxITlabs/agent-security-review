# Frameworks

Every rule is organized around two complementary frameworks: one for the *kind* of architectural failure it detects, one for the *layer* of the agent stack it covers.

## Scope / Sign / Stop

Architectural shifts from the "Kill the God Agent" talk. Each rule ID carries its shift as a prefix (`scope.*`, `sign.*`, `stop.*`).

- **Scope** — limit blast radius. Bound what an agent and its components can reach: capped loops, no God Agent, validated inputs, namespaced memory, narrow skill tool sets.
- **Sign** — establish identity. Every action carries an authenticated principal — no hardcoded secrets, no ambient identity, no Confused Deputy, auth on every gateway and A2A hop.
- **Stop** — gate dangerous flows. A reference monitor sits between untrusted output and dangerous sinks: no LLM output straight into control flow or SQL, no ungated dispatch, no secrets in logs.

## MAESTRO 7-layer

The [CSA Agentic AI Threat Modeling Framework](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) — what layer of the agent stack (L1–L7) each rule covers. Rules that map cleanly to a layer tag it as `maestro_layer` in their metadata.

## Grounding

The pack draws on published thinking from: Meta's Rule of Two, Simon Willison's Lethal Trifecta, DeepMind's CaMeL, AWS Cedar/AgentCore, Microsoft's "When prompts become shells", Tim Kellogg's MCP Colors, and the CSA MAESTRO framework.

## References

| Framework | URL |
|---|---|
| Meta Agents Rule of Two | https://ai.meta.com/blog/practical-ai-agent-security/ |
| Simon Willison — Lethal Trifecta | https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ |
| DeepMind CaMeL | https://arxiv.org/abs/2503.18813 |
| CSA MAESTRO 7-layer Framework | https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro |
| Securing Agentic AI (paper applying MAESTRO) | https://arxiv.org/abs/2508.10043 |
| AWS Cedar / AgentCore | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-common-patterns.html |
| Microsoft — When prompts become shells | https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/ |
| Tim Kellogg — MCP Colors | https://timkellogg.me/blog/2025/11/03/colors |
