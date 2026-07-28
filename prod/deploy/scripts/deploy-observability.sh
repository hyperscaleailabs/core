#!/usr/bin/env bash
# Wave 3 (ASC-040/041/042): OTel Collector + Prometheus + Tempo + Grafana (with provisioning).
# Called by deploy-local.sh. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

kubectl apply -f "$ROOT/deploy/k3s/components/otel/collector.yaml"

helm repo add grafana https://grafana.github.io/helm-charts >/dev/null 2>&1 || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

helm upgrade --install tempo grafana/tempo -n observability \
  -f "$ROOT/deploy/helm-values/tempo.yaml" --wait
helm upgrade --install kps prometheus-community/kube-prometheus-stack -n observability \
  -f "$ROOT/deploy/helm-values/kube-prometheus-stack.yaml" --wait

# Provision Grafana datasources + the ASC dashboard via labeled ConfigMaps (sidecar discovery).
kubectl -n observability create configmap grafana-ds-asc \
  --from-file="$ROOT/dashboards/grafana/provisioning/datasources.yaml" \
  --dry-run=client -o yaml | kubectl label -f - --local -o yaml --dry-run=client \
  grafana_datasource=1 | kubectl apply -f -
kubectl -n observability create configmap grafana-dash-asc-overview \
  --from-file="$ROOT/dashboards/grafana/asc-overview.json" \
  --dry-run=client -o yaml | kubectl label -f - --local -o yaml --dry-run=client \
  grafana_dashboard=1 | kubectl apply -f -
kubectl -n observability create configmap grafana-alerts-asc \
  --from-file="$ROOT/dashboards/grafana/provisioning/alerts.yaml" \
  --dry-run=client -o yaml | kubectl label -f - --local -o yaml --dry-run=client \
  grafana_alert=1 | kubectl apply -f -

echo ">> observability stack deployed."
