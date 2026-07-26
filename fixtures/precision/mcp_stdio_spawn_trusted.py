# Precision fixture (NEGATIVE): legitimate, internally-configured MCP stdio spawns.
# The spawn recipe originates server-side (literals, a constant registry, a config
# file). Callers never supply command/args/env. None of these may fire.
import json
import pathlib

from langchain_mcp_adapters.client import MultiServerMCPClient

# Trusted server-side registry baked into the image.
ALLOWED_MCP_SERVERS = {
    "filesystem": {"command": "npx", "args": ["-y", "@mcp/filesystem"]},
}


def build_from_literals():
    sc = {"transport": "stdio"}
    sc["command"] = "npx"                                    # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
    sc["args"] = ["-y", "@mcp/filesystem"]                   # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
    return MultiServerMCPClient({"fs": sc})


def build_from_registry(name):
    sc = {"transport": "stdio"}
    sc["command"] = ALLOWED_MCP_SERVERS[name]["command"]     # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
    sc["args"] = ALLOWED_MCP_SERVERS[name]["args"]           # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
    return MultiServerMCPClient({name: sc})


def build_from_config_file():
    raw = json.loads(pathlib.Path("/etc/myapp/mcp_servers.json").read_text())
    out = {}
    for name, entry in raw.items():
        sc = {"transport": "stdio"}
        sc["command"] = entry["command"]                     # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
        sc["env"] = entry.get("env", {})                     # EXPECT_NONE:scope.mcp-stdio-spawn-from-external-config
        out[name] = sc
    return MultiServerMCPClient(out)
