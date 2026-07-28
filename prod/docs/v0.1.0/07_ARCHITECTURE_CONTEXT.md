# Architecture Context

## 1. Architecture reference

The generated architecture diagram is available at:

```text
assets/architecture.png
```

It separates the platform into Simulation, Control, and Data planes and shows how production evidence eventually feeds new simulation profiles.

## 2. Simulation pane

Responsibilities:

- Experiment and workflow configuration.
- Persona, primary agent, and sub-agent execution.
- MCP simulator/cache/proxy.
- Learned or assumed dependency failure distributions.
- Harness validation and recovery.
- Accelerated execution using smaller models, caching, and optional GPU optimization.
- Trajectory, log, metric, and trace emission.

The initial MVP runs this logic in the browser. The first backend implementation should move it into a deterministic simulation kernel and background workers.

## 3. Control pane

Responsibilities:

- Workflow, skill, harness, agent, and tool registries.
- Policies and guardrails.
- Gate definitions and thresholds.
- Anomaly and alert rules.
- Release decision and rollback policy definitions.
- Versioning and audit.

The control plane should not be embedded inside workers. Workers consume immutable versioned configuration.

## 4. Data pane

Responsibilities:

- Ingest logs, telemetry, traces, tool outcomes, and trajectory events.
- Stream and aggregate features.
- Provide near-real-time experiment analytics.
- Provide operational infrastructure monitoring.
- Retain reproducibility and audit evidence.

Target components shown in the diagram:

- Kafka + Flink for streaming and features.
- Druid + Apache Superset for near-real-time OLAP and analytics.
- OpenTelemetry + Grafana for infrastructure and operational observability.

MVP substitutions are permitted if contracts remain compatible.

## 5. Production-informed loop

Future production flow:

```text
Production agent execution
→ sanitized telemetry and trajectories
→ streaming analysis
→ versioned learned failure distributions
→ operator-reviewed simulation profile
→ stochastic experiments
→ evaluation gates
→ safer release
→ new production evidence
```

The system must label the source of every distribution. Learned distributions should not silently replace manually approved profiles.

## 6. Recommended logical services

- Operator Web.
- Control API.
- Experiment Orchestrator.
- Simulation Worker.
- Agent Runtime Adapter.
- MCP Simulator/Proxy.
- Harness Runtime.
- Gate Evaluation Service.
- Telemetry/Event Adapter.
- Aggregation Worker.
- Query/Analytics API.
- Production Evidence Importer, later.
- Release Integration Adapter, later.

## 7. Suggested storage

- PostgreSQL for control-plane configuration, versioning, run metadata, gates, and audit.
- Object storage for large raw/sanitized trajectory artifacts and exports.
- Kafka/Redpanda for event transport.
- Druid or ClickHouse for analytical queries when scale requires it.
- OpenTelemetry backend for traces and operational metrics.

## 8. Key architectural rules

- Completed runs reference immutable configuration versions.
- Each iteration has a deterministic seed and runtime version.
- Worker execution is bounded and isolated.
- Transactional tools use idempotency and explicit ambiguous-state recovery.
- Tool authorization is enforced outside the model.
- Raw sensitive data is redacted before telemetry emission.
- Gate decisions are deterministic from versioned metrics and gate definitions.
- Analytics failure cannot erase simulation results.
- Event schemas are versioned and backward compatible.

## 9. MVP-to-production substitution map

| Browser MVP | Production implementation |
|---|---|
| Local fixture state | Control API + PostgreSQL |
| Browser deterministic generator | Simulation kernel + workers |
| Fake event stream | SSE/WebSocket backed by queue/events |
| Browser metrics aggregation | Streaming/batch aggregation service |
| Static trajectory list | Durable trajectory/event store |
| Mock integration status | Real health, lag, and trace metrics |
| Local JSON export | Signed/versioned result artifact |
| Simulated decision | Gate service and CI/CD check |

## 10. Architecture decisions still required

See `09_DECISIONS_AND_OPEN_QUESTIONS.md` for choices around LangGraph/custom state machines, Temporal, Kafka/Redpanda, Druid/ClickHouse/PostgreSQL, model gateway, production data retention, and Kubernetes job versus worker-pool execution.
