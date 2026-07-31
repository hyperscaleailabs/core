# Implementation Spec - Agent Simulation Control Plane

**Version:** 0.2.0-dev · **Companion to:** [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md),
[`DEPLOYMENT.md`](DEPLOYMENT.md), [`CICD_STRATEGY.md`](CICD_STRATEGY.md),
[`BACKLOG.md`](BACKLOG.md)

This spec is concrete enough to implement PR-by-PR. Each section maps to one or more backlog
items / GitHub issues. Where the product spec already dictates behavior, it is cited rather than
repeated.

---

## 1. Tech stack & conventions

- **Language:** Python 3.12 for all backend services and libs (repo already uses `ruff` + `pytest`).
  Rationale in [ADR-0001](../adr/0001-language-and-runtime.md).
- **Web framework:** FastAPI + Uvicorn. **ORM:** SQLAlchemy 2.x + Alembic. **Validation:** Pydantic v2.
- **Async messaging:** `aiokafka` (or `confluent-kafka`) producers/consumers.
- **Telemetry:** `opentelemetry-sdk` + OTLP exporter.
- **Frontend:** the v0.1.0 static HTML MVP served by nginx, incrementally wired to the API; new
  Observability tabs added as iframes. (A framework rewrite is explicitly out of scope for phase 1.)
- **Packaging:** each `services/*` and `packages/*` has its own `pyproject.toml`; a root workspace
  ties them together. Shared libs are installed editable into services.
- **Lint/format/type:** `ruff` (lint+format), `mypy` (strict on `packages/`), `pytest` (+`pytest-cov`).
- **Containers:** one `Dockerfile` per service; multi-stage, non-root, pinned base
  (`python:3.12-slim`). Images published to GHCR.
- **Config:** 12-factor env vars; no secrets in images or experiment configs (`06_…` §9). Local
  secrets via k8s Secrets created by the deploy script; GCP via Secret Manager (phase 2).

### Directory contract
```
packages/domain           pydantic models + JSON-schema export for the 4 core contracts
packages/gate-engine      pure evaluate(metrics, gateSet) -> ReleaseDecision
packages/simulation-kernel deterministic WF-01..WF-04 execution + failure sampling + replay
packages/telemetry        event envelope, kafka adapter, otel adapter, redaction
services/control-api      REST + SSE, Postgres, registries, versioning, results
services/simulation-orchestrator  run expansion, dispatch, run state machine, final aggregation
services/simulation-worker        iteration executor -> Kafka + OTel + MinIO
services/mcp-simulator-proxy      MCP-compatible failure-injecting tool endpoint
services/telemetry-adapter        (optional) bridges/normalizes if worker doesn't emit directly
services/aggregation-worker       Kafka -> metrics fallback when Flink/Druid lag
services/operator-web             nginx-served UI + observability tabs config
stream/flink-job                  failure-type statistics job (SQL + PyFlink)
ingestion/druid                   supervisor specs
dashboards/{superset,grafana}     dashboards + provisioning
deploy/k3s                        kustomize bases/overlays + helm values
infra/terraform/gcp               phase-2 VM + k3s
```

---

## 2. `packages/domain` - core schemas (do first)

Pydantic models + `model_json_schema()` export for:

- `ExperimentConfig`, `ExperimentVersion` (immutable), `Persona`, `AssistantAgent`, `SubAgent`,
  `WorkflowTemplate` (enum WF-01..04), `FailureProfile`, `Harness`, `GateSet`, `Gate`, `Policy`.
- `IterationEventEnvelope` (§4.2 of SYSTEM_DESIGN) - the Kafka/Flink/Druid contract.
- `RunMetrics`, `GateResult`, `ReleaseDecision`.

**Acceptance:** the fixtures in `examples/` validate against these models round-trip; JSON schemas
are exported to `packages/domain/schemas/` and checked in CI for backward compatibility.

---

## 3. `packages/simulation-kernel` - deterministic engine

- `run_iteration(config, seed) -> (Trajectory, list[IterationEvent], IterationMetrics)`.
- Seeded RNG keyed by `(seed, stage, tool, callIndex)`; failure outcomes sampled from
  `FailureProfile.outcomes`; latency from the configured distribution (fixed/uniform/normal/percentile).
- `AgentRuntimeAdapter` protocol; `DeterministicAdapter` is the phase-1 implementation.
- Harness runtime: input/schema/semantic/policy validation, failure classification, bounded retry,
  recovery policies (from `transaction_safety_harness.json`), idempotency-key handling.
- Cost/latency accounting per event.

**Golden behavior (must be unit-tested):** GW-01 (unsafe retry → duplicate risk), GW-02 (safe
recovery via `transaction_status`), GW-03 (same-seed replay stable), GW-04 (new-seed differs),
GW-05 (linear passes), GW-08 (probabilities must total 100%).

---

## 4. `packages/gate-engine`

Pure `evaluate(metrics: RunMetrics, gate_set: GateSet) -> ReleaseDecision` implementing the §5
decision rule of SYSTEM_DESIGN. Unit tests cover GW-12 (severity precedence) and GW-13 (policy
blocks despite high success). No I/O, no globals.

---

## 5. `packages/telemetry`

- `IterationEventEnvelope` serialization (JSON, schema-versioned key `schemaVersion: "1"`).
- `KafkaEmitter` (topic `sim.iteration.events.v1`, key=`runId`).
- `OtelTracer` helper producing spans with `runId`/`iteration`/`trajectoryId` attributes and
  `traceId` propagation.
- `redact()` - strips secrets / raw sensitive fields before emission; raw output is stored to MinIO
  and referenced by `rawOutputRef`.

---

## 6. `services/control-api`

REST (OpenAPI-generated) + SSE. Endpoints (v1):

```
POST   /experiments                 create draft
POST   /experiments/{id}/versions   freeze immutable version
GET    /experiments/{id}
POST   /experiments/{id}/clone      clone-and-modify (lineage)
GET/POST /agents /personas /workflows /harnesses /failure-profiles /gate-sets /policies
POST   /runs                        start run (delegates to orchestrator)
POST   /runs/{id}/stop              graceful stop (GW-10)
GET    /runs/{id}                   run state + provisional metrics
GET    /runs/{id}/events            SSE live stream (from Kafka bridge / failure.stats)
GET    /runs/{id}/result            final ReleaseDecision + scorecard
GET    /runs/{id}/result/export     signed result JSON (GW-14)
GET    /trajectories/{id}           operational tree (no chain-of-thought)
GET    /observability/links?runId=  deep links to Grafana/Superset for a run
```

- Persistence via SQLAlchemy + Alembic migrations.
- Immutability enforced at the version/run boundary; edits on completed runs return 409 + offer
  clone (GW-09).
- Validation gate GW-08: reject failure profiles whose enabled probabilities ≠ 100% at the API,
  not only in the UI.
- SSE stream is fed by a Kafka consumer bridge subscribing to `sim.run.control.v1` and
  `sim.failure.stats.v1`.

---

## 7. `services/simulation-orchestrator`

- `POST /runs`: load immutable experiment version, expand into N iteration jobs with deterministic
  seeds and pinned worker image digest, enqueue (Kafka work topic or DB-backed queue), emit
  `run.started` to `sim.run.control.v1`.
- Run state machine: `Ready → Running → Analyzing → {Passed|Warnings|Manual review|Blocked}`.
- Stop (GW-10): stop dispatch, let in-flight finish or cancel per policy, mark queued as
  `cancelled` (not `failed`), keep completed evidence queryable.
- Final aggregation: when all iterations terminal, compute `RunMetrics` (prefer Flink/Druid
  rollups; fall back to `aggregation-worker` if analytics lags - GW-11), call `gate-engine`,
  persist `ReleaseDecision`, emit `run.completed`.

---

## 8. `services/simulation-worker`

- Consume iteration jobs; for each: `simulation-kernel.run_iteration(config, seed)`.
- Tool calls go to `mcp-simulator-proxy` over HTTP (MCP-compatible) so failure injection and
  idempotency are centralized and observable.
- Emit each event via `telemetry.KafkaEmitter` + OTel spans; write full trajectory artifact to
  MinIO; emit `iteration_result`.
- Bounded execution: enforce harness bounds (retries, steps, tokens, cost, duration).
- Horizontally scalable (Deployment `replicas`); parallelism from experiment `execution.parallelism`.

---

## 9. `services/mcp-simulator-proxy`

- MCP-compatible tool endpoints: `check_inventory`, `check_balance`, `make_purchase`,
  `transaction_status`, plus knowledge/profile/inventory/reservation/transfer/notification/etc.
- Outcome sampled deterministically from the run's failure profile keyed by `(seed, tool, callIndex)`.
- `make_purchase` supports idempotency keys and the `ambiguous_completion` / `timeout` outcomes;
  `transaction_status` reflects the true underlying state so the safe harness can recover (GW-02).
- Tool authorization enforced here (outside the model); scope violations recorded as policy
  violations (GW-07, GW-13).

---

## 10. `stream/flink-job` - failure-type statistics

Per SYSTEM_DESIGN §8. Deliver:
- `sql/failure_stats.sql` - Kafka source `sim.iteration.events.v1`, windowed aggregation by
  `(runId, failureClassification)`, sink `sim.failure.stats.v1`.
- `pyflink/job.py` - packaging + submission for any custom classification logic.
- Dead-letter to `sim.deadletter.v1`.
- Local submission via a `flink run` Job resource in `deploy/k3s`.

**Acceptance:** during the golden run, `sim.failure.stats.v1` shows a non-zero
`duplicate_transaction_risk` count for the unsafe config and zero for the safe config.

---

## 11. Druid ingestion & Superset dashboards

- `ingestion/druid/iteration_events_supervisor.json` and `failure_stats_supervisor.json` (Kafka
  indexing service, minute rollup, dimensions = correlation IDs + failure type, metrics = count,
  cost, latency quantiles).
- `dashboards/superset/*` exported assets: Experiment Overview, Failure-Type Breakdown, Cost vs
  Reliability, Latency Distribution, Baseline-vs-Candidate. Imported at deploy time via
  `superset import-dashboards`.

## 12. Grafana + OTel

- `deploy/k3s/components/otel` - Collector config (OTLP in; Prometheus + Tempo out).
- `dashboards/grafana/*` - provisioned datasources + dashboards (Service Health, Kafka Lag, Worker
  Throughput/Errors, Trace Explorer, Run-in-Progress). Alerts for stuck runs, lost telemetry,
  gate-engine errors (`06_…` §10).

## 13. `services/operator-web`

- Serve the existing HTML; inject a runtime config (`/config.js`) with Grafana + Superset base URLs.
- Add an **Observability** nav section with **tabs** (Grafana | Superset) as iframes and per-run
  **deep links** built from `/observability/links?runId=`.
- Keep the deterministic demo working offline; live data appears when the API is reachable.

---

## 14. Golden end-to-end test (the definition of "done" for phase 1)

`tests/e2e/test_purchase_ambiguity.py`:
1. Load `examples/purchase_ambiguity_experiment.json`; run 100–1000 iterations with the **basic
   retry** harness against the deployed stack (or an in-process harness in CI). Assert decision =
   **Blocked** and a linked trajectory contains `make_purchase → timeout → make_purchase` with a
   `duplicate_transaction_risk` policy violation (GW-01).
2. Swap in `examples/transaction_safety_harness.json`, rerun same seeds. Assert zero duplicate
   policy violations, blocking gates pass, decision = **Passed / Passed with warnings** (GW-02).
3. Assert `sim.failure.stats.v1` / Druid reflect the failure-type counts.
4. Assert exported result JSON matches displayed result and redacts sensitive data (GW-14).

CI runs steps 1–2 in-process (fast, no cluster); a nightly / on-demand job runs the full deployed
variant on an ephemeral k3d cluster.

---

## 15. Definition of done (per PR)

Every PR carries the evidence bundle from `04_IMPLEMENTATION_HANDOFF.md` §9 where applicable:
build, tests, coverage, lint/type, schema-compat, security scan, screenshots for UI changes,
golden result JSON, and trace/log evidence for one success / one recovery / one failure.
