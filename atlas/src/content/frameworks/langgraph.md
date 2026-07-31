---
title: "LangGraph"
name: "LangGraph"
description: "A low-level orchestration framework for stateful, durable agents modeled as graphs - with checkpointing, human-in-the-loop, and multi-actor topologies."
level: advanced
readingTime: 7
category: orchestration
language: [python, javascript]
repo: "https://github.com/langchain-ai/langgraph"
homepage: "https://www.langchain.com/langgraph"
docs: "https://docs.langchain.com/oss/python/langgraph/overview"
codeLicense: "MIT"
maturity: stable
maintainer: "LangChain, Inc."
supportsMcp: true
supportsMultiAgent: true
updated: 2026-06-30
tags: [framework, orchestration, state-machine, durability, multi-agent]
sources:
  - title: "LangGraph - Overview"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
    publisher: "LangChain"
    accessed: "2026-06-30"
  - title: "LangChain Documentation"
    url: "https://docs.langchain.com/"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

**LangGraph** models an agent as a **graph**: nodes are steps (an LLM call, a
tool, a sub-agent) and edges are transitions over shared state. Instead of hiding
the control flow, it makes the loop explicit and inspectable - which is exactly
what you want when an agent needs to be durable, resumable, and auditable in
production.

## Why a graph

The [agent loop](/foundations/what-is-an-agent) is a state machine. LangGraph
leans into that:

- **Explicit state** - a typed object threaded through every node; you control
  what persists and what's derived.
- **Cycles** - first-class support for loops (reason → act → observe), not just
  DAGs.
- **Deterministic control flow** - you decide routing and stopping conditions
  around the model's decisions.

## Production features that matter

- **Checkpointing & durability** - persist state so a run can pause and resume,
  survive crashes, and support long-running tasks
  ([long-running harnesses](/production/long-running-harnesses)).
- **Human-in-the-loop** - interrupt at a node for approval or correction, then
  continue.
- **Time travel / replay** - inspect and re-run from a prior state, invaluable for
  debugging.
- **Multi-actor topologies** - orchestrator–worker, sequential, and peer patterns
  for [multi-agent systems](/patterns/multi-agent-orchestration).
- **Streaming & observability** - stream tokens/events; integrates with tracing.

## When to reach for it

- Your agent is stateful, long-running, or needs human approvals.
- You need reproducibility and the ability to resume after failure.
- You're building multi-agent workflows and want explicit control over topology.

## Tradeoffs

- **More concepts up front.** You define state, nodes, and edges - more ceremony
  than a one-shot agent loop, which pays off as complexity grows.
- **You still own design.** The framework gives durability primitives; choosing a
  sane topology and stopping conditions is on you.

## Relationship to LangChain

[LangChain](/frameworks/langchain) supplies the components (models, tools,
retrievers); LangGraph supplies the stateful runtime. Use LangChain tools and
[MCP](/frameworks/model-context-protocol) integrations as nodes within a LangGraph
graph.

## See also

- [Framework comparison matrix](/comparisons/framework-matrix)
- [Long-running harnesses](/production/long-running-harnesses)
