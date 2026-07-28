#!/usr/bin/env bash
# Print the reachable URLs for a deployed stack, discovered rather than assumed.
#
# The previous version hardcoded port 8080 and listed every surface as an ingress
# host, which was wrong on a real cluster: k3d publishes the load balancer on
# whatever host port was free, and only operator-web has an Ingress - Grafana,
# Superset, and Flink are ClusterIP and need port-forwards. Printing URLs that do
# not answer is worse than printing none.
set -uo pipefail

CTX="${CTX:-k3d-agentsim}"
CLUSTER="${CLUSTER_NAME:-agentsim}"
NS_PLATFORM="${NS_PLATFORM:-platform}"

k() { kubectl --context "$CTX" "$@"; }

if ! k get ns >/dev/null 2>&1; then
  echo "cluster context '$CTX' unreachable - run 'make cluster-up' first." >&2
  exit 1
fi

# The published host port of the k3d load balancer, read from the container.
LB_PORT=""
if command -v docker >/dev/null 2>&1; then
  LB_PORT=$(docker port "k3d-${CLUSTER}-serverlb" 2>/dev/null \
    | awk -F: '/^80\/tcp -> 0\.0\.0\.0/ {print $2; exit}')
fi
LB_PORT="${LB_PORT:-${LB_PORT_OVERRIDE:-8080}}"

INGRESS_HOST=$(k -n "$NS_PLATFORM" get ingress operator-web \
  -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || true)
INGRESS_HOST="${INGRESS_HOST:-operator.localhost}"

echo "Ingress (reachable now):"
printf '  %-16s %s\n' "Operator console" "http://${INGRESS_HOST}:${LB_PORT}/"
printf '  %-16s %s\n' "v0.1.0 MVP" "http://${INGRESS_HOST}:${LB_PORT}/mvp/"
printf '  %-16s %s\n' "Control API docs" "http://${INGRESS_HOST}:${LB_PORT}/api/docs"
echo ""
echo "ClusterIP services - start the forwards with 'make dashboards', then:"
printf '  %-16s %s\n' "Grafana" "http://127.0.0.1:3000   (admin / admin)"
printf '  %-16s %s\n' "Superset" "http://127.0.0.1:8088   (admin / admin)"
printf '  %-16s %s\n' "Flink UI" "http://127.0.0.1:8081"
printf '  %-16s %s\n' "ClickHouse" "http://127.0.0.1:8123   (asc / asc)"
echo ""
echo "Credentials above are the local demo defaults committed in the manifests."
echo "A real deployment overrides them from its secret store; see the root README."
