#!/usr/bin/env bash
# Deploy the stack to the local cluster in dependency-aware waves (ASC-052, DEPLOYMENT.md §3).
# Idempotent: re-running upgrades in place. Requires a running cluster (make cluster-up), kubectl,
# and helm. Cluster bring-up itself pulls several GB (Druid/Flink/Superset) - run when ready.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OVERLAY="${OVERLAY:-local}"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
need kubectl; need helm

ns() { kubectl create namespace "$1" --dry-run=client -o yaml | kubectl apply -f -; }
wait_rollout() { kubectl -n "$1" rollout status "$2" --timeout="${3:-180s}"; }

echo "== Wave 1: namespaces + secrets =="
ns platform; ns data; ns observability
if [[ -f "$ENV_FILE" ]]; then
  kubectl -n data create secret generic asc-secrets --from-env-file="$ENV_FILE" \
    --dry-run=client -o yaml | kubectl apply -f -
else
  echo ">> WARN: $ENV_FILE not found; copy .env.example -> .env before deploying stateful infra."
fi

echo "== Wave 2: data infra (PostgreSQL, MinIO, Kafka) + topics =="
BITNAMI=oci://registry-1.docker.io/bitnamicharts
helm upgrade --install postgres "$BITNAMI/postgresql" -n data -f "$ROOT/deploy/helm-values/postgresql.yaml" --wait
helm upgrade --install minio    "$BITNAMI/minio"      -n data -f "$ROOT/deploy/helm-values/minio.yaml" --wait
helm upgrade --install kafka    "$BITNAMI/kafka"      -n data -f "$ROOT/deploy/helm-values/kafka.yaml" --wait
kubectl apply -f "$ROOT/deploy/k3s/components/kafka/topics-job.yaml"
kubectl -n data wait --for=condition=complete job/kafka-topic-bootstrap --timeout=180s || true

echo "== Wave 3: observability (OTel, Prometheus, Tempo, Grafana) =="
if [[ -x "$ROOT/deploy/scripts/deploy-observability.sh" ]]; then
  bash "$ROOT/deploy/scripts/deploy-observability.sh"
else
  echo ">> deploy-observability.sh not present yet (added with ASC-040..042); skipping."
fi

echo "== Wave 4: stream/analytics (Flink, Druid, Superset) =="
if kubectl get crd flinkdeployments.flink.apache.org >/dev/null 2>&1; then
  kubectl apply -f "$ROOT/deploy/k3s/components/flink/flinkdeployment.yaml"
else
  echo ">> Flink operator CRDs not installed; install via deploy/helm-values/flink-operator.yaml."
fi
if [[ -x "$ROOT/deploy/scripts/deploy-analytics.sh" ]]; then
  bash "$ROOT/deploy/scripts/deploy-analytics.sh"
else
  echo ">> deploy-analytics.sh not present yet (added with ASC-032/033); skipping Druid/Superset."
fi

echo "== Wave 5: platform services =="
kubectl apply -k "$ROOT/deploy/k3s/apps/overlays/$OVERLAY"
wait_rollout platform deploy/control-api
wait_rollout platform deploy/mcp-simulator-proxy
wait_rollout platform deploy/operator-web

echo "== Wave 6: URLs =="
bash "$ROOT/deploy/scripts/print-urls.sh"
