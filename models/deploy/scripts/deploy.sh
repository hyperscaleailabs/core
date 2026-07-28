#!/usr/bin/env bash
# Deploy the model stack to the current kubectl context (local or remote K3s).
#
# Usage:
#   ./deploy/scripts/deploy.sh              # deploy all models
#   ./deploy/scripts/deploy.sh faster-whisper gemma-vllm   # subset
#
# Point KUBECONFIG at .kube/remote-config to target an SSH-provisioned box.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODELS_DIR="$REPO_ROOT/deploy/k3s/models"

echo "==> Context: $(kubectl config current-context)"
kubectl apply -k "$REPO_ROOT/deploy/k3s/base"

if [[ $# -gt 0 ]]; then
  MANIFESTS=()
  for name in "$@"; do
    MANIFESTS+=("$MODELS_DIR/$name.yaml")
  done
else
  MANIFESTS=("$MODELS_DIR"/*.yaml)
fi

for manifest in "${MANIFESTS[@]}"; do
  echo "==> Applying $(basename "$manifest")"
  kubectl apply -f "$manifest"
done

echo "==> Waiting for rollouts"
for manifest in "${MANIFESTS[@]}"; do
  name="$(basename "$manifest" .yaml)"
  kubectl -n hyperswarm-models rollout status "deployment/$name" --timeout=15m
done

kubectl -n hyperswarm-models get pods,svc
