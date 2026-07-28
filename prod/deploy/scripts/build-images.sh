#!/usr/bin/env bash
# Build service container images and push to the local k3d registry (ASC-007).
# Build context is the repo root so the monorepo packages are available to each image.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REGISTRY="${REGISTRY:-k3d-agentsim-registry:5001}"
TAG="${TAG:-dev}"
PUSH="${PUSH:-1}"

# image-name : dockerfile : build-context
IMAGES="
control-api:deploy/docker/control-api.Dockerfile:.
mcp-simulator-proxy:deploy/docker/mcp-proxy.Dockerfile:.
operator-web:deploy/docker/operator-web.Dockerfile:.
flink-sql:stream/flink-job/Dockerfile.sql:stream/flink-job
"
# flink-job (PyFlink) is x86-only (no arm64 wheels); on arm64 use flink-sql above. To build it:
#   docker build -f stream/flink-job/Dockerfile -t $REGISTRY/flink-job:$TAG stream/flink-job

cd "$ROOT"
for entry in $IMAGES; do
  name="${entry%%:*}"; rest="${entry#*:}"; dockerfile="${rest%%:*}"; context="${rest#*:}"
  ref="${REGISTRY}/${name}:${TAG}"
  echo ">> build ${ref}  (${dockerfile}, ctx ${context})"
  docker build -f "$dockerfile" -t "$ref" "$context"
  if [[ "$PUSH" == "1" ]]; then docker push "$ref"; fi
done
echo "done."
