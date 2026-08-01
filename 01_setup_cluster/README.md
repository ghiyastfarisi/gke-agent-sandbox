# 01 — GKE Autopilot cluster with Agent Sandbox

## Run

```bash
./cluster-check.sh   # enable APIs, check the region offers a RAPID version
./cluster-up.sh      # create-auto --enable-agent-sandbox + get-credentials
./cluster-down.sh    # drain the warm pool and claims
```

Jakarta (`asia-southeast2`), cluster `agent-sandbox-auto`. Each script has its
own `export` block — edit in place.

## Verify

```bash
./cluster-check.sh
```

Four CRDs and a running controller in `agent-sandbox-system`:

```
sandboxclaims.extensions.agents.x-k8s.io
sandboxes.agents.x-k8s.io
sandboxtemplates.extensions.agents.x-k8s.io
sandboxwarmpools.extensions.agents.x-k8s.io
```

## Notes

- Do **not** pin `--cluster-version`. RAPID retires old patch versions and
  pinning below the current default causes an opaque rejection.
- No gVisor node yet is fine — Autopilot provisions one when step 02 creates
  the warm pool.
- Cluster deletion is commented out in `cluster-down.sh`.

Next: [`../02_setup_sandbox_crd`](../02_setup_sandbox_crd)
