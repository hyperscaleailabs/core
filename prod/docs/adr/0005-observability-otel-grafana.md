# ADR-0005: OpenTelemetry + Grafana for operational observability

**Status:** Accepted · **Date:** 2026-07-24

## Context
The product spec and diagram show **OTel → Grafana** for infra/operational monitoring, distinct
from the Druid/Superset analytical path. Traces must correlate an iteration end-to-end by
experiment/run/iteration/trajectory/trace IDs (Milestone 3 exit criterion).

## Decision
Instrument all services with the **OpenTelemetry SDK** exporting OTLP to an **OTel Collector**,
which fans out **metrics → Prometheus** and **traces → Tempo**, both visualized in **Grafana**
with provisioned datasources and dashboards (`dashboards/grafana/`).

## Consequences
- Clear separation: Grafana = operational/infra + traces; Superset = experiment analytics.
- `runId`/`traceId` correlation enables jumping from a run to its traces.
- Prometheus + Tempo add footprint; the `lite` overlay trims retention/replicas.
