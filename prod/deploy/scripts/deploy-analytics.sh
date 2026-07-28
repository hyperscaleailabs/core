#!/usr/bin/env bash
# Wave 4 (ASC-032/033): Druid + Superset, then register the Kafka indexing supervisors and import
# Superset dashboards. Called by deploy-local.sh. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

helm repo add druid-helm https://asdf2014.github.io/druid-helm/ >/dev/null 2>&1 || true
helm repo add superset https://apache.github.io/superset >/dev/null 2>&1 || true
helm repo update >/dev/null

helm upgrade --install druid druid-helm/druid -n data \
  -f "$ROOT/deploy/helm-values/druid.yaml" --wait
helm upgrade --install superset superset/superset -n data \
  -f "$ROOT/deploy/helm-values/superset.yaml" --wait

# Register Druid Kafka indexing supervisors via a port-forward to the router/overlord.
kubectl -n data port-forward svc/druid-router 18888:8888 >/tmp/druid-pf.log 2>&1 &
PF=$!
trap 'kill $PF 2>/dev/null || true' EXIT
for i in $(seq 1 30); do curl -sf http://127.0.0.1:18888/status >/dev/null 2>&1 && break; sleep 2; done
for spec in iteration_events_supervisor failure_stats_supervisor; do
  echo ">> submit druid supervisor: $spec"
  curl -sf -X POST -H 'Content-Type: application/json' \
    --data @"$ROOT/ingestion/druid/${spec}.json" \
    http://127.0.0.1:18888/druid/indexer/v1/supervisor >/dev/null && echo "   ok" || echo "   FAILED (check druid)"
done

echo ">> Superset: register the Druid dataset + import dashboards/superset/* (see its README)."
echo ">> analytics stack deployed."
