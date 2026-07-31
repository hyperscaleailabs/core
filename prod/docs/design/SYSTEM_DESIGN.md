# System Design - Agent Simulation Control Plane

**Status:** Draft for implementation · **Version:** 0.2.0-dev · **Supersedes:** none
**Source of truth for product intent:** [`docs/v0.1.0/01_PRODUCT_REQUIREMENTS.md`](../v0.1.0/01_PRODUCT_REQUIREMENTS.md)
**Architecture reference:** [`assets/architecture.png`](../../assets/architecture.png)

This document defines the target system for the first *functional* implementation: a stack that
runs end-to-end on a local k3s cluster and, in a later batch, on a GCP VM. It makes the technology
choices that [`docs/v0.1.0/09_DECISIONS_AND_OPEN_QUESTIONS.md`](../v0.1.0/09_DECISIONS_AND_OPEN_QUESTIONS.md)
left open. Rationale for each choice is captured as an ADR under [`docs/adr/`](../adr/).

---

## 1. Goals and non-goals for this phase

**In scope (local-k3s batch):**

- Deterministic simulation kernel that executes the four workflow templates (WF-01…WF-04) with
  seeded, replayable dependency outcomes - **no live LLM required** for the golden path.
- Real backend services replacing the browser's in-memory state: control API + PostgreSQL,
  orchestrator, worker pool, MCP simulator/proxy, telemetry adapter.
- Real event backbone: **Kafka (KRaft)** carrying the iteration event envelope.
- Real stream processing: **Apache Flink** computing failure-type statistics in near-real-time.
- Real analytics path: **Druid** ingesting from Kafka, **Superset** dashboards on top.
- Real observability: **OpenTelemetry Collector → Prometheus + Tempo → Grafana**.
- Operator web app that (a) drives experiments and (b) embeds Grafana + Superset as in-panel tabs
  with deep links.
- Full stack deployable to a local **k3d/k3s** cluster with one `make` target, and the golden
  Purchase Ambiguity workflow reproducible (one Blocked run, one corrected Passed run).

**Out of scope for this phase (later batches):**

- Live LLM / real MCP server adapters (boundary preserved; kernel is swappable).
- Production telemetry ingestion and learned failure distributions.
- Automated rollback (recommendation-only).
- Multi-tenancy, SSO/identity, billing.
- Autoscaling beyond a fixed local worker pool.

---

## 2. Planes and service decomposition

The product separates concerns into three planes (see `07_ARCHITECTURE_CONTEXT.md`). This design
maps each plane to concrete services.

### 2.1 Control plane
Owns immutable, versioned configuration and governs releases. **Workers never mutate control
state.**

| Service | Responsibility | Tech |
|---|---|---|
| `control-api` | REST API for experiments, agents, personas, workflows, harnesses, failure profiles, gates, policies, registries; versioning; audit; run metadata; results & decisions. Serves SSE stream to the UI. | Python 3.12, FastAPI, SQLAlchemy, PostgreSQL |
| `gate-engine` (lib) | Deterministic gate evaluation from versioned metrics + gate definitions → release decision. | Python package |

### 2.2 Simulation plane
Executes scenarios and emits telemetry. Consumes immutable config; produces events + artifacts.

| Service | Responsibility | Tech |
|---|---|---|
| `simulation-orchestrator` | Expands a run into N iterations, assigns deterministic seeds + pinned runtime version, dispatches work, tracks run state machine, handles Stop, aggregates final metrics, invokes `gate-engine`. | Python, FastAPI (internal), Postgres, Kafka producer (control topic) |
| `simulation-worker` | Pulls iteration jobs, runs the `simulation-kernel`, applies the harness, emits the iteration event envelope to Kafka and OTel spans, writes trajectory artifacts to MinIO. Horizontally scalable. | Python, Kafka producer, OTel SDK |
| `mcp-simulator-proxy` | MCP-compatible tool endpoint returning outcomes sampled from failure profiles; deterministic per (seed, tool, call index); supports idempotency keys and ambiguous-completion semantics. | Python, FastAPI |
| `simulation-kernel` (lib) | Pure, deterministic execution of workflow templates; failure sampling; cost/latency calculation; seeded replay. Agent-runtime adapter boundary lives here. | Python package |
| `telemetry` (lib) | Event envelope schema (versioned), Kafka + OTel adapters, redaction. | Python package |

### 2.3 Data plane
Transport, streaming, analytics, observability, durable storage.

| Component | Responsibility | Tech |
|---|---|---|
| Event backbone | Durable transport of iteration events + control events. | **Apache Kafka** (KRaft, single broker locally) |
| Stream processor | Near-real-time failure-type statistics, windowed aggregates, feature rows for analytics; dead-letter handling. | **Apache Flink** (`stream/flink-job`) |
| Analytical store | Near-real-time OLAP on iteration/failure events. | **Apache Druid** (Kafka indexing ingestion) |
| Analytics UI | Operator/analyst dashboards and ad-hoc querying. | **Apache Superset** (Postgres metadata db) |
| Traces/metrics pipeline | Collect OTel spans/metrics from services. | **OpenTelemetry Collector** |
| Metrics store | Service + infra metrics. | **Prometheus** |
| Trace store | Distributed traces. | **Tempo** |
| Observability UI | Infra/operational dashboards (throughput, queue lag, worker errors, traces). | **Grafana** |
| Control DB | Config, versions, run metadata, gates, results, audit. | **PostgreSQL** |
| Object storage | Raw/sanitized trajectory artifacts, result JSON exports. | **MinIO** (S3-compatible) |
| `aggregation-worker` (fallback) | Batch aggregation directly from Kafka when Flink/Druid unavailable, so results are never lost (satisfies GW-11). | Python |

---

## 3. Data flow

### 3.1 Happy path (one iteration)
```
control-api            orchestrator            worker                 Kafka
   creates run  ─────►  expand N iters  ─────►  run kernel + harness  ─►  iter.events.v1
   (Postgres)          assign seeds            emit envelope + spans      │
                       dispatch jobs           write artifact ► MinIO     ├─► Flink ─► failure_stats.v1 ─► Druid ─► Superset
                                                                          └─► OTel Collector ─► Prometheus/Tempo ─► Grafana
   run complete ◄──── aggregate metrics ◄──── all iters done ◄───────────┘
   gate-engine → release decision (Passed / Warnings / Manual review / Blocked) → Postgres → SSE ► operator-web
```

### 3.2 Topics (Kafka)
| Topic | Key | Payload | Producers | Consumers |
|---|---|---|---|---|
| `sim.iteration.events.v1` | `runId` | Iteration event envelope (§4.2) | worker | Flink, Druid, aggregation-worker |
| `sim.run.control.v1` | `runId` | run lifecycle (started/stopped/completed) | orchestrator | Flink, UI bridge |
| `sim.failure.stats.v1` | `runId:failureType` | windowed failure-type counts/rates | Flink | Druid, control-api (provisional gates) |
| `sim.deadletter.v1` | `runId` | undecodable/incompatible events | Flink, Druid supervisor | ops/alerting |

### 3.3 Failure isolation rules (from `07_ARCHITECTURE_CONTEXT.md` §8)
- Analytics failure **cannot** erase simulation results: worker persistence to Kafka + MinIO is
  the durable record; Druid/Superset are derived. If Flink/Druid lag, the aggregation-worker can
  replay `sim.iteration.events.v1` to produce final metrics (GW-11).
- Event schemas are versioned (`.v1` suffix) and backward compatible.
- Gate decisions are deterministic from versioned metrics + gate definitions.

---

## 4. Core contracts

These four contracts are stabilized **first** (per `04_IMPLEMENTATION_HANDOFF.md` §7). Canonical
schemas live in `packages/domain`; JSON fixtures in `examples/` are the seed data.

### 4.1 Experiment configuration
Versioned; immutable after a completed run. Fields: workflow template, persona, assistant (+ up
to 5 sub-agents, depth ≤ 2), failure profile(s), harness ref, gate-set ref, execution settings
(iterations, parallelism, seed strategy, cached resources), baseline/candidate versions, owner,
tags. See [`examples/purchase_ambiguity_experiment.json`](../../examples/purchase_ambiguity_experiment.json).

### 4.2 Iteration event envelope
Emitted per event within an iteration. Correlation IDs: `experimentId`, `experimentVersion`,
`runId`, `iteration`, `trajectoryId`, `traceId`, `spanId`, `sessionId`, `requestId`, `seed`,
`timestamp`. Body: `workflowStage`, `component`, `promptVersion`, `model`, `tool`, `toolInput`,
`sanitizedOutput`, `rawOutputRef` (MinIO pointer, redacted from stream), `processedOutput`,
`validationStatus`, `failureClassification`, `retryCount`, `tokens`, `costUsd`, `latencyMs`,
`outcome`. This is the **single schema** Kafka, Flink, and Druid agree on.

### 4.3 Gate result
`{ metric, scope, actualValue, threshold, operator, severity, sampleSize, result, relatedTrajectoryIds[] }`.
See [`examples/transaction_release_gates.json`](../../examples/transaction_release_gates.json).

### 4.4 Release decision
`{ status, explanations[], blockingGates[], warnings[], reviewGates[], versionIdentifiers,
reproducibilityMetadata }`. Status ∈ {Passed, Passed with warnings, Manual review, Blocked},
computed by rule in §5.

---

## 5. Gate evaluation & decision rule

`gate-engine` is a pure function `evaluate(metrics, gateSet) -> ReleaseDecision`:

1. For each gate, compute `result` by comparing `actualValue` to `threshold` via `operator`.
2. A gate that fails contributes at its `severity`: `blocking`, `manual_review`, or `warning`.
3. Decision precedence (GW-12, GW-13):
   - Any failed **blocking** gate → **Blocked**.
   - Else any failed **manual_review** gate → **Manual review**.
   - Else any failed **warning** gate → **Passed with warnings**.
   - Else → **Passed**.
4. Minimum-sample-size gate guards against deciding on too-few iterations.
5. Every gate carries `relatedTrajectoryIds` so the decision links to evidence.

Determinism requirement: identical `(metrics, gateSet)` always yields identical decision. This
function is unit-tested against GW-01, GW-02, GW-12, GW-13.

---

## 6. Determinism & replay

- Each iteration has a stored `seed` and a pinned `runtimeVersion` (worker image digest).
- The kernel derives all stochastic choices (tool outcome, latency sample, business outcome) from
  a seeded RNG keyed by `(seed, stage, tool, callIndex)` so **same-seed replay reproduces
  dependency outcomes** (GW-03) and **new-seed replay may differ** (GW-04) while config is
  unchanged.
- The `mcp-simulator-proxy` is stateless w.r.t. randomness: given the same seed + call sequence it
  returns the same outcomes. Idempotency keys are honored so a safe retry does not double-charge.
- Completed-run configs are immutable; editing offers Clone-and-Modify with lineage (GW-09).

---

## 7. Simulation kernel & the four workflows

The kernel implements WF-01 (linear), WF-02 (hierarchical depth-1), WF-03 (router depth-2),
WF-04 (transactional MCP). The **golden path is WF-04 / Purchase Ambiguity**:

- **Unsafe (GW-01):** `make_purchase → timeout → make_purchase` with a fresh idempotency key →
  `duplicate_transaction_risk` policy violation → **Blocked**.
- **Safe (GW-02):** timeout classified as `ambiguous_transaction` → recovery calls
  `transaction_status` before any repeat; retries reuse the original idempotency key → zero policy
  violations → blocking gates pass → **Passed / Passed with warnings**.

The kernel exposes an **agent-runtime adapter** interface. For this phase the adapter is the
deterministic simulator. A later phase swaps in a model-gateway adapter without changing the
kernel's contract (preserves the MVP-to-production substitution map, `07_…` §9).

---

## 8. Flink failure-statistics job

`stream/flink-job` consumes `sim.iteration.events.v1` and produces near-real-time **failure-type
statistics** (the explicit requirement). Minimum viable job:

- Filter events with `outcome ∈ {failed, recovered}` or non-null `failureClassification`.
- Keyed by `(runId, failureClassification)`, tumbling + sliding windows (e.g., 5s tumbling for
  live UI, 1m sliding for trend).
- Emit counts, rate = failures / completed iterations, P50/P95/P99 latency per failure type,
  retry rate, and duplicate-transaction-risk count to `sim.failure.stats.v1`.
- These rows feed (a) Druid for Superset dashboards and (b) control-api provisional gates in the
  live monitor.
- Dead-letter malformed/incompatible events to `sim.deadletter.v1`.

Implementation is Flink SQL (Kafka connector) where sufficient; PyFlink/DataStream where custom
classification is needed. Job is packaged as an image and submitted to the Flink JobManager.

---

## 9. Analytics: Druid + Superset

- **Druid** runs a Kafka indexing supervisor on `sim.iteration.events.v1` (rollup by minute) and
  `sim.failure.stats.v1`. Ingestion specs live in `ingestion/druid/`.
- **Superset** connects to Druid (SQL) and ships pre-built dashboards in `dashboards/superset/`:
  Experiment Overview, Failure-Type Breakdown, Cost vs Reliability, Latency Distribution,
  Baseline-vs-Candidate. Dashboards are exported as importable assets and provisioned on deploy.

## 10. Observability: OTel + Grafana

- All services export OTLP to the **OTel Collector**. Collector fans out metrics → **Prometheus**,
  traces → **Tempo**.
- **Grafana** provisions datasources (Prometheus, Tempo, and Druid for cross-panels) and
  dashboards in `dashboards/grafana/`: Service Health, Kafka/Consumer Lag, Worker Throughput &
  Errors, Trace Explorer, Run-in-Progress. Correlation is by `traceId`/`runId`.

## 11. Operator web app & embedded dashboards

`services/operator-web` evolves from the v0.1.0 HTML MVP. New for this phase: an **Observability**
section in the primary nav with **in-panel tabs** (Grafana / Superset) rendered as iframes, plus
**deep links** ("Open in Grafana", "Open in Superset") from a run/result to the pre-filtered
dashboard for that `runId`. This satisfies the requirement that the simulation dashboard has
clickable links that open the dashboards or feature them as tabs. Config (dashboard base URLs) is
injected at deploy time, not hard-coded.

---

## 12. Storage model (PostgreSQL, high level)

`experiments`, `experiment_versions` (immutable), `agents`, `personas`, `workflows`, `harnesses`,
`failure_profiles`, `gate_sets`, `policies`, `runs`, `iterations`, `results`, `gate_results`,
`release_decisions`, `audit_log`. Large payloads (raw trajectories, exports) are pointers to
MinIO objects. Migrations are versioned (Alembic).

---

## 13. Deployment & delivery

Full stack targets a Kubernetes cluster. **Phase 1** is local **k3d/k3s**; **Phase 2** provisions
a **GCP VM + k3s via Terraform** and rolls the identical manifests. See
[`DEPLOYMENT.md`](DEPLOYMENT.md) and [`CICD_STRATEGY.md`](CICD_STRATEGY.md). CI/CD is integrated
with the simulator itself: the golden Purchase Ambiguity workflow runs in CI, and the release
decision JSON becomes a machine-readable check (advisory first, per `06_…` §5).

---

## 14. Key rules preserved from the product spec

- Completed runs reference immutable config versions; workers consume versioned config.
- Tool authorization is enforced outside the model (in the proxy/policy layer).
- Raw sensitive data is redacted before telemetry emission; raw output stays in MinIO behind
  access control.
- No private chain-of-thought is exposed in trajectories - only operational summaries, tool calls,
  validations, and recovery actions.
- Analytics failure cannot erase results; telemetry can be buffered and replayed.

---

## 15. Open decisions deferred (tracked as ADRs / issues)

- Model-gateway abstraction (phase 2+). ADR-0006 records the deterministic-kernel-first choice.
- Druid vs ClickHouse at larger scale - Druid chosen now (ADR-0004); revisit on cost/scale.
- Temporal for durable orchestration - deferred; queue + Postgres state machine for now (ADR-0006).
- Learned-distribution review workflow - phase 3+.
