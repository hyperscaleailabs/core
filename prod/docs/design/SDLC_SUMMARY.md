# SDLC Summary — Agent Simulation Control Plane

**Version:** 0.2.0 · **Date:** 2026-07-25 · **Repo:**
`hyperscaleailabs/ai-multi-agent-simulation-eval-observability`

This document records the full software-development lifecycle for turning the v0.1.0 product handoff
into a working, locally-deployed system, and defines the path to production on GCP. It is intended
as a **reusable template for an automated SDLC**: each stage names its inputs, decisions, artifacts,
and the tickets/PRs that produced them. Sections marked _[placeholder]_ are stubs to expand.

Grounding data: **36 commits, 15 merged PRs (#45–#69), 51 delivery issues (ASC-001…087) across
milestones M0–M7 (all closed), 13 production follow-up tickets (ASC-090…0102, #70–#82) in M8.**

---

## 1. Inputs — the v0.1.0 handoff

The starting point was a self-contained handoff package (preserved under `app/`, `docs/v0.1.0/`,
`release/`):

| Input artifact | Role | Helped / Hindered |
|---|---|---|
| `app/agent_simulation_control_plane_mvp.html` (673 KB) | Deterministic browser MVP (interaction reference) | **Helped**: unambiguous UX target. **Hindered**: minified single-file bundle → not wire-able to the backend; kept as `/mvp` reference, a new live console was built instead. |
| `01_PRODUCT_REQUIREMENTS.md`, `02_OPERATOR_UI_SPEC.md` | Functional + UI intent | **Helped**: clear domain entities and acceptance. |
| `08_GOLDEN_WORKFLOW_TEST_CASES.md` (GW-01…GW-15) | Executable Given/When/Then acceptance | **Most valuable input** — became unit/e2e tests verbatim and the definition of done. |
| `07_ARCHITECTURE_CONTEXT.md` + `assets/architecture.png` | 3-plane target architecture | **Helped**: named the Kafka/Flink/Druid/Superset/OTel/Grafana topology. |
| `09_DECISIONS_AND_OPEN_QUESTIONS.md` | Open tech choices | **Helped**: pre-scoped the ADRs. |
| `examples/*.json` (experiment, harness, gates, trajectories) | Seed contracts/fixtures | **Helped**: drove the domain schemas and golden path directly. |

**Structure that worked:** a source-of-truth ordering (requirements → UI spec → golden tests →
architecture) plus concrete fixtures. **What was missing:** no arch decisions on language/runtime,
persistence, or platform (arm64) — surfaced late as the main friction (see §7).

---

## 2. SDLC stages & work done

### Stage A — Planning & design (foundational commit + M0 docs)
- Reviewed the handoff; wrote **SYSTEM_DESIGN, IMPLEMENTATION_SPEC, DEPLOYMENT, CICD_STRATEGY,
  BACKLOG** (`docs/design/`) and **7 ADRs** resolving the open decisions.
- Scaffolded the monorepo, tooling (ruff/mypy/pytest), CI skeleton, issue/PR templates, CODEOWNERS.
- Converted the backlog into **51 GitHub issues (ASC-###)** across milestones M0–M7 with a 16-PR plan.

### Stage B — Implementation (deterministic core → services → data/observability)
Delivered as stacked/sequential PRs, each green with tests and an evidence bundle:

| Milestone | Work | PRs |
|---|---|---|
| M0 Foundations | domain schemas, gate-engine, simulation-kernel, telemetry, CI | #45 |
| M1 Golden workflow | control-api, orchestrator, worker, mcp-proxy, in-process Blocked→Passed e2e | #47, #49 |
| M2 Event backbone | Kafka emitter, OTel tracing, MinIO artifacts, SSE | #53, #54, #58 |
| M3 Streaming/analytics | Flink failure-stats job (SQL + tested Python reference) | #55, #67 |
| M4 Observability | OTel Collector, Prometheus/Tempo, Grafana; operator-web live console | #52, #55 |
| M5 Local k3s | Dockerfiles, kustomize overlays, wave deploy, deployed golden e2e | #51, #66, #67, #69 |
| M6 CI/CD | GHCR+SBOM images, security scans, nightly k3d e2e, simulator-as-a-check | #57 |
| M7 GCP (written) | Terraform VM+k3s, terraform-validate, gcp overlay, runbook | #56 |

Late scope from platform reality: control-api stability fix (#66), lite arm64 stack (#67), and
**ClickHouse+Superset** analytics (#69, ADR-0004 update).

### Stage C — Local deployment & verification
Stood up the full stack on a local **k3d** cluster (`agentsim`) and verified **every hop
end-to-end**, with browser + CLI evidence in [`docs/evidence/UI_EVIDENCE.md`](../evidence/UI_EVIDENCE.md):
core loop (Blocked/Passed) → Kafka → Flink → `sim.failure.stats.v1` (`duplicate_transaction_risk`)
→ ClickHouse → **Superset dashboard**; and services → OTel → Tempo → **Grafana traces**.

### Stage D — Wrap-up (see §9)

---

## 3. Modules implemented

Monorepo (`packages/*`, `services/*`, `stream/*`); all Python 3.12 unless noted.

| Module | Responsibility |
|---|---|
| `packages/domain` (`asc_domain`) | Pydantic contracts (ExperimentConfig, IterationEventEnvelope, GateResult, ReleaseDecision, …) + JSON-schema export |
| `packages/gate-engine` (`asc_gate_engine`) | Pure `evaluate(metrics, gate_set) → ReleaseDecision`; provisional gates |
| `packages/simulation-kernel` (`asc_kernel`) | Deterministic WF-04 execution, seeded failure sampling, replay, harness runtime |
| `packages/telemetry` (`asc_telemetry`) | Event envelope, Kafka/Null emitters, OTel tracing, redaction, artifact stores (MinIO/Null) |
| `services/control-api` (`asc_control_api`) | FastAPI: experiments/runs/results/SSE/observability-links (in-memory store — see ASC-091) |
| `services/simulation-orchestrator` (`asc_orchestrator`) | Run expansion, state machine, Stop, aggregation |
| `services/simulation-worker` (`asc_worker`) | Iteration executor → kernel + emitter + tracer + artifact store |
| `services/mcp-simulator-proxy` (`asc_mcp_proxy`) | MCP tools, idempotency, tool authorization |
| `services/aggregation-worker` (`asc_aggregation`) | Kafka→metrics fallback (analytics-independent durability, GW-11) |
| `services/operator-web` | nginx: v0.1.0 MVP at `/mvp` + live console + `/api` proxy + observability tabs |
| `stream/flink-job` (`asc_flink`) | Flink SQL failure-stats job + tested Python reference; `Dockerfile.sql` (JVM, arm64) |
| `deploy/` | Dockerfiles, kustomize (base + local/lite/gcp), Helm values, component manifests, wave scripts |
| `infra/terraform/gcp` | Phase-2 VM + k3s (written, human-gated apply) |

---

## 4. Dependencies

| Layer | Chosen | Notes / ADR |
|---|---|---|
| Language/runtime | Python 3.12, Pydantic v2, FastAPI/Uvicorn | ADR-0001 |
| Event backbone | **Apache Kafka (KRaft)** via official `apache/kafka` | ADR-0002; switched off Bitnami (images removed) |
| Stream processing | **Apache Flink** SQL session cluster (JVM) | ADR-0003; PyFlink dropped on arm64 (no wheels) |
| OLAP store | **Druid** (x86) / **ClickHouse** (arm64 local) | ADR-0004 + update |
| Analytics UI | **Apache Superset** | ADR-0004 |
| Tracing/metrics | **OpenTelemetry → Tempo/Prometheus → Grafana** | ADR-0005 |
| Orchestration | Deterministic kernel + queue/state-machine (no Temporal yet) | ADR-0006 |
| Local/cloud | **k3d/k3s** local; **GCP VM + k3s** via Terraform | ADR-0007 |
| Storage | PostgreSQL (planned), MinIO/GCS (artifacts) | ASC-091, ASC-093 |
| Test/CI | pytest, ruff, GitHub Actions, syft/trivy/gitleaks/bandit | — |

---

## 5. Key decisions (ADRs)

ADR-0001 Python; 0002 Kafka; 0003 Flink; 0004 Druid+Superset (**updated**: ClickHouse on arm64);
0005 OTel+Grafana; 0006 deterministic-kernel-first; 0007 local-k3s-then-GCP. See `docs/adr/`.

---

## 6. What helped / what didn't

**Helped:** golden test cases as executable acceptance; concrete fixtures; injectable adapters
(emitter/artifact-store/agent-runtime) enabling in-process tests without infra; a tested Python
reference for the Flink logic (parity checks + arm64 fallback); wave-ordered idempotent deploy
scripts; the simulator-as-a-check CI job.

**Didn't / friction:** the minified HTML MVP couldn't be wired to the backend; the handoff omitted
platform (arm64) constraints; ephemeral (emptyDir) storage lost state on the Docker restart.

---

## 7. Issues, errors & constraints encountered (and resolutions)

| Constraint / error | Impact | Resolution |
|---|---|---|
| **PyFlink has no arm64 wheels** | Embedded Flink image build failed | JVM **Flink SQL session cluster** (`Dockerfile.sql`, no PyFlink) |
| **Apache Druid has no arm64 image** (amd64/distroless; nano-quickstart needs `perl`) | Druid unusable on Apple Silicon | **ClickHouse** (arm64-native) as OLAP store; Druid retained for x86 (ASC-099) |
| **Bitnami images removed from Docker Hub** | Kafka/Superset/Druid Helm charts `ImagePullBackOff` | Official `apache/kafka`; single-pod ClickHouse/Superset (no Bitnami subcharts) |
| **Docker Desktop 7.65 GiB cap** | Full stack didn't fit | Freed other containers; **bumped to 12 GiB** (18 GiB failed to boot the VM on the 24 GiB host) |
| **control-api OOMKilled (137)** deployed | In-memory emitter/artifact stores accumulated across runs | **NullEmitter/NullArtifactStore** fallbacks + relaxed liveness (PR #66, ASC-085) |
| Flink SQL: `APPROX_PERCENTILE` unknown; event-time watermark never advanced | No windowed output | `MAX` proxy + **processing-time windows** |
| Flink entrypoint ignores `FLINK_PROPERTIES` for `sql-client` | `sql-client` dialed localhost (refused) | Write cluster config into `flink-conf.yaml` before submit |
| Tempo query API on **3200** (assumed 3100) | Grafana datasource couldn't read traces | Fixed datasource URL to `:3200` |
| Stacked-PR merge (#46/#48/#50 closed-not-merged) | Bookkeeping only | Commits landed transitively; issues auto-closed via commit messages |
| `Closes #NN` shell-expansion quirk | ASC-085 stayed open | Closed manually |

_[placeholder]_ Deeper post-mortems per incident can link back to the PR that fixed them.

---

## 8. Verification & evidence

- **Unit/e2e:** all golden cases (GW-01…GW-15) as tests; the in-process Purchase Ambiguity
  Blocked→Passed runs on every PR and publishes `release-decision.json` (simulator-as-a-check).
- **Deployed (local k3s):** browser-verified operator console, Superset dashboard, Grafana traces;
  live Kafka/Flink/ClickHouse data. See [`docs/evidence/UI_EVIDENCE.md`](../evidence/UI_EVIDENCE.md).

---

## 9. Next steps — production on GCP (M8 follow-up tickets)

The local system is the reference; production requires managed services, persistence, identity, and
CD. Each item is a tracked ticket (basis for automated SDLC); bodies contain _[placeholder]_ scopes.

| Area | Ticket | Summary |
|---|---|---|
| Provision | [ASC-090 #70](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/70) | Apply the GCP Terraform (human-gated checklist) |
| Persistence | [ASC-091 #71](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/71) | Control-plane Postgres + Alembic (replace in-memory store) |
| Cluster | [ASC-092 #72](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/72) | Managed **GKE** + prod topology (replace single-node k3s VM) |
| Managed data | [ASC-093 #73](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/73) | Confluent Cloud/Pub-Sub, Dataflow, Cloud SQL, GCS |
| Durability | [ASC-094 #74](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/74) | PVCs/managed disks, Flink checkpoints to GCS, backups |
| Security | [ASC-095 #75](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/75) | Secret Manager, Workload Identity, SSO/IAP, RBAC |
| Edge | [ASC-096 #76](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/76) | cert-manager, Cloud DNS, ingress/network hardening |
| Delivery | [ASC-097 #77](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/77) | CD to GKE, dev→staging→prod promotion, blue/green, rollback |
| Agents | [ASC-098 #78](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/78) | Real model-gateway + MCP adapters (replace deterministic kernel) |
| Analytics | [ASC-099 #79](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/79) | Native Druid on x86/GKE; import Superset dashboards |
| Ops | [ASC-0100 #80](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/80) | Managed Prometheus/Cloud Monitoring, alerting, SLOs |
| Scale | [ASC-0101 #81](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/81) | HPA, 1000+ concurrent iterations, cost bounds, load test |
| Learning loop | [ASC-0102 #82](https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability/issues/82) | Phase-3 production-evidence → learned distributions |

Recommended sequence: **#70 → #71 → #72 → #77** (provision, persist, cluster, CD) then data/security
hardening (#73–#76), then agents/analytics/ops/scale (#78–#0101), then the learning loop (#0102).

---

## 10. Project wrap-up

- **Delivered:** phase-1 local system fully demoable end-to-end; phase-2 GCP Terraform written +
  CI-validated (apply human-gated). 15 PRs merged, 51 delivery issues closed.
- **Known gaps (tracked):** in-memory control-plane store (ASC-091); deterministic kernel, no live
  LLM (ASC-098); Druid deferred to x86 (ASC-099); ephemeral local storage (ASC-094).
- **Local demo lifecycle:** `make cluster-up && make images && make deploy-local` (or
  `deploy/scripts/deploy-lite.sh` on constrained hosts); teardown `k3d cluster delete agentsim`.
- **Reproducibility:** every decision is an ADR; every unit of work is an issue + PR with an
  evidence bundle; the golden workflow is the invariant across in-process and deployed runs.

_[placeholder]_ Attach a one-page exec summary and a demo script/recording for stakeholders.

---

## Appendix — index

- **PRs:** #45, #47, #49, #51, #52, #53, #54, #55, #56, #57, #58, #59, #66, #67, #69.
- **Milestones:** M0–M7 (delivery, closed) · M8 (production/cloud, #70–#82).
- **Design:** `docs/design/` · **Decisions:** `docs/adr/` · **Evidence:** `docs/evidence/` ·
  **Product source-of-truth:** `docs/v0.1.0/`.
