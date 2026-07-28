#!/bin/sh
# Runs from nginx's /docker-entrypoint.d/ before nginx starts: inject runtime config into
# /config.js from env. Does NOT start nginx (the base image's entrypoint does that afterwards).
set -eu
: "${CONTROL_API_BASE_URL:=/api}"
: "${GRAFANA_BASE_URL:=http://grafana.localhost:8080}"
: "${SUPERSET_BASE_URL:=http://superset.localhost:8080}"
export CONTROL_API_BASE_URL GRAFANA_BASE_URL SUPERSET_BASE_URL

envsubst '${CONTROL_API_BASE_URL} ${GRAFANA_BASE_URL} ${SUPERSET_BASE_URL}' \
  < /usr/share/nginx/html/config.js.template > /usr/share/nginx/html/config.js
