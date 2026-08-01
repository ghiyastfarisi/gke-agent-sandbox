export REGION="asia-southeast2"
export ZONE="asia-southeast2-a"
export CLUSTER="agent-sandbox-auto"

kubectl scale sandboxwarmpool/python-sandbox-warmpool --replicas=0
kubectl delete sandboxclaims --all -n default
kubectl get sandboxes,sandboxclaims,pods -n default 