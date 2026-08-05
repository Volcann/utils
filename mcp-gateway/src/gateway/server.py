from typing import Any

from fastmcp import FastMCP

from gateway.config import load_config
from gateway.manager import GatewayManager

gateway = FastMCP("mcp-gateway")
manager = GatewayManager()


def _build_tool_function(namespaced_name: str, tool_def: dict):
    schema = tool_def.get("inputSchema", {})
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    type_map = {
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "object": "dict",
        "array": "list",
        "string": "str",
    }

    params = []
    req_keys = [k for k in props if k in required]
    opt_keys = [k for k in props if k not in required]

    for k in req_keys:
        ptype = props[k].get("type", "string")
        tname = type_map.get(ptype, "str")
        params.append(f"{k}: {tname}")

    for k in opt_keys:
        ptype = props[k].get("type", "string")
        tname = type_map.get(ptype, "str")
        params.append(f"{k}: {tname} = None")

    param_str = ", ".join(params)
    fn_name = f"tool_{namespaced_name}".replace("-", "_").replace(".", "_")

    code = f"""
def {fn_name}({param_str}):
    kwargs = {{k: v for k, v in locals().items() if v is not None}}
    result = manager.call('{namespaced_name}', kwargs)
    if isinstance(result, dict) and "content" in result:
        texts = [b.get("text", "") for b in result["content"] if isinstance(b, dict) and b.get("type") == "text"]
        return "\\n".join(texts) or str(result)
    return result
"""
    local_ns = {"manager": manager}
    exec(code, local_ns)
    fn = local_ns[fn_name]
    fn.__doc__ = tool_def.get("description", "")
    return fn


def _register_tool(tool_def: dict):
    name = tool_def["name"]
    fn = _build_tool_function(name, tool_def)
    gateway.tool(name=name)(fn)


def run():
    cfg = load_config()
    gw_cfg = cfg["gateway"]

    manager.start()

    for tool_def in manager.all_tools:
        _register_tool(tool_def)

    total = len(manager.all_tools)
    print(f"\n[gateway] {total} tool(s) ready across {len(manager.procs)} server(s)")
    print(f"[gateway] Listening → http://{gw_cfg['host']}:{gw_cfg['port']}/mcp\n")

    gateway.run(
        transport="streamable-http",
        host=gw_cfg["host"],
        port=gw_cfg["port"],
        stateless_http=True,
        json_response=True,
    )
