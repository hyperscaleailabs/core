---
title: "The Agent Engineer's Glossary"
description: "Precise, opinionated definitions for the vocabulary of agentic systems - from action space to swarm - so a team can argue about the right thing."
level: beginner
readingTime: 7
order: 5
updated: 2026-06-30
tags: [glossary, definitions, reference]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Model Context Protocol - Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
  - title: "LangGraph - Overview"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

Shared vocabulary prevents shallow disagreements. These definitions are
deliberately opinionated toward how the terms are used in production.

## Core

**Agent** - A system where an LLM directs its own actions in a loop toward a
goal, choosing the control flow at runtime. Contrast with *workflow*.

**Workflow** - LLM(s) and tools orchestrated through developer-defined code
paths. Predictable; the model fills steps but doesn't choose the sequence.

**Agent loop** - The cycle of decide → act (tool) → observe, repeated until a
stop condition. The unit of everything agentic.

**Harness** - The code around the model that runs the loop: tool execution,
context management, stopping conditions, retries, durability, guards, tracing.

**Policy** - The decision-making function. In an LLM agent, the model is the
policy.

## Action & tools

**Tool / function** - A callable capability exposed to the model with a name,
description, and JSON-schema parameters. The model requests it; your code runs it.

**Action space** - The full set of tools/actions available to an agent. Larger
spaces are more capable and harder to keep reliable.

**MCP (Model Context Protocol)** - An open protocol standardizing how tools,
data, and prompts are described and served to models, so integrations are
portable across hosts and models. See [MCP](/frameworks/model-context-protocol).

**A2A (Agent-to-Agent)** - Protocols/standards for agents to discover and
communicate with each other across systems. See [A2A](/frameworks/a2a-protocol).

## Reasoning & planning

**Chain-of-thought (CoT)** - Eliciting intermediate reasoning steps to improve
multi-step accuracy.

**ReAct** - A pattern interleaving reasoning traces with actions (reason → act →
observe), the archetype for the tool-using loop.

**Planning** - Decomposing a goal into an ordered set of steps/subgoals, possibly
revised as the agent learns. See [planning](/patterns/planning).

**Reflection** - An agent critiquing and revising its own output before finishing.
See [reflection](/patterns/reflection).

## Memory & context

**Context window** - The finite token budget the model sees each turn; the
agent's working memory.

**Context engineering** - Deliberately curating what enters the context each turn
to preserve signal and avoid degradation. See [context
engineering](/patterns/context-engineering).

**Context rot / degradation** - Quality decline as the context fills with stale,
redundant, or low-signal tokens.

**RAG** - Retrieval-Augmented Generation: fetching relevant external documents
into context at query time. **GraphRAG** adds a knowledge-graph structure over
the corpus. See [RAG / GraphRAG](/patterns/graphrag).

## Topology

**Single-agent** - One loop, one context. The right default.

**Orchestrator–worker (manager–agent)** - A coordinator delegates subtasks to
specialist agents and synthesizes results.

**Swarm** - Many agents coordinating with limited central control, often peer to
peer. See [swarms](/patterns/agent-swarms).

**Handoff** - Transferring control (and relevant context) from one agent to
another.

**Graph / state machine** - Agents/steps as nodes with explicit transitions and
shared state; the [LangGraph](/frameworks/langgraph) model.

## Reliability

**Guardrail** - A constraint enforced on inputs, outputs, or actions (validation,
allow-lists, permission scoping, human approval). See
[guardrails](/production/guardrails-safety).

**Human-in-the-loop (HITL)** - A person approves or corrects specific actions
before they take effect.

**Evaluation (eval)** - Systematic measurement of agent quality against tasks and
criteria, offline or in production. See [evaluation](/production/evaluation).

**Trace** - The recorded sequence of a run: prompts, model outputs, tool calls,
results, tokens, latencies. The primary artifact for debugging agents.

**Failure mode** - A characteristic way agents go wrong (looping, hallucinated
tool use, context poisoning, cascading multi-agent errors). See [failure
modes](/production/failure-modes).

## Next

- [What is an agent?](/foundations/what-is-an-agent) if any of these were new.
- [Comparisons](/comparisons) to see these concepts applied across frameworks.
