# ADR-0004: Druid + Superset for near-real-time analytics

**Status:** Accepted · **Date:** 2026-07-24

## Context
`09_…` asks: PostgreSQL, ClickHouse, or Druid for experiment analytics? The architecture diagram
and stakeholder request explicitly name **Druid (near-real-time OLAP) + Apache Superset
(querying/visualization)**.

## Decision
Use **Apache Druid** with a Kafka indexing supervisor on the iteration/failure-stats topics, and
**Apache Superset** as the analytics UI, with dashboards provisioned from `dashboards/superset/`.

## Consequences
- Sub-second OLAP over high-cardinality correlation IDs and failure types; ideal for live run
  analytics.
- Druid is the heaviest local tenant; a `micro-quickstart`/`lite` profile is used on small hosts.
- ClickHouse remains a future option if operational cost of Druid proves too high; the boundary is
  the Kafka topics + Superset SQL, so the store can be swapped.

## Update (2026-07-25): ClickHouse on Apple Silicon / arm64
Apache Druid ships **no arm64 container image** (amd64-only, distroless), so on Apple Silicon it can
only run under slow qemu emulation, and the single-process launcher needs `perl` the distroless base
lacks; the community Helm chart also depends on now-unavailable Bitnami postgres/zookeeper images.
For the local (arm64) deployment we therefore use **ClickHouse** as the OLAP store — the alternative
this ADR already anticipated. It is arm64-native and light, ingests directly from Kafka via the
Kafka table engine + a materialized view (`sim.failure.stats.v1` → MergeTree), and Superset connects
via `clickhouse-connect`. Druid remains the choice for x86 clusters (manifests + ingestion specs are
retained). The contract boundary (Kafka topics + Superset SQL) is unchanged, so the swap is
transparent to the rest of the system.
