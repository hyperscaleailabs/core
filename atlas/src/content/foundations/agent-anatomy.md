---
title: "Agent Anatomy: The Six Components Every System Has"
description: "Model, instructions, tools, memory, orchestration, and the harness - the parts that make up any agent, and the design decisions each one forces."
level: intermediate
readingTime: 11
order: 4
updated: 2026-06-30
tags: [architecture, memory, tools, orchestration, harness]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Effective Context Engineering for AI Agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Claude Agent SDK - Overview"
    url: "https://code.claude.com/docs/en/agent-sdk/overview"
    publisher: "Anthropic"
    accessed: "2026-06-30"
---

Whatever framework you pick, an agent decomposes into the same six components.
Naming them explicitly is the fastest way to design a system, review someone
else's, or localize a bug.

## 1. The model (the policy)

The LLM that decides the next action. Key decisions:

- **Capability vs. cost/latency.** A frontier model reasons better but costs more
  per step, and agents take many steps. Many production systems **route**: a
  strong model for planning, a cheaper/faster one for routine sub-steps.
- **One model or several.** Mixing models per role is common but adds operational
  surface (prompts, evals, and quirks multiply).

## 2. Instructions (the system prompt & policies)

The durable behavioral contract: role, objectives, constraints, tone, and
*especially* what **not** to do. This is where you encode guardrails the model
should self-enforce and the criteria for "done." Treat the system prompt as
code - version it, review it, and evaluate changes. Vague instructions are the
number-one cause of agents that "sort of work."

## 3. Tools (the action space)

Everything the agent can *do*: retrieval, code execution, API calls, file edits,
sub-agent invocation. Tool design is interface design for a non-human caller:

- **Descriptions are prompts.** The name and description are how the model
  decides when to use a tool. Ambiguity here causes wrong-tool errors.
- **Narrow beats broad.** A few well-scoped tools outperform one god-tool with a
  dozen modes.
- **Return signal, not noise.** Tool results consume context; return the useful
  slice, not a 40 KB dump.
- **Standardize with [MCP](/frameworks/model-context-protocol)** so tools are
  portable across agents and hosts.

See [tool use](/patterns/tool-use) for the full design guide.

## 4. Memory

Two distinct kinds, often conflated:

- **Working memory** = the context window. It's finite and it's the model's only
  view of the world each turn. Managing it well is
  [context engineering](/patterns/context-engineering): what to include,
  summarize, or evict.
- **Long-term memory** = external stores that outlive a turn or session: vector
  DBs and knowledge graphs for retrieval ([RAG / GraphRAG](/patterns/graphrag)),
  scratchpad files, databases of past interactions. The agent reads/writes these
  through tools.

A frequent bug: teams push everything into working memory until the context
degrades ("context rot"), when the fix is to move most state to long-term memory
and retrieve on demand.

## 5. Orchestration (the topology)

How control and work are arranged:

- **Single agent** - one loop, one context. Simplest; start here.
- **Manager / workers** - a coordinator delegates to specialists and synthesizes.
- **Sequential / graph** - explicit stages with defined transitions
  ([LangGraph](/frameworks/langgraph) style).
- **Swarm / peer-to-peer** - many agents coordinating with less central control
  ([swarms](/patterns/agent-swarms)).

Topology is a real architectural decision with cost, latency, and failure-mode
consequences - cover it in [multi-agent
orchestration](/patterns/multi-agent-orchestration).

## 6. The harness (the runtime)

The code around the model that actually runs the loop - often 80% of the
engineering and the least glamorous. It owns:

- The action loop and **stopping conditions** (max steps, budget, goal checks).
- **Error handling & retries** for flaky tools.
- **Durability**: checkpointing and resumption for long tasks.
- **Human-in-the-loop** gates for risky actions.
- **Observability**: tracing every step, tool call, and token
  ([observability](/production/observability)).
- **Guardrails**: input/output validation, permission scoping
  ([guardrails](/production/guardrails-safety)).

Agent SDKs (e.g. the [Claude Agent SDK](/frameworks/claude-agent-sdk),
[Strands](/frameworks/strands-agents)) exist largely to give you a batteries-included
harness so you don't rebuild this per project.

## How the components interact

```text
        instructions ─┐
                       ▼
   observation ──▶ [ MODEL ] ──▶ action ──▶ [ TOOLS ] ──▶ world
        ▲              │                         │
        │              ▼                         ▼
   [ HARNESS ] ◀── memory (working + long-term) ◀┘
   (loop, retries, durability, guards, tracing)
        ▲
        └── orchestration decides which agent/topology handles the step
```

## A design checklist

When designing or reviewing an agent, answer one question per component:

1. **Model** - which model(s), and why; is routing worth it?
2. **Instructions** - is "done" defined? Are the don'ts explicit?
3. **Tools** - are they narrow, well-described, and low-noise?
4. **Memory** - what lives in context vs. retrieved on demand?
5. **Orchestration** - is single-agent enough? If not, what topology?
6. **Harness** - stopping conditions, retries, durability, tracing, guards?

If you can't answer all six, you've found where the system will surprise you.

## Next

- [Context engineering](/patterns/context-engineering) - managing component #4.
- [Long-running harnesses](/production/long-running-harnesses) - component #6 at
  scale.
- [Glossary](/foundations/glossary) - precise definitions for the terms above.
