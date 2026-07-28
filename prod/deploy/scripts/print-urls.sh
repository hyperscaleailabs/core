#!/usr/bin/env bash
# Print operator-web / Grafana / Superset / Druid / Flink URLs for the local cluster.
# Implemented in ASC-053.
set -euo pipefail
LB_PORT="${LB_PORT:-8080}"
cat <<EOF
Operator Web : http://operator.localhost:${LB_PORT}
Grafana      : http://grafana.localhost:${LB_PORT}
Superset     : http://superset.localhost:${LB_PORT}
Druid        : http://druid.localhost:${LB_PORT}
Flink UI     : http://flink.localhost:${LB_PORT}

(If ingress hostnames are not resolvable, add them to /etc/hosts pointing at 127.0.0.1,
 or use: kubectl -n <ns> port-forward svc/<svc> <port>.)
EOF
