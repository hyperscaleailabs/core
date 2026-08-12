---
title: "Multi-Agent Orchestration: Topologies and Tradeoffs"
description: "Orchestrator-worker, sequential, and graph topologies for coordinating multiple agents - when multi-agent beats single-agent, and the overhead you're signing up for."
level: advanced
readingTime: 10
problem: "A task is too broad, too parallel, or too specialized for one agent and one context window."
alsoKnownAs: [manager-agent, supervisor, hierarchical-agents]
updated: 2026-06-30
tags: [multi-agent, orchestration, topology, delegation]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Building a Multi-Agent System (Production-Ready AI Roadshow)"
    url: "https://codelabs.developers.google.com/codelabs/production-ready-ai-roadshow/1-building-a-multi-agent-system/building-a-multi-agent-system#0"
    publisher: "Google Developers"
    accessed: "2026-06-30"
  - title: "LangGraph - Overview"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

Multi-agent systems are seductive: split the problem, give each part a specialist,
compose the results. Sometimes that's exactly right. Often a single well-designed
agent with good tools is simpler and more reliable. This page is about choosing
deliberately - and knowing what coordination costs.

## Start with the question: do you need more than one?

A second agent earns its keep when at least one is true:

- **Specialization** - subtasks need genuinely different tools, instructions, or
  even models (a coding agent vs. a research agent).
- **Parallelism** - independent subtasks can run concurrently to cut wall-clock
  time (search N sources at once).
- **Context isolation** - each subtask needs its own clean context window, and
  merging them into one would cause [context rot](/patterns/context-engineering).
- **Separation of duties** - a reviewer agent that must not share the author's
  context (a [reflection](/patterns/reflection) boundary).

If none apply, prefer a [single agent](/foundations/agent-anatomy). Every extra
agent multiplies prompts, evals, tokens, latency, and failure surface.

## The core topologies

### Orchestrator–worker (manager–agent)
A coordinator decomposes the goal, dispatches subtasks to specialist workers, and
synthesizes their outputs. The dominant production pattern: clear ownership,
easy to add workers, natural place for [planning](/patterns/planning). Google's
[multi-agent codelab](https://codelabs.developers.google.com/codelabs/production-ready-ai-roadshow/1-building-a-multi-agent-system/building-a-multi-agent-system#0)
walks through building exactly this shape.

```text
              ┌────────────────┐
              │  ORCHESTRATOR  │  plans, delegates, synthesizes
              └───┬──────┬─────┘
        ┌─────────┘      └─────────┐
        ▼                          ▼
   ┌─────────┐               ┌──────────┐
   │ worker  │               │  worker  │  specialists, isolated contexts
   │ (search)│               │ (coding) │
   └─────────┘               └──────────┘
```

### Sequential / pipeline
Agents hand off in a fixed order (draft → edit → fact-check). Predictable and
easy to evaluate stage-by-stage; effectively a [workflow](/foundations/what-is-an-agent)
of agents. Good when stages are stable.

### Graph / state machine
Agents and steps are nodes with explicit transitions over shared state - the
[LangGraph](/frameworks/langgraph) model. Supports cycles, conditional routing,
checkpointing, and human-in-the-loop. The right choice when control flow is
complex but must remain auditable and resumable.

### Swarm / peer-to-peer
Many agents coordinate with limited central control. Powerful for exploration and
resilience, hardest to keep reliable - covered in [agent
swarms](/patterns/agent-swarms).

## The overhead you're signing up for

Multi-agent is a distributed system; the classic problems return (see
[the pre-agentic era](/foundations/pre-agentic-era)):

- **Cascading errors** - one worker's wrong output silently corrupts the
  synthesis. Validate at boundaries.
- **Coordination cost** - every handoff is tokens, latency, and a place for
  context to be lost or garbled.
- **Context handoff** - deciding *what* context to pass is a real design problem;
  pass too little and the worker flails, too much and it drowns.
- **Debuggability** - traces span multiple agents; you need
  [observability](/production/observability) that stitches them together.
- **Cost multiplication** - N agents, each looping, each calling models.

## A decision heuristic

1. Can one agent with better tools/prompt do it? **Do that.**
2. Need specialization or parallelism? **Orchestrator–worker.**
3. Fixed, stable stages? **Sequential pipeline.**
4. Complex, cyclic, must be resumable/auditable? **Graph (LangGraph).**
5. Genuinely emergent/exploratory and you can afford the reliability tax?
   **Swarm.**

## Next

- [Agent swarms](/patterns/agent-swarms) - the far end of the spectrum.
- [Failure modes](/production/failure-modes) - what breaks, and how to catch it.
- [Framework comparison matrix](/comparisons/framework-matrix)
