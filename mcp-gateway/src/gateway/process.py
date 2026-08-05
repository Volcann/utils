import json
import os
import subprocess
import sys
import threading


class StdioProcess:
    def __init__(self, cfg: dict):
        self.name: str = cfg["name"]
        self.cfg = cfg
        self.proc: subprocess.Popen | None = None
        self._id = 0
        self._lock = threading.Lock()

    def start(self):
        env = {**os.environ, **self.cfg.get("env", {})}
        cmd = [self.cfg["command"]] + self.cfg.get("args", [])
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            env=env,
        )
        print(f"[gateway] ✓ Started '{self.name}' (pid={self.proc.pid})")
        self._initialize()

    def _initialize(self):
        try:
            self._rpc(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-gateway", "version": "0.1.0"},
                },
            )
            self._notify("notifications/initialized", {})
        except Exception as exc:  # noqa: BLE001
            print(f"[gateway] Note: initialize for '{self.name}': {exc}")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            print(f"[gateway] ✗ Stopped '{self.name}'")

    @property
    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def _notify(self, method: str, params: dict):
        with self._lock:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }) + "\n"
            if self.proc and self.proc.stdin:
                self.proc.stdin.write(payload)
                self.proc.stdin.flush()

    def _rpc(self, method: str, params: dict) -> dict:
        with self._lock:
            self._id += 1
            req_id = self._id
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "method": method,
                "params": params,
            }) + "\n"
            if not self.proc or not self.proc.stdin or not self.proc.stdout:
                raise RuntimeError(f"Process '{self.name}' is not running")
            self.proc.stdin.write(payload)
            self.proc.stdin.flush()

            while True:
                raw = self.proc.stdout.readline()
                if not raw:
                    raise RuntimeError(
                        f"Process '{self.name}' closed stdout unexpectedly"
                    )
                raw_str = raw.strip()
                if not raw_str:
                    continue
                try:
                    data = json.loads(raw_str)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict) and data.get("id") == req_id:
                    if "error" in data:
                        raise RuntimeError(
                            f"[{self.name}] RPC error: {data['error']}"
                        )
                    return data.get("result", {})

    def list_tools(self) -> list[dict]:
        return self._rpc("tools/list", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        return self._rpc("tools/call", {"name": name, "arguments": arguments})
