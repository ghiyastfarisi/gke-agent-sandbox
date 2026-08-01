# SandboxTemplate + SandboxWarmPool.
# Group split: Sandbox is agents.x-k8s.io; SandboxTemplate/WarmPool/Claim are
# extensions.agents.x-k8s.io. Wrong group => "no matches for kind".

kubectl apply -f sandboxcrd.yaml

kubectl get sandboxwarmpools,sandboxes -n default
kubectl get pods -n default -l sandbox=python-sandbox-example
