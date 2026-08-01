# 02 — SandboxTemplate & SandboxWarmPool

## Run

```bash
./run.sh                            # kubectl apply -f sandboxcrd.yaml
kubectl delete -f sandboxcrd.yaml   # teardown; GCs its sandboxes and pods
```

## Verify

```bash
kubectl get sandboxwarmpools -n default -w
```

```
NAME                      READY   DESIRED   AGE
python-sandbox-warmpool   3       3         47m
```

## Notes

- **Be patient on Autopilot.** The first pod can take several minutes while a
  gVisor node is provisioned; `READY 0` with a `Pending` pod is normal.
  Check with `kubectl get nodes -L sandbox.gke.io/runtime`.
- Every `# Required` field in the manifest is enforced by the admission
  webhook: `runtimeClassName: gvisor`, `automountServiceAccountToken: false`,
  `runAsNonRoot: true`, the gVisor nodeSelector/toleration, a memory limit, and
  `capabilities.drop: ["ALL"]`.
- `replicas: 3` gives headroom — each execution consumes a pooled sandbox and
  Autopilot needs ~60s to schedule a replacement.
- `no matches for kind` means the wrong API group: template, warm pool and
  claim are `extensions.agents.x-k8s.io/v1beta1`; only `Sandbox` is
  `agents.x-k8s.io`.

Next: [`../03_setup_sandbox_router`](../03_setup_sandbox_router)
