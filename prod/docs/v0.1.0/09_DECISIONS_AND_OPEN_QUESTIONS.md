# Decisions and Open Questions

Implementation agents should convert resolved items into Architecture Decision Records.

## Orchestration

- Use LangGraph, a custom typed state machine, or another agent runtime?
- Is Temporal required for durable experiments, pause/resume, and long-running recovery, or can a queue plus database state machine satisfy the first production MVP?
- Should each iteration run as a Kubernetes job, or should a persistent worker pool execute many iterations?

## Data and streaming

- Kafka versus Redpanda for local and development environments?
- Flink from the first production MVP, or a simpler aggregation worker until volume requires it?
- PostgreSQL, ClickHouse, or Druid for experiment analytics?
- How long are raw and sanitized trajectories retained?

## Models and evaluation

- Which model gateway abstraction is used?
- How are model price catalogs versioned?
- Which metrics are deterministic and which require evaluator models?
- How is persona satisfaction calculated without allowing evaluator nondeterminism to hide failures?

## Security and governance

- Identity provider and role model?
- Multi-tenant isolation requirements and key strategy?
- Which prompt/tool fields are sensitive and must be redacted?
- Who can create or override blocking gates?
- Are manual decision overrides allowed in production, and how do they expire?

## Production evidence

- What production event schema can be collected lawfully and safely?
- How are learned distributions reviewed, versioned, and approved?
- How are rare catastrophic failures preserved when learning distributions?
- What drift threshold triggers a new simulation cycle?

## Release integration

- Which CI/CD system consumes decisions?
- Is a platform decision advisory or required?
- Which rollback actions can be automated and which remain manual?
- How is a rollback correlated to the experiment that justified it?

## UI and product

- Is arbitrary workflow editing needed after the four templates?
- Which registry items require approval workflows?
- What report format is required for auditors or executives?
- Which analytical views remain in the custom UI versus Superset/Grafana?

## Statistical policy

- Minimum iteration count for each gate?
- Confidence intervals or Bayesian decision rules for low-probability failures?
- How should zero observed failures be interpreted in finite samples?
- How are correlated failures and temporal bursts represented?
