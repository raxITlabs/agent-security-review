# Precision fixtures for the DSPy rules.
#   scope.dspy-code-execution   (detector, warning)
#   scope.dspy-react-without-max-iters       (ReAct max_iters branch)
import dspy
from dspy import ProgramOfThought, ReAct


def get_weather(city: str) -> str:
    return "sunny"


# Code-execution primitives.
pot = dspy.ProgramOfThought("question -> answer")  # EXPECT_MATCH:scope.dspy-code-execution
interp = dspy.PythonInterpreter()  # EXPECT_MATCH:scope.dspy-code-execution
pot_bare = ProgramOfThought("question -> answer")  # EXPECT_MATCH:scope.dspy-code-execution

# ChainOfThought is not a code-execution primitive.
cot = dspy.ChainOfThought("question -> answer")  # EXPECT_NONE:scope.dspy-code-execution

# ReAct without max_iters relies on the default of 20 model round-trips.
react_unbounded = dspy.ReAct("question -> answer", tools=[get_weather])  # EXPECT_MATCH:scope.dspy-react-without-max-iters
react_bare = ReAct("question -> answer", tools=[get_weather])  # EXPECT_MATCH:scope.dspy-react-without-max-iters
react_bounded = dspy.ReAct("question -> answer", tools=[get_weather], max_iters=6)  # EXPECT_NONE:scope.dspy-react-without-max-iters
