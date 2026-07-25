# Precision fixtures for the AutoGen / AG2 code-executor rule.
#   scope.autogen-local-code-executor  (detector, error)
from pathlib import Path

from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

work_dir = Path("coding")

# Local executor runs model-generated code on the host.
local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)  # EXPECT_MATCH:scope.autogen-local-code-executor

# Docker executor is sandboxed -> must NOT fire.
docker_executor = DockerCommandLineCodeExecutor(work_dir=work_dir)  # EXPECT_NONE:scope.autogen-local-code-executor
