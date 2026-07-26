# Precision fixture (POSITIVE): MCP stdio spawn recipe built from a caller-injected
# config with no server-side origin anywhere in the module. This is the
# gpt-researcher CVE shape: anonymous websocket JSON -> mcp_configs -> argv.
# NOTE: guards are module-scoped, so negatives live in mcp_stdio_spawn_trusted.py.
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPClientManager:
    def __init__(self, mcp_configs):
        self.mcp_configs = mcp_configs or []

    def convert_configs_to_langchain_format(self):
        server_configs = {}
        for i, config in enumerate(self.mcp_configs):
            server_config = {}
            server_config["transport"] = config.get("connection_type", "stdio")
            if server_config.get("transport") == "stdio":
                if config.get("command"):
                    server_config["command"] = config["command"]      # EXPECT_MATCH:scope.mcp-stdio-spawn-from-external-config
                    server_args = config.get("args", [])
                    server_config["args"] = server_args               # EXPECT_MATCH:scope.mcp-stdio-spawn-from-external-config
                    server_env = config.get("env", {})
                    if server_env:
                        server_config["env"] = server_env             # EXPECT_MATCH:scope.mcp-stdio-spawn-from-external-config
            server_configs[config.get("name", f"s{i}")] = server_config
        return server_configs

    def client(self):
        return MultiServerMCPClient(self.convert_configs_to_langchain_format())
