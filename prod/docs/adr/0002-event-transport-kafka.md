# ADR-0002: Apache Kafka (KRaft) as the event backbone

**Status:** Accepted · **Date:** 2026-07-24

## Context
Open question in `09_DECISIONS_AND_OPEN_QUESTIONS.md`: Kafka vs Redpanda. The target architecture
diagram and product spec explicitly show **Kafka + Flink**, and the stakeholder request names
Kafka. Druid's Kafka indexing service and Flink's Kafka connector are first-class.

## Decision
Use **Apache Kafka in KRaft mode** (no ZooKeeper), single broker locally, as the transport for the
iteration event envelope and control/stats topics. Topics are schema-versioned (`.v1`).

## Consequences
- Native, well-supported integration with Flink (source/sink) and Druid (indexing supervisor).
- KRaft removes ZooKeeper, simplifying the k3s footprint.
- Redpanda remains a drop-in Kafka-API alternative if local resource pressure demands it; the code
  depends only on the Kafka protocol, not broker internals.
