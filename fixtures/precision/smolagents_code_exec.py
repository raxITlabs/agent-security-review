# Precision fixtures for the smolagents code-execution rules.
#   scope.smolagents-code-agent-unsandboxed  (detector, error)
#   scope.pos.smolagents-code-agent-sandboxed        (positive evidence, info)
#   scope.smolagents-unsafe-authorized-imports   (detector, warning)
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel()

# Default executor is local -> runs generated code on the host.
bad_default = CodeAgent(tools=[], model=model)  # EXPECT_MATCH:scope.smolagents-code-agent-unsandboxed
bad_local = CodeAgent(tools=[], model=model, executor_type="local")  # EXPECT_MATCH:scope.smolagents-code-agent-unsandboxed

# Sandboxed executor -> detector must NOT fire.
ok_e2b = CodeAgent(tools=[], model=model, executor_type="e2b")  # EXPECT_NONE:scope.smolagents-code-agent-unsandboxed

# Positive-evidence rule fires only when a sandbox executor is set.
pos_docker = CodeAgent(tools=[], model=model, executor_type="docker")  # EXPECT_MATCH:scope.pos.smolagents-code-agent-sandboxed
pos_none = CodeAgent(tools=[], model=model)  # EXPECT_NONE:scope.pos.smolagents-code-agent-sandboxed

# Over-broad authorized imports.
wild = CodeAgent(tools=[], model=model, executor_type="e2b", additional_authorized_imports=["*"])  # EXPECT_MATCH:scope.smolagents-unsafe-authorized-imports
host_mod = CodeAgent(tools=[], model=model, additional_authorized_imports=["os", "numpy"])  # EXPECT_MATCH:scope.smolagents-unsafe-authorized-imports
safe_imports = CodeAgent(tools=[], model=model, executor_type="e2b", additional_authorized_imports=["numpy", "pandas"])  # EXPECT_NONE:scope.smolagents-unsafe-authorized-imports
