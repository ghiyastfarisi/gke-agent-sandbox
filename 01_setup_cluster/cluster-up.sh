export REGION="asia-southeast2"
export ZONE="asia-southeast2-a"
export CLUSTER="agent-sandbox-auto"

gcloud beta container clusters create-auto ${CLUSTER} \
  --location=${REGION} \
  --release-channel=rapid \
  --enable-agent-sandbox

gcloud container clusters get-credentials ${CLUSTER} --location=${REGION}
