#!/usr/bin/env bash
# Lite data + observability deploy for memory-constrained hosts (ASC-083/084):
# Kafka + embedded Flink failure-stats + OTel Collector + Tempo + Grafana. Skips the heaviest
# tenants (Druid/Superset/Prometheus). Assumes the platform services are already deployed and the
# agentsim cluster is current. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="/opt/homebrew/bin:$PATH"

kubectl create namespace data          --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -

echo "== Kafka (single-node KRaft, official image) + topics =="
helm repo add grafana https://grafana.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null
kubectl apply -f "$ROOT/deploy/k3s/components/kafka/kafka-kraft.yaml"
kubectl -n data rollout status deploy/kafka --timeout=180s
kubectl apply -f "$ROOT/deploy/k3s/components/kafka/topics-job.yaml"
kubectl -n data wait --for=condition=complete job/kafka-topic-bootstrap --timeout=180s || true

echo "== Flink session cluster + submit failure-stats SQL =="
kubectl apply -f "$ROOT/deploy/k3s/components/flink/flink-session.yaml"
kubectl -n data rollout status deploy/flink-jobmanager --timeout=150s
kubectl -n data rollout status deploy/flink-taskmanager --timeout=120s
kubectl delete job flink-sql-submit -n data >/dev/null 2>&1 || true
kubectl apply -f "$ROOT/deploy/k3s/components/flink/flink-sql-submit.yaml"
kubectl -n data wait --for=condition=complete job/flink-sql-submit --timeout=180s || true

echo "== Observability: OTel Collector + Tempo + Grafana =="
kubectl apply -f "$ROOT/deploy/k3s/components/otel/collector.yaml"
helm upgrade --install tempo grafana/tempo -n observability -f "$ROOT/deploy/helm-values/tempo.yaml" --wait
helm upgrade --install grafana grafana/grafana -n observability -f "$ROOT/deploy/helm-values/grafana-lite.yaml" --wait

echo "== Point platform services at Kafka + OTel =="
kubectl -n platform set env deploy/control-api \
  KAFKA_BOOTSTRAP=kafka.data.svc.cluster.local:9092 \
  OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector.observability.svc.cluster.local:4317
kubectl -n platform rollout status deploy/control-api --timeout=120s

echo ">> lite data + observability stack deployed."
