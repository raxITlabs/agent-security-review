# Precision fixture for scope.tool-exposes-code-execution.
# LLM tools are often declared as plain dict specs (not @tool decorators), so a
# "python"/"terminal" code-exec tool slips past the decorator rules. Match the
# tool's self-description. Real case: unsloth Studio's python/terminal tools.

PYTHON_TOOL = {
    "type": "function",
    "function": {
        "name": "python",
        "description": "Execute Python code in a sandbox and return stdout/stderr.",  # EXPECT_MATCH:scope.tool-exposes-code-execution
        "parameters": {"code": {"type": "string", "description": "The Python code to run"}},
    },
}

TERMINAL_TOOL = {
    "type": "function",
    "function": {
        "name": "terminal",
        "description": "Execute a terminal command and return stdout/stderr.",  # EXPECT_MATCH:scope.tool-exposes-code-execution
    },
}

# Benign tools must NOT fire — they describe retrieval / compute, not code exec.
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for a query and return results.",  # EXPECT_NONE:scope.tool-exposes-code-execution
    },
}

CALC_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Run a math calculation and return the result.",  # EXPECT_NONE:scope.tool-exposes-code-execution
    },
}
