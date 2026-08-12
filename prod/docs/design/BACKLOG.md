# Implementation Backlog - Agent Simulation Control Plane

**Version:** 0.2.0-dev · **Companion to:** [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md),
[`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md)

Prioritized, dependency-ordered backlog. Every item below is mirrored as a GitHub issue with the
same `ASC-###` id and grouped by milestone. Priorities: **P0** = required for phase-1 done, **P1**
= required for the full local-k3s stack, **P2** = hardening / phase-2.

**Phase-1 "done" line:** M0–M5 complete → the full stack (services + Kafka + Flink + Druid +
Superset + OTel + Grafana) runs on a local k3d/k3s cluster and the Purchase Ambiguity golden
workflow reproduces a **Blocked** run and a corrected **Passed** run end-to-end.

**Phase-2 (human-gated):** M7 - GCP VM + k3s via Terraform. Blocked until a human enables GCP
access / keys.

Legend: dep = depends on · GW = golden workflow test case in `docs/v0.1.0/08_…`.

---

## Milestone M0 - Foundations & contracts  *(P0)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-001 | Repo scaffolding, workspace tooling, root Makefile | P0 | - | monorepo layout, ruff/mypy/pytest configured, `make help` works |
| ASC-002 | `packages/domain`: pydantic models + JSON-schema export for the 4 core contracts | P0 | 001 | `examples/*.json` validate round-trip; schemas exported + checked in |
| ASC-003 | `packages/gate-engine`: `evaluate()` + decision rule | P0 | 002 | GW-12, GW-13 unit tests pass; pure function, no I/O |
| ASC-004 | `packages/simulation-kernel`: deterministic WF-04 + failure sampling + replay | P0 | 002 | GW-01, GW-02, GW-03, GW-04 unit tests pass |
| ASC-005 | `packages/telemetry`: event envelope + kafka/otel adapter interfaces + redaction | P0 | 002 | envelope serializes; redaction unit-tested |
| ASC-006 | CI `ci.yml`: lint, type, test, schema-compat, security, container build | P0 | 001 | PR pipeline green on scaffold |
| ASC-007 | Base Dockerfiles + `build-images.sh` | P0 | 001 | all service images build locally |

## Milestone M1 - Golden workflow, API-driven (deterministic)  *(P0)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-010 | `control-api`: experiments/versions/runs CRUD + Postgres + Alembic + immutability | P0 | 002 | GW-09 (immutable completed config, clone-and-modify) |
| ASC-011 | `control-api`: failure-profile probability validation at the API | P0 | 010 | GW-08 (probabilities must total 100%; API rejects) |
| ASC-012 | `simulation-orchestrator`: run expansion, seeds, state machine, Stop | P0 | 010,004 | GW-10 (stop preserves evidence; queued → cancelled) |
| ASC-013 | `simulation-worker`: iteration executor via kernel (in-process emit first) | P0 | 004,005 | 100+ iterations execute within bounds |
| ASC-014 | `mcp-simulator-proxy`: MCP tools + idempotency + ambiguous completion + tool authz | P0 | 004 | GW-07 (scope violation blocked); idempotency honored |
| ASC-015 | `control-api`: results + release decision + export JSON + SSE | P0 | 003,012 | GW-14 (export matches display, redacted) |
| ASC-016 | `tests/e2e`: Purchase Ambiguity Blocked→Passed (in-process) | P0 | 012,013,014,015 | GW-01 + GW-02 reproducible in CI |
| ASC-017 | `aggregation-worker`: metrics fallback | P1 | 013 | GW-11 (results durable if analytics lags) |

## Milestone M2 - Event backbone & telemetry  *(P1)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-020 | Kafka (KRaft) Helm values + topic bootstrap | P1 | - | 4 topics created; broker healthy on k3d |
| ASC-021 | Worker → Kafka real emission of iteration events | P1 | 013,020 | events land on `sim.iteration.events.v1` |
| ASC-022 | OTel instrumentation across services (traces + metrics) | P1 | 013 | one iteration traceable end-to-end by ids |
| ASC-023 | MinIO + trajectory artifact storage + `rawOutputRef` | P1 | 013 | raw output in MinIO, redacted from stream |
| ASC-024 | control-api SSE fed by Kafka bridge (control + failure.stats) | P1 | 020,015 | live monitor updates from real topics |

## Milestone M3 - Streaming & analytics  *(P1)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-030 | Flink job: failure-type statistics (SQL) → `failure.stats` + dead-letter | P1 | 021 | non-zero `duplicate_transaction_risk` on unsafe run, zero on safe |
| ASC-031 | Flink deployment (operator/session) + job submission | P1 | 020,030 | job runs on cluster; restarts cleanly |
| ASC-032 | Druid: Kafka indexing supervisors (events + failure stats) | P1 | 021,030 | data queryable in Druid within seconds |
| ASC-033 | Superset: datasource + 5 dashboards export/import | P1 | 032 | dashboards render golden-run data |
| ASC-034 | Provisional gates in live monitor from `failure.stats` | P2 | 030,024 | provisional gate values update during a run |

## Milestone M4 - Observability (OTel + Grafana)  *(P1)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-040 | OTel Collector deploy (OTLP → Prometheus + Tempo) | P1 | 022 | services export; collector healthy |
| ASC-041 | Prometheus + Tempo deploy | P1 | 040 | metrics + traces stored |
| ASC-042 | Grafana deploy + provisioned datasources + dashboards + alerts | P1 | 041 | 5 dashboards + alerts for stuck runs / lost telemetry / gate errors |
| ASC-043 | operator-web: Observability tabs (Grafana/Superset iframes) + per-run deep links | P1 | 033,042 | tabs render; "Open in Grafana/Superset" deep-links per `runId` |

## Milestone M5 - Local k3s deployment (full stack e2e)  *(P0 for phase-1 done)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-050 | `cluster-up.sh`: k3d cluster + local registry | P0 | - | `make cluster-up` yields a ready cluster |
| ASC-051 | Kustomize base + `local`/`lite` overlays for our services | P0 | 007 | `kubectl apply -k` deploys services |
| ASC-052 | `deploy-local.sh`: wave orchestration + readiness gates | P0 | 020,031,032,033,040,051 | `make deploy-local` brings the full stack up idempotently |
| ASC-053 | `print-urls.sh` + Traefik ingress host rules | P0 | 052 | operator-web/Grafana/Superset reachable |
| ASC-054 | Deployed golden workflow e2e on k3d | P0 | 052,016 | full deployed Blocked→Passed run passes |
| ASC-055 | `.env.example` + secret bootstrap | P0 | 052 | no secrets in repo; deploy creates them |

## Milestone M6 - CI/CD hardening  *(P2)*

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-060 | `images.yml`: GHCR publish + SBOM + provenance | P2 | 006,007 | images pushed on `main` with SBOM |
| ASC-061 | `e2e-k3d.yml`: nightly deployed golden workflow | P2 | 054 | ephemeral k3d run green nightly |
| ASC-062 | Simulator-as-a-check: `release-decision.json` artifact + PR comment | P1 | 016 | PR shows the golden run's release decision |
| ASC-063 | Security scans (pip-audit, gitleaks, trivy, bandit/semgrep) | P2 | 006 | scans wired into CI |
| ASC-064 | Issue/PR templates + CODEOWNERS + branch-protection docs | P2 | - | templates + CODEOWNERS present |

## Milestone M7 - GCP provisioning (phase 2, human-gated)  *(P2)*

> **Blocked** until a human enables the GCP project, billing, APIs, and provides credentials.

| ID | Title | Prio | Dep | Acceptance |
|---|---|---|---|---|
| ASC-070 | Terraform `gcp`: VM + firewall + disk + cloud-init k3s install | P2 | phase-1 done | `terraform validate` passes; documented |
| ASC-071 | `terraform-validate.yml` (fmt/validate/tflint, no apply) | P2 | 070 | CI validates without credentials |
| ASC-072 | `gcp` overlay + Secret Manager integration | P2 | 070,051 | same manifests deploy on GCP overlay |
| ASC-073 | GCP deploy runbook + human-gating checklist | P2 | 070 | runbook complete; apply steps human-gated |

---

## PR / branch plan (full-auto, one coherent unit per PR)

Trunk-based; each PR is a short-lived branch off `main`, references its issue(s), and carries the
evidence bundle. Recommended order (respecting deps):

| PR | Branch | Issues | Theme |
|---|---|---|---|
| PR-1 | `feat/scaffold-and-ci` | ASC-001, 006, 007, 064 | scaffold, tooling, CI skeleton, templates |
| PR-2 | `feat/domain-contracts` | ASC-002, 005 | domain schemas + telemetry envelope |
| PR-3 | `feat/gate-engine` | ASC-003 | gate engine + decision rule |
| PR-4 | `feat/simulation-kernel` | ASC-004 | deterministic kernel + WF-04 golden logic |
| PR-5 | `feat/control-api` | ASC-010, 011, 015 | control-api + Postgres + results/SSE |
| PR-6 | `feat/orchestrator-worker-proxy` | ASC-012, 013, 014, 017 | orchestrator + worker + MCP proxy + fallback |
| PR-7 | `test/golden-e2e-inprocess` | ASC-016, 062 | in-process golden e2e + simulator-as-a-check |
| PR-8 | `feat/kafka-otel-minio` | ASC-020, 021, 022, 023, 024 | event backbone + telemetry + artifacts |
| PR-9 | `feat/flink-failure-stats` | ASC-030, 031 | Flink failure-type statistics job + deploy |
| PR-10 | `feat/druid-superset` | ASC-032, 033, 034 | Druid ingestion + Superset dashboards |
| PR-11 | `feat/observability-grafana` | ASC-040, 041, 042 | OTel Collector + Prometheus + Tempo + Grafana |
| PR-12 | `feat/operator-web-observability` | ASC-043 | operator-web observability tabs + deep links |
| PR-13 | `feat/local-k3s-deploy` | ASC-050, 051, 052, 053, 055 | k3d + kustomize + deploy orchestration |
| PR-14 | `test/deployed-golden-e2e` | ASC-054, 061 | deployed golden workflow + nightly CI |
| PR-15 | `chore/security-images` | ASC-060, 063 | GHCR/SBOM + security scans |
| PR-16 | `feat/gcp-terraform` *(phase 2)* | ASC-070, 071, 072, 073 | GCP VM + k3s Terraform (human-gated apply) |

PRs 1–14 deliver phase-1 done. PR-15 hardens. PR-16 is written in phase 1, applied in phase 2.
