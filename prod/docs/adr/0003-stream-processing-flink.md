# ADR-0003: Apache Flink for streaming failure-type statistics

**Status:** Accepted · **Date:** 2026-07-24

## Context
`09_…` asks: Flink from the first production MVP, or a simpler aggregation worker until volume
requires it? The stakeholder request explicitly wants a **Flink stream with basic statistics on
failure types**, and the architecture diagram shows Flink between Kafka and Druid.

## Decision
Ship a **Flink job** (`stream/flink-job`) computing near-real-time failure-type statistics from
`sim.iteration.events.v1` into `sim.failure.stats.v1`. Keep a **fallback `aggregation-worker`**
(plain Kafka consumer → metrics) so final run results are never blocked by streaming availability
(GW-11). Prefer Flink SQL; use PyFlink/DataStream for custom classification.

## Consequences
- Meets the explicit requirement and the diagram.
- The fallback preserves the rule "analytics failure cannot erase simulation results."
- Two aggregation paths must agree on the same event contract and metric definitions (tested).
