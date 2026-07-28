# Prod

Simulation, evaluation, release, and observability: the **Agent Simulation Control
Plane**, a pre-production control plane for testing non-deterministic AI agents and
multi-agent workflows under production-like failure conditions.

Operators configure personas, agents, tools, probabilistic failures, validation and
recovery harnesses, and release gates; run repeated stochastic simulations; inspect
telemetry and trajectories; and receive an explainable **release decision** - Passed,
Passed with warnings, Manual review, or Blocked. The release decision is one required
check, never the sole authorization.

This is the module that makes the axis guardrail *"learned policies and language models
propose; deterministic supervisors dispose"* executable: the gate engine is the
deterministic supervisor, and every release decision it emits is reproducible from a
seed.

Acceptance criteria template for projects touching this subproject:
[ACCEPTANCE.md](ACCEPTANCE.md).

All command examples in this subproject's docs are written relative to `prod/` - run
them from this directory (`cd prod`), not the repo root.

## The three planes

The root [README](../README.md#subprojects) describes this module as `ui/`, `backend/`,
and `platform/`. Those are **roles**, not directories: the project was integrated with
its own internal structure intact, and each role maps onto real paths below.

| Role | What it is | Where it lives |
|------|-----------|----------------|
| **ui** | Operator console: live runs, explainable gate scorecard, embedded Grafana and Superset tabs; the v0.1.0 MVP is kept as a design reference at `/mvp` | [`services/operator-web/`](services/operator-web/README.md), `app/` |
| **backend** | Control API, orchestrator, simulation worker, MCP simulator proxy, aggregation worker, and the four shared contract packages | `services/`, `packages/` |
| **platform** | Kafka event backbone, Flink stream processing, ClickHouse OLAP, Superset and Grafana presentation, OTel collection, and the cluster manifests that assemble them | [`stream/flink-job/`](stream/flink-job/README.md), [`ingestion/druid/`](ingestion/druid/README.md), `dashboards/`, [`deploy/k3s/`](deploy/k3s/base/README.md) |

## Architecture

```text
Simulation plane                Data plane                          Observability
-----------------               --------------------------          -----------------
control-api (FastAPI)           Kafka (KRaft) -- Flink SQL job       OTel Collector
orchestrator                      |  failure-type statistics           |
simulation-worker  -- events -->  +-> ClickHouse -> Superset           +-> Prometheus -> Grafana
mcp-simulator-proxy               +-> (dead-letter / replay)           +-> Tempo ------>  (embedded
harness runtime                 MinIO (trajectory artifacts)                             in operator-web)
```

Analytics is **derived**: Kafka and the artifact store are the durable record, and no
analytics failure can erase a run's result. That invariant is what makes the aggregation
worker (a Kafka-to-metrics fallback path) part of the design rather than a redundancy.

## Layout

| Path | Purpose |
|------|---------|
| `packages/domain/` | Pydantic contracts (experiment config, iteration event envelope, gate result, release decision) plus JSON-schema export |
| `packages/gate-engine/` | Pure `evaluate(metrics, gate_set) -> ReleaseDecision`, including provisional gates |
| `packages/simulation-kernel/` | Deterministic workflow execution, seeded failure sampling, replay, harness runtime |
| `packages/telemetry/` | Event envelope, Kafka and null emitters, OTel tracing, redaction, artifact stores |
| `services/control-api/` | FastAPI surface: experiments, runs, results, SSE, observability links |
| `services/simulation-orchestrator/` | Run expansion, state machine, stop handling, aggregation |
| `services/simulation-worker/` | Iteration executor: kernel + emitter + tracer + artifact store |
| `services/mcp-simulator-proxy/` | MCP tools, idempotency, tool authorization |
| `services/aggregation-worker/` | Kafka-to-metrics fallback so durability never depends on analytics |
| `services/operator-web/` | nginx: live console, the v0.1.0 MVP at `/mvp`, `/api` proxy, observability tabs |
| `stream/flink-job/` | Flink SQL failure-statistics job plus a tested Python reference implementation |
| `ingestion/druid/` | Druid ingestion specs (x86 path; ClickHouse is the arm64 store) |
| `dashboards/` | Superset and Grafana dashboards and provisioning |
| `deploy/` | Dockerfiles, kustomize base and overlays, Helm values, component manifests, wave scripts |
| `infra/terraform/gcp/` | Phase-2 VM and k3s provisioning, written and CI-validated; apply is human-gated |
| `examples/`, `tests/`, `artifacts/golden/` | Golden fixtures, e2e tests, and recorded release decisions |
| `docs/` | Design docs, ADRs, evidence, lessons, articles, and the v0.1.0 product specs |

## Quick start (local k3d)

```bash
cd prod
make cluster-up      # create the local k3d cluster
make images          # build service container images
make deploy-local    # deploy the stack
make e2e             # golden Purchase Ambiguity workflow, end to end
make urls            # print operator-web / Grafana / Superset / Flink URLs
```

On memory-constrained hosts use `bash deploy/scripts/deploy-lite.sh` instead of
`make deploy-local`; it skips the heaviest tenants and is what the arm64 evidence in
`docs/evidence/` was collected on. Teardown is `make cluster-down`.

The checks that need no cluster - lint, unit tests, schema compatibility, and the
in-process golden workflow - run directly:

```bash
cd prod
make verify && make lint && make test && make e2e
```

## Reviewing a running stack

Everything a reviewer needs, in three commands:

```bash
cd prod
make urls          # discovers the published port and prints what is reachable
make dashboards    # holds Grafana / Superset / Flink / ClickHouse open (Ctrl-C to stop)
make evidence      # fresh golden run, then verifies every hop of the chain
```

| Surface | Where | Credentials |
|---------|-------|-------------|
| Operator console | `http://operator.localhost:<lb-port>/` | none |
| v0.1.0 MVP | `http://operator.localhost:<lb-port>/mvp/` | none |
| Control API docs | `http://operator.localhost:<lb-port>/api/docs` | none |
| Grafana (traces) | `http://127.0.0.1:3000` | `admin` / `admin` |
| Superset (analytics) | `http://127.0.0.1:8088` | `admin` / `admin` |
| Flink UI | `http://127.0.0.1:8081` | none |
| ClickHouse | `http://127.0.0.1:8123` | `asc` / `asc` |

`make urls` reads the load-balancer port from the cluster rather than assuming
one, because k3d publishes whichever host port was free. Grafana, Superset,
Flink, and ClickHouse are ClusterIP and only reachable while `make dashboards`
is running; it restarts a forward that drops, since `kubectl port-forward` dies
under the concurrent queries a dashboard fires and the charts then report
"Unexpected error" as though the data were bad.

The credentials above are the local demo defaults committed in the manifests. A
real deployment overrides them from its secret store - see
[Production configuration](../README.md) in the root README.

To walk the golden path by hand: open the console, **Seed golden experiment**,
pick `basic_retry (unsafe)` and **Start run** - expect **Blocked** with three
failing gates - then switch to `transaction_safety (safe)` and re-run for
**Passed**. The run's data reaches Superset within about a minute (Flink uses
5-second processing-time windows; ClickHouse ingests from Kafka continuously),
and its traces appear in Grafana once Tempo flushes its block.

## The golden workflow

The **Purchase Ambiguity** workflow is the invariant across every environment: the same
experiment must produce **Blocked** under the unsafe `basic_retry` harness and **Passed**
under the safe `transaction_safety` harness, in-process and deployed alike. It runs on
every PR as a check and publishes its release decision as evidence - the product gates
its own delivery. Golden cases GW-01 through GW-15 are specified in
[docs/v0.1.0/08_GOLDEN_WORKFLOW_TEST_CASES.md](docs/v0.1.0/08_GOLDEN_WORKFLOW_TEST_CASES.md)
and exist verbatim as tests.

## Where to start

| You are a... | Read this |
|---|---|
| New engineer or architect | [docs/design/SYSTEM_DESIGN.md](docs/design/SYSTEM_DESIGN.md) |
| Implementer | [docs/design/IMPLEMENTATION_SPEC.md](docs/design/IMPLEMENTATION_SPEC.md) |
| DevOps or platform | [docs/design/DEPLOYMENT.md](docs/design/DEPLOYMENT.md) and [docs/design/CICD_STRATEGY.md](docs/design/CICD_STRATEGY.md) |
| Planning or product | [docs/design/BACKLOG.md](docs/design/BACKLOG.md) |
| Looking for decisions | [docs/adr/](docs/adr/) |
| Looking for product intent | [docs/v0.1.0/01_PRODUCT_REQUIREMENTS.md](docs/v0.1.0/01_PRODUCT_REQUIREMENTS.md) |

## How this subproject is developed

All work follows the repository's four-level SDLC ([sdlc/](../sdlc/README.md)); a project
touching `prod/` includes the criteria from [ACCEPTANCE.md](ACCEPTANCE.md) in its
acceptance criteria. CI runs this subproject's checks - static checks, unit tests, the
golden workflow, schema compatibility, deployed-evidence verification, and policy guards -
via `.github/workflows/prod.yml`, path-scoped to `prod/`.

What this project contributed upward, because it is not specific to this module, is the
promotion pipeline and its evidence bundle: [sdlc/PROMOTION.md](../sdlc/PROMOTION.md).
What stayed here is what only this module means: the golden workflow, the gate engine's
decision semantics, and the data and observability planes.

This subproject was integrated from a standalone repository at version
[0.2.0](VERSION); its pre-integration history is summarized in
[docs/design/SDLC_SUMMARY.md](docs/design/SDLC_SUMMARY.md), and the product handoff it
implements is preserved under [docs/v0.1.0/README.md](docs/v0.1.0/README.md).

## Status and known gaps

Phase 1 (local k3s) runs end to end; phase 2 (GCP) is written and CI-validated with a
human-gated apply. Tracked gaps, each with a follow-up ticket recorded in
[docs/design/SDLC_SUMMARY.md](docs/design/SDLC_SUMMARY.md): in-memory control-plane
store, deterministic kernel rather than a live model gateway, Druid deferred to x86, and
ephemeral local storage.

## License

Apache 2.0 - see the root [LICENSE](../LICENSE) and this module's [NOTICE.md](NOTICE.md).
