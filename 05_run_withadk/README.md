# 05 — ADK agent + sandbox

An ADK `LlmAgent` writes Python; a throwaway gVisor sandbox runs it. The
model's code never executes on your machine.

| File | Role |
|---|---|
| `main_adk.py` | The agent — ~30 lines |
| `sandbox_executor.py` | `SandboxCodeExecutor`, the ADK ↔ agent-sandbox glue |

## Run

```bash
cp .env.example .env    # then paste a key from aistudio.google.com/apikey
uv run main_adk.py
```

Needs steps 01–03 done. Start with [`../04_run_pysandbox`](../04_run_pysandbox)
if you haven't — it proves the plumbing without an LLM in the way.

## Verify

```
--- code written by the LLM ---
import math

print(math.factorial(17))
--- output from the gVisor sandbox ---
Code execution result:
355687428096000
```

The model wrote the code; the sandbox computed the answer. Watch the pods churn
during a run to confirm it ran remotely:

```bash
kubectl get pods -n default -w
kubectl logs -n default -l app=sandbox-router --tail=5
```

## Notes

**Why a custom executor.** ADK's built-in `GkeCodeExecutor(executor_type=
"sandbox")` targets an older SDK and fails against `k8s-agent-sandbox` 0.5.4 —
it calls `SandboxClient(template_name=…)` and `sandbox.run()`, neither of which
exists. `sandbox_executor.py` is the ~40-line equivalent for the current API.

**Sandbox quirks it works around**, none of them documented upstream:

- `files.write()` fails — the runtime's `/upload` endpoint isn't wired up, so
  code ships as base64.
- `/execute` has no shell; it splits arguments. Pipes and redirection need an
  explicit `sh -c`.
- `close_connection()` permanently nulls `commands`/`files`. A failed request
  kills the port-forward, so a retry needs a *whole new sandbox*.

**Known flakiness:**

| Symptom | What's happening |
|---|---|
| `502`/`504` on first execute | Cold sandbox. The executor retries with a fresh one; the run still passes |
| Run stalls ~60s+ | Warm pool drained — each run consumes one, Autopilot is slow to replace it. Raise `replicas` in `../02_setup_sandbox_crd/sandboxcrd.yaml` |
| `ModuleNotFoundError` | Standard library only — nothing third-party is installed |
| `No API key was provided` | Missing or empty `.env` |

**Model variance.** With a loose instruction the model sometimes reached for
`sympy` or answered without emitting code (4/6 before the prompt was tightened).
The instruction in `main_adk.py` pins *"Standard library only"* — keep it if the
demo must not fail live.

## Versions

`google-adk` 2.6.0 · `k8s-agent-sandbox` 0.5.4 · `gemini-flash-latest` ·
runtime image `python-runtime-sandbox:v0.1.0`

Bonus: [`../bonus`](../bonus) — the same sandbox as an MCP tool for Antigravity.
