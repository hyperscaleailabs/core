# Deployment — Local k3s now, GCP VM + k3s next

**Version:** 0.2.0-dev · **Companion to:** [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md),
[`CICD_STRATEGY.md`](CICD_STRATEGY.md)

Two environments, one set of manifests. Phase 1 targets a **local k3d/k3s** cluster on a laptop.
Phase 2 provisions a **GCP VM running k3s** with Terraform and rolls the identical manifests. The
only differences are the overlay (resources, storage class, ingress host) and how secrets are
sourced.

---

## 1. Prerequisites

**Local (phase 1):** Docker, `k3d` (already installed), `kubectl`, `helm`, `python3.12`, `make`.
Recommended host: ≥ 8 vCPU / 16 GB RAM / 40 GB disk (Druid + Flink + Superset + Kafka are the
heavy tenants; a `lite` overlay trims replicas/heap for 8 GB machines).

**GCP (phase 2, human-gated):** a GCP project with billing, `gcloud` authenticated, Terraform, and
a service account with Compute Admin. **A human must enable GCP access / provide keys before this
phase runs.**

---

## 2. Manifest strategy

- **Kustomize** for our own services (`deploy/k3s/apps/*`) with `base/` + overlays `local/` and
  `gcp/`.
- **Helm** for heavy third-party components, values pinned in `deploy/helm-values/`:
  - Kafka — Bitnami Kafka (KRaft, 1 broker locally).
  - Flink — Flink Kubernetes Operator (JobManager + TaskManager) or `flink-kubernetes` session.
  - Druid — Apache Druid Helm chart (micro-quickstart profile locally).
  - Superset — Superset Helm chart (Postgres metadata db, Redis cache).
  - Grafana / Prometheus / Tempo — kube-prometheus-stack + Tempo, or standalone charts.
  - OTel Collector — opentelemetry-collector chart.
  - PostgreSQL, MinIO — Bitnami charts.
- Namespaces: `platform` (our services), `data` (Kafka/Flink/Druid/Superset/PG/MinIO),
  `observability` (OTel/Prometheus/Tempo/Grafana).
- Storage: local `local-path` (k3s default) in phase 1; `pd-standard`/`pd-balanced` in GCP.
- Ingress: k3s Traefik. Local hostnames via `*.localhost` / port-forward; GCP via the VM's
  external IP + Traefik host rules.

---

## 3. Deploy order (dependency-aware)

`deploy/scripts/deploy-local.sh` applies in waves and waits for readiness between them:

1. Namespaces + secrets + storage.
2. **Data infra:** PostgreSQL, MinIO, Kafka. Wait for Kafka; create topics
   (`sim.iteration.events.v1`, `sim.run.control.v1`, `sim.failure.stats.v1`, `sim.deadletter.v1`).
3. **Observability:** OTel Collector, Prometheus, Tempo, Grafana (+ provisioned dashboards).
4. **Stream/analytics:** Flink (submit failure-stats job), Druid (apply Kafka supervisors),
   Superset (import dashboards).
5. **Platform services:** control-api (run migrations), orchestrator, mcp-simulator-proxy,
   simulation-worker, aggregation-worker, operator-web.
6. Health checks + `print-urls.sh`.

Idempotent: re-running upgrades in place. `make cluster-up && make deploy-local` from scratch on a
clean machine is the phase-1 acceptance path.

---

## 4. Local cluster (`deploy/scripts/cluster-up.sh`)

Creates a k3d cluster with a mapped load-balancer port and a local image registry so
`make images` can push without a remote registry:

```bash
k3d cluster create "$CLUSTER_NAME" \
  --servers 1 --agents 2 \
  --registry-create "$CLUSTER_NAME-registry:0.0.0.0:5001" \
  --port "8080:80@loadbalancer" \
  --k3s-arg "--disable=traefik@server:0"   # if we manage our own ingress; else keep Traefik
```

Images are built by `deploy/scripts/build-images.sh` and pushed to the k3d registry; manifests
reference `k3d-<cluster>-registry:5001/<image>`.

---

## 5. Access & URLs (`print-urls.sh`)

Prints (via ingress host or `kubectl port-forward`):
- operator-web: `http://operator.localhost:8080` (or `:8080/`)
- Grafana: `http://grafana.localhost:8080`
- Superset: `http://superset.localhost:8080`
- Druid console, Flink UI, Kafka UI (optional dev tools).

operator-web is configured (via `/config.js`) with the Grafana/Superset URLs so its Observability
tabs and per-run deep links resolve to these hosts.

---

## 6. Secrets

Phase 1: `deploy/scripts/deploy-local.sh` creates k8s Secrets from a local `.env` (git-ignored;
`.env.example` checked in). Nothing sensitive is committed. Superset/Grafana/Postgres/MinIO
credentials are generated on first deploy.

Phase 2 (GCP): secrets sourced from **GCP Secret Manager**; the VM's service account reads them at
boot. No secrets in Terraform state or images.

---

## 7. Phase 2 — GCP VM + k3s (Terraform)

`infra/terraform/gcp/` provisions:
- A **Compute Engine VM** (e.g., `e2-standard-8`, Ubuntu LTS) with a persistent disk sized for
  Druid/Kafka.
- Firewall rules (SSH from operator IP; HTTP/HTTPS; internal).
- A **startup script / cloud-init** that installs k3s single-node, installs Helm, and clones this
  repo to run `deploy/scripts/deploy-local.sh` (renamed target reused via the `gcp` overlay).
- Optional static external IP + DNS.
- Outputs: external IP, kubeconfig fetch command, dashboard URLs.

**Gating:** this module is inert until a human enables the GCP project, billing, APIs
(`compute.googleapis.com`), and supplies a service-account key / `gcloud` auth. The Terraform is
written and reviewed in phase 1 but **not applied** until then. `terraform plan` in CI can validate
syntax without credentials.

Blue/green and canary strategies from `06_CICD_AND_DELIVERY_GUIDE.md` §6 apply to the stateless
services (control-api, operator-web, orchestrator); stateful components (Kafka, Druid, Postgres)
use backward-compatible migrations and version-pinned workers per run.

---

## 8. Resource profiles

| Overlay | Kafka | Flink TM | Druid | Superset | Use |
|---|---|---|---|---|---|
| `lite` | 1×512Mi | 1×1Gi | micro-quickstart | 1 replica | 8 GB laptop |
| `local` | 1×1Gi | 2×2Gi | small | 1 replica | 16 GB laptop |
| `gcp` | 1×2Gi | 2×4Gi | small/medium | 2 replicas | GCP VM |

---

## 9. Teardown

`make cluster-down` deletes the k3d cluster (and its registry). GCP: `terraform destroy` in
`infra/terraform/gcp/`.
