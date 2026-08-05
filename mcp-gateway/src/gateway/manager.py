import signal
import sys

from gateway.config import load_config
from gateway.process import StdioProcess


class GatewayManager:
    def __init__(self):
        self.procs: dict[str, StdioProcess] = {}
        self.tool_router: dict[str, str] = {}
        self.all_tools: list[dict] = []

    def start(self):
        cfg = load_config()
        for server_cfg in cfg["servers"]:
            if not server_cfg.get("enabled", True):
                print(f"[gateway] — Skipping (disabled): {server_cfg['name']}")
                continue
            proc = StdioProcess(server_cfg)
            try:
                proc.start()
                self.procs[server_cfg["name"]] = proc
            except Exception as exc:
                print(f"[gateway] ERROR starting '{server_cfg['name']}': {exc}")
        self._collect_tools()
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _collect_tools(self):
        for name, proc in self.procs.items():
            try:
                tools = proc.list_tools()
                for tool in tools:
                    namespaced = f"{name}__{tool['name']}"
                    self.tool_router[namespaced] = name
                    self.all_tools.append({**tool, "name": namespaced})
                print(f"[gateway]   {name}: {len(tools)} tool(s) loaded")
            except Exception as exc:
                print(f"[gateway] ERROR collecting tools from '{name}': {exc}")

    def call(self, namespaced: str, args: dict) -> dict:
        server_name = self.tool_router.get(namespaced)
        if not server_name:
            return {"error": f"Unknown tool: '{namespaced}'"}
        if not self.procs[server_name].alive:
            return {"error": f"Server '{server_name}' is not running"}
        original_name = namespaced.split("__", 1)[1]
        return self.procs[server_name].call_tool(original_name, args)

    def _shutdown(self, *_):
        print("\n[gateway] Shutting down all servers...")
        for proc in self.procs.values():
            proc.stop()
        sys.exit(0)
