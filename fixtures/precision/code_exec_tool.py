# Precision fixture for scope.tool-exposes-code-execution.
# LLM tools are often declared as plain dict specs (not @tool decorators), so a
# code-exec tool slips past the decorator rules. The rule generalizes across
# frameworks/wordings (NOT tuned to one repo) — it signals on canonical exec tool
# NAMES and verb-agnostic exec DESCRIPTIONS. Each tool below uses a different
# framework's idiom. Tags sit on the line that fires (name or description).

# unsloth Studio python tool (the case that exposed the gap) — name + description.
PYTHON_TOOL = {
    "function": {
        "name": "python",                                                         # EXPECT_MATCH:scope.tool-exposes-code-execution
        "description": "Execute Python code in a sandbox and return stdout/stderr.",
    },
}

# Terminal tool, different verb-object wording.
TERMINAL_TOOL = {"name": "terminal", "description": "Execute a terminal command."}  # EXPECT_MATCH:scope.tool-exposes-code-execution

# OpenAI Assistants code_interpreter (type, not name).
CODE_INTERP = {"type": "code_interpreter"}                                          # EXPECT_MATCH:scope.tool-exposes-code-execution

# MCP function tool, "run_code" / "Runs the provided code".
RUN_CODE = {"name": "run_code", "description": "Runs the provided code and returns output."}  # EXPECT_MATCH:scope.tool-exposes-code-execution

# LangChain PythonREPL idiom.
REPL = {"name": "python_repl", "description": "A Python shell. Use this to execute python commands."}  # EXPECT_MATCH:scope.tool-exposes-code-execution

# Generic shell tool, terse.
SHELL = {"name": "shell", "description": "Run shell commands on the host."}         # EXPECT_MATCH:scope.tool-exposes-code-execution

# Bash tool whose description is vague — caught by the canonical NAME signal.
BASH = {"name": "bash", "description": "A persistent session for the agent."}       # EXPECT_MATCH:scope.tool-exposes-code-execution

# ---- Benign tools — must NOT fire. They describe retrieval / a specific compute,
# ---- not code/shell execution. These are the false-positive guards.
WEB_SEARCH = {"name": "web_search", "description": "Search the web for a query and return results."}  # EXPECT_NONE:scope.tool-exposes-code-execution
CALC = {"name": "calculator", "description": "Run a math calculation and return the result."}         # EXPECT_NONE:scope.tool-exposes-code-execution
DB = {"name": "query_db", "description": "Run a read-only SQL query against the catalog."}            # EXPECT_NONE:scope.tool-exposes-code-execution
EMAIL = {"name": "send_email", "description": "Send an email to a recipient."}                        # EXPECT_NONE:scope.tool-exposes-code-execution
