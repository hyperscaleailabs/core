# ADR-0006: Deterministic simulation kernel first; queue + DB state machine (no Temporal yet)

**Status:** Accepted · **Date:** 2026-07-24

## Context
`09_…` open questions: LangGraph vs custom state machine; Temporal for durable execution; k8s job
per iteration vs persistent worker pool. Phase-1 goal is a reproducible golden workflow on local
k3s **without** requiring live LLMs.

## Decision
- Implement a **custom, typed, deterministic simulation kernel** (`packages/simulation-kernel`)
  with an `AgentRuntimeAdapter` boundary; the phase-1 adapter is the deterministic simulator. A
  model-gateway adapter is added later without changing the kernel contract.
- Orchestration uses a **queue (Kafka/DB-backed) + PostgreSQL run state machine**, not Temporal,
  for the first functional MVP. Revisit Temporal when durable pause/resume and long recovery
  justify it.
- Execution uses a **persistent worker pool** (Deployment with replicas), not one k8s Job per
  iteration, to avoid scheduling overhead at 100s–1000s of iterations.

## Consequences
- Reproducible, LLM-free golden path; fast CI.
- Simpler infra now; Temporal/LangGraph deferred behind the adapter + state-machine boundaries.
- Durable long-running recovery semantics are limited until Temporal is introduced.
