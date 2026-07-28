#!/usr/bin/env bash
# Create a local k3d cluster with a mapped load-balancer port and a local image registry.
# Implemented in ASC-050. This is the scaffold entrypoint referenced by `make cluster-up`.
set -euo pipefail

CLUSTER_NAME="${1:-agentsim}"
REGISTRY_PORT="${REGISTRY_PORT:-5001}"
LB_PORT="${LB_PORT:-8080}"

if ! command -v k3d >/dev/null 2>&1; then
  echo "k3d is required. Install: https://k3d.io" >&2
  exit 1
fi

if k3d cluster list | awk '{print $1}' | grep -qx "$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' already exists."
  exit 0
fi

echo ">> Creating k3d cluster '$CLUSTER_NAME' (registry :$REGISTRY_PORT, lb :$LB_PORT)"
k3d cluster create "$CLUSTER_NAME" \
  --servers 1 --agents 2 \
  --registry-create "${CLUSTER_NAME}-registry:0.0.0.0:${REGISTRY_PORT}" \
  --port "${LB_PORT}:80@loadbalancer" \
  --wait

kubectl create namespace platform      --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace data          --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -

echo ">> Cluster '$CLUSTER_NAME' ready. Next: make deploy-local"
