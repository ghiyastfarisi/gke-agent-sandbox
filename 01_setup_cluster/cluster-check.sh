export PROJECT_ID=$(gcloud config get project)
export REGION="asia-southeast2"          # Jakarta
export ZONE="asia-southeast2-a"
export CLUSTER="agent-sandbox-auto"

gcloud services enable container.googleapis.com artifactregistry.googleapis.com

gcloud container get-server-config --location=${REGION} \
  --format="yaml(channels)" | grep -A3 RAPID

gcloud beta container clusters describe ${CLUSTER} \
  --location=${REGION} \
  --format="value(addonsConfig.agentSandboxConfig.enabled)"

kubectl get runtimeclass gvisor
kubectl get crd | grep agents.x-k8s.io
kubectl get deploy -n agent-sandbox-system
kubectl get nodes -L sandbox.gke.io/runtime 
