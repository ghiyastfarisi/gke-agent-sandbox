# Sandbox router: ClusterIP Service + Deployment in `default`.
# Clients must set router_namespace="default" — the SDK defaults to
# agent-sandbox-system.

kubectl apply -f sandboxrouter.yaml

kubectl get svc sandbox-router-svc -n default
kubectl get pods -n default -l app=sandbox-router
