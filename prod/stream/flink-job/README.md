# flink-job

Near-real-time **failure-type statistics** for the Agent Simulation Control Plane (ASC-030/031).

Consumes `sim.iteration.events.v1`, computes tumbling-window counts/rates keyed by
`(runId, failureClassification)`, and writes to `sim.failure.stats.v1` - which feeds Druid/Superset
and the live-monitor provisional gates.

## Layout
- `sql/failure_stats.sql` - the deployed Flink SQL job (Kafka source/sink, 5s tumbling windows).
- `pyflink/job.py` - entrypoint that loads + executes the SQL on a streaming TableEnvironment.
- `src/asc_flink/failure_stats.py` - pure-Python **reference implementation** of the same
  aggregation, unit-tested against golden-run events (no cluster needed).
- `Dockerfile` - Flink base + PyFlink + Kafka SQL connector + the job.

## Acceptance (ASC-030)
During the golden run, `sim.failure.stats.v1` shows a non-zero `duplicate_transaction_risk` count
for the unsafe config and zero for the safe config - verified by `tests/test_failure_stats.py`.

## Deploy
Requires the Flink Kubernetes Operator (`deploy/helm-values/flink-operator.yaml`); the job runs via
`deploy/k3s/components/flink/flinkdeployment.yaml` (application mode).
