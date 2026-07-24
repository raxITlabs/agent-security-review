# Precision fixtures for the Google ADK rules.
#   scope.google-adk-loop-without-max-iterations  (detector, warning)
#   scope.pos.adk-max-iterations-present           (positive evidence, info)
#   scope.google-adk-unsafe-code-executor          (detector, error)
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor, VertexAiCodeExecutor

worker = LlmAgent(name="worker", instruction="do the thing")

# LoopAgent without max_iterations -> unbounded refinement loop.
loop_unbounded = LoopAgent(name="refine", sub_agents=[worker])  # EXPECT_MATCH:scope.google-adk-loop-without-max-iterations

# LoopAgent with a safety limit -> detector must NOT fire, positive MUST fire.
loop_bounded = LoopAgent(name="refine", sub_agents=[worker], max_iterations=5)  # EXPECT_NONE:scope.google-adk-loop-without-max-iterations
loop_bounded_pos = LoopAgent(name="refine2", sub_agents=[worker], max_iterations=5)  # EXPECT_MATCH:scope.pos.adk-max-iterations-present
loop_unbounded_pos = LoopAgent(name="refine3", sub_agents=[worker])  # EXPECT_NONE:scope.pos.adk-max-iterations-present

# A plain LlmAgent is a single reasoning agent, not a loop construct.
single = LlmAgent(name="reasoner", instruction="answer")  # EXPECT_NONE:scope.google-adk-loop-without-max-iterations

# Unsafe local code executor runs model-generated code in-process.
unsafe = UnsafeLocalCodeExecutor()  # EXPECT_MATCH:scope.google-adk-unsafe-code-executor

# A sandboxed executor must NOT fire.
sandboxed = VertexAiCodeExecutor()  # EXPECT_NONE:scope.google-adk-unsafe-code-executor
