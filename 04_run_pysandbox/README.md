# 04 — Run code in a sandbox from Python

No LLM. Claims a pod from the warm pool, runs `ls -la` inside it, terminates it.
Proves the cluster plumbing works before an agent is in the picture.

## Run

```bash
uv run main_agent_sandbox.py
```

Needs steps 01–03 done, `uv`, and `kubectl` pointed at the cluster.

## Verify

```
total 33
drwxr-xr-x 1 1000 1000    60 ...  .
drwxr-xr-x 1 root root    80 ...  ..
-rwxr-xr-x 1 1000 1000  3675 ...  main.py
-rw-r--r-- 1 1000 1000 29388 ...  requirements.txt
```

That listing is the sandbox's filesystem, not yours. Then check nothing leaked:

```bash
kubectl get sandboxclaims -A            # expect: No resources found
kubectl get sandboxwarmpools -n default # replenished back to 3
```

## Notes

Three things the client must get right — all three are in the script:

- `create_sandbox(warmpool=...)`, **not** `template=`. You name the warm pool;
  it resolves the template itself.
- `router_namespace="default"` — the SDK defaults to `agent-sandbox-system`,
  but step 03 deploys the router to `default`.
- Retry past `SandboxTemplateNotFoundError`. On warm-pool adoption the
  controller briefly writes `Ready=False/TemplateNotFound` before flipping to
  ready ~70ms later, so a bare call fails most of the time. The message names
  the warm pool as a missing template; nothing is actually missing.

`SandboxLocalTunnelConnectionConfig` is the only mode that works from a laptop —
it shells out to `kubectl port-forward`. The in-cluster modes resolve
`*.svc.cluster.local`.

Always `terminate()` in a `finally` block, or claims and pods leak.

| Symptom | Fix |
|---|---|
| Hangs for minutes | Warm pool drained — Autopilot needs ~60s per replacement |
| `504`/`502` | Cold sandbox, readiness probe on :8888 not passing yet |

Next: [`../05_run_withadk`](../05_run_withadk)
