# Precision fixtures for the Pydantic AI usage-limit rules.
#   scope.pydantic-ai-run-without-usage-limits  (detector, warning)
#   scope.pos.pydantic-ai-usage-limits-present     (positive evidence, info)
import subprocess

from pydantic_ai import Agent, UsageLimits

agent = Agent("openai:gpt-4o")

# No usage_limits -> unbounded model-turn / token budget.
unbounded = agent.run_sync("hello")  # EXPECT_MATCH:scope.pydantic-ai-run-without-usage-limits


async def stream_it():
    async with agent.run_stream("hello") as stream:  # EXPECT_MATCH:scope.pydantic-ai-run-without-usage-limits
        return stream

# With usage_limits -> detector must NOT fire, positive MUST fire.
bounded = agent.run_sync("hello", usage_limits=UsageLimits(request_limit=3))  # EXPECT_NONE:scope.pydantic-ai-run-without-usage-limits
bounded_pos = agent.run_sync("hi", usage_limits=UsageLimits(request_limit=3))  # EXPECT_MATCH:scope.pos.pydantic-ai-usage-limits-present

# OpenAI Agents SDK Runner.run_sync must stay owned by the runner rules, not this one.
res = Runner.run_sync(agent, "hello")  # EXPECT_NONE:scope.pydantic-ai-run-without-usage-limits

# subprocess.run must never be mistaken for an agent run.
proc = subprocess.run(["ls"])  # EXPECT_NONE:scope.pydantic-ai-run-without-usage-limits
