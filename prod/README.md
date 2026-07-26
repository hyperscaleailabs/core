# Prod

Simulation, evaluation, release, and observability.

Release stages: pre-release simulation with internal dashboard and configuration,
promotion to canary, then ramped-up production. Internal dashboards are gated to
internal use.

| Directory | Component |
|-----------|-----------|
| `ui/` | Frontend |
| `backend/` | Backend services |
| `platform/` | Kafka services, data plane with observability and telemetry, ClickHouse, presentation via Superset and Grafana |

Status: placeholder. Structure and code migrate here in upcoming iterations.
See the root [README](../README.md) for repository rules (public repo: no PII, squash merges, policy checks required).
