#!/usr/bin/env bash
# Open every ClusterIP dashboard at a stable local port, in the foreground.
#
# Grafana, Superset, Flink, and ClickHouse have no Ingress in the local stack, so a
# reviewer cannot reach them without forwards. This holds them all open until
# Ctrl-C and cleans up after itself.
#
# Usage (from prod/):  bash deploy/scripts/port-forward-uis.sh
set -uo pipefail

CTX="${CTX:-k3d-agentsim}"
NS_DATA="${NS_DATA:-data}"
NS_OBS="${NS_OBS:-observability}"

kubectl --context "$CTX" get ns >/dev/null 2>&1 || {
  echo "cluster context '$CTX' unreachable - run 'make cluster-up' first." >&2; exit 1; }

declare -a SPECS=(
  "$NS_OBS|grafana|3000|80|Grafana"
  "$NS_DATA|superset|8088|8088|Superset"
  "$NS_DATA|flink-jobmanager|8081|8081|Flink UI"
  "$NS_DATA|clickhouse|8123|8123|ClickHouse"
)
declare -a PIDS=()

cleanup() {
  echo ""
  echo "closing forwards..."
  for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null || true; done
}
trap cleanup EXIT INT TERM

start_one() { # index -> (re)start that forward, store its pid
  local spec="${SPECS[$1]}"
  IFS='|' read -r ns svc lport rport _label <<<"$spec"
  kubectl --context "$CTX" -n "$ns" port-forward "svc/$svc" "$lport:$rport" >/dev/null 2>&1 &
  PIDS[$1]=$!
}

echo "Forwarding dashboards (Ctrl-C to stop):"
for i in "${!SPECS[@]}"; do
  IFS='|' read -r _ns _svc lport _rport label <<<"${SPECS[$i]}"
  start_one "$i"
  printf '  %-16s %s\n' "$label" "http://127.0.0.1:$lport"
done
echo ""
echo "Grafana and Superset: admin / admin. ClickHouse: asc / asc."
echo "Operator console is on the ingress already - run 'make urls' for its address."
echo ""

# kubectl port-forward drops its connection under concurrent load - a Superset
# dashboard firing several chart queries at once is enough to kill it, and the
# charts then render "Unexpected error" as if the data were bad. Restart a dead
# forward rather than exiting: the reviewer wants the dashboards to stay up.
while true; do
  for i in "${!SPECS[@]}"; do
    if ! kill -0 "${PIDS[$i]}" 2>/dev/null; then
      IFS='|' read -r _ns _svc lport _rport label <<<"${SPECS[$i]}"
      echo "  $label forward dropped - restarting on :$lport" >&2
      start_one "$i"
    fi
  done
  sleep 3
done
