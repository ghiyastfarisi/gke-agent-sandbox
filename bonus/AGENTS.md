# AGENTS.md — GKE Agent Sandbox MCP server

Exposes the GKE Agent Sandbox to Antigravity as an MCP tool, so code the agent
writes executes on a gVisor-isolated pod in the cluster instead of on this
machine.

---

## Instructions for the agent

**Execute Python through `run_python_in_sandbox`, not the local terminal.**

- Any code you generate for the user — scratch calculations, data checks,
  one-off scripts — goes to `run_python_in_sandbox`.
- Do not fall back to `python3`, `uv run`, or a shell heredoc when the sandbox
  tool errors. Report the error instead. A local fallback silently defeats the
  isolation this project exists to demonstrate.
- The sandbox is **standard library only**. No `numpy`, `pandas`, `sympy`,
  `requests`. Write plain Python or say what's missing.
- Each call gets a **fresh sandbox that is destroyed afterwards**. Nothing
  persists between calls — no files, no variables, no installed packages. Send
  self-contained code every time.
- First call after an idle period can take ~60s while GKE Autopilot schedules a
  replacement pod. That is normal; do not retry in a loop.

---

## Setup

### 1. Prerequisites

The cluster side must be running — see [`../docs/run.md`](../docs/run.md):

```bash
kubectl get sandboxwarmpools -n default   # want READY 3
```

### 2. The server

`server.py` wraps the existing `SandboxCodeExecutor` from
[`../pycode/sandbox_executor.py`](../pycode/sandbox_executor.py):

```python
"""MCP server exposing the GKE Agent Sandbox as a tool."""

import sys

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, "../pycode")
from google.adk.code_executors.code_execution_utils import CodeExecutionInput
from sandbox_executor import SandboxCodeExecutor

mcp = FastMCP("gke-sandbox")
executor = SandboxCodeExecutor()


@mcp.tool()
def run_python_in_sandbox(code: str) -> str:
    """Run Python in an isolated gVisor sandbox on GKE.

    Standard library only. State does not persist between calls.
    """
    result = executor.execute_code(None, CodeExecutionInput(code=code))
    return result.stdout or result.stderr or "(no output)"


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 3. Register it with Antigravity

Workspace-local — `.agents/mcp_config.json`:

```json
{
  "mcpServers": {
    "gke-sandbox": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/trial4/agy-mcp", "server.py"]
    }
  }
}
```

Global instead: `~/.gemini/config/mcp_config.json`, same format.

Use an **absolute path** — the server is launched from Antigravity's working
directory, not this one.

### 4. Verify

Ask the agent to compute something, then confirm it ran remotely:

```bash
kubectl get pods -n default -w
```

A `python-sandbox-warmpool-*` pod should churn on each execution. If nothing
moves, the agent ran the code locally — see below.

---

## Making the sandbox the *only* execution path

Registering the tool makes the sandbox **available**, not **mandatory**. The
agent still has its own terminal and may use it, especially under time
pressure or when the sandbox errors.

Antigravity supports `disabledTools` and permission patterns such as
`mcp(server/tool)` / `mcp(server/*)`. To make the isolation claim enforceable
rather than advisory, deny the built-in local execution tool so the MCP tool is
the only route.

> ⚠️ **Unverified.** The permission syntax above is documented for MCP tools.
> Whether Antigravity's *built-in* terminal can be denied the same way has not
> been tested here. Confirm it in Antigravity's settings before claiming that
> *all* agent-generated code is sandboxed — the instructions at the top of this
> file are guidance the model usually follows, not a hard boundary.

---

## Security properties this demonstrates

Each execution lands on a pod created from
[`../sandboxcrd.yaml`](../sandboxcrd.yaml):

| Control | Effect |
|---|---|
| `runtimeClassName: gvisor` | Syscalls are intercepted by a user-space kernel |
| `automountServiceAccountToken: false` | No credential to reach the Kubernetes API |
| `runAsNonRoot: true` | No root inside the container |
| `capabilities.drop: ["ALL"]` | No Linux capabilities |
| memory/CPU limits | Runaway code can't exhaust the node |
| fresh sandbox per call | No state carried between executions |

**Caveat for a security audience:** the router runs with
`ALLOW_UNAUTHENTICATED_ROUTER=true` because the Python SDK cannot send a token.
Fine for a local demo cluster, not for anything shared. Rationale in
[`../docs/run.md`](../docs/run.md) §2.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| Tool missing in Antigravity | Bad path in `mcp_config.json`; must be absolute |
| `SandboxTemplateNotFoundError` | Warm-pool adoption race — the executor retries; a misleading message, nothing is actually missing |
| `504` / `502` on first call | Cold sandbox. The executor retries with a new one |
| Call hangs for minutes | Warm pool drained; raise `replicas` in `../sandboxcrd.yaml` |
| `ModuleNotFoundError` | Third-party import — standard library only |
| Pods don't churn during a run | The agent executed locally, not in the sandbox |
