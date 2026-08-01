# 03 — Sandbox router

Creates `Service/sandbox-router-svc` (ClusterIP :8080) and
`Deployment/sandbox-router-deployment` in `default`. It proxies `/execute`
through to the sandbox pod on :8888.

## Run

```bash
./run.sh                               # kubectl apply -f sandboxrouter.yaml
kubectl delete -f sandboxrouter.yaml   # teardown
```

## Verify

```bash
kubectl get pods -n default -l app=sandbox-router     # 1/1, no restarts
kubectl logs -n default -l app=sandbox-router --tail=20
```

```
Proxying request for sandbox 'python-sandbox-warmpool-xxxxx' to URL: http://10.x.x.x:8888/execute
INFO:     127.0.0.1:33102 - "POST /execute HTTP/1.1" 200 OK
```

## Notes

- Clients must pass `router_namespace="default"` — the SDK defaults to
  `agent-sandbox-system`, where there is no router Service.
- `ALLOW_UNAUTHENTICATED_ROUTER: "true"` is set because the Python SDK sends no
  `Authorization` header; setting `ROUTER_AUTH_TOKEN` instead would lock out
  the client. Without either, the router refuses to start. **Demo clusters
  only.**
- `sandbox-router:latest-main` is a floating staging tag — pin a digest if you
  need repeatability.
- `504` on `/execute` means the sandbox pod is still `0/1` and its readiness
  probe on :8888 hasn't passed.

Next: [`../04_run_pysandbox`](../04_run_pysandbox)
