# Precision fixture: the FastMCP call-decorator @mcp.tool() must be REACHABLE.
# Regression guard for the decorated_definition anchor fix (these rules matched
# nothing before because they anchored on function_definition).
# Tags may be scoped to a rule id: EXPECT_MATCH:rule-id / EXPECT_NONE:rule-id.

@mcp.tool()
def run_cmd(cmd: str):
    import subprocess
    return subprocess.run(cmd, shell=True)            # EXPECT_MATCH:scope.mcp-server-without-input-validation

@mcp.tool()
def fetch(url: str):
    import requests
    return requests.get(url).text                      # EXPECT_MATCH:sign.mcp-tool-without-allowlist

@server.tool
def fetch_bare(url: str):
    import requests
    return requests.get(url).text                      # EXPECT_MATCH:sign.mcp-tool-without-allowlist

@mcp.tool()
def safe_fetch(url: str, ctx):
    from urllib.parse import urlparse
    if urlparse(url).netloc not in ALLOWED_HOSTS:      # EXPECT_NONE:sign.mcp-tool-without-allowlist
        raise ValueError("blocked")
    import requests
    return requests.get(url).text
