---
title: "What Is an AI Agent? A Definition That Survives Contact With Production"
description: "A precise, engineering-first definition of an AI agent — the loop, autonomy, tools, and where the boundary sits between an agent and a plain LLM call."
level: beginner
readingTime: 8
order: 1
updated: 2026-06-30
tags: [fundamentals, definitions, agent-loop, autonomy]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Model Context Protocol — Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
---

"Agent" is one of the most overloaded words in software right now. A vendor calls
a single prompt template an "agent"; a researcher reserves the word for a fully
autonomous planner. Before you can compare frameworks or design a system, you
need a definition you can actually build against.

## The one-sentence definition

> An **AI agent** is a system where an LLM directs its own actions in a loop —
> deciding what to do next, taking an action against the world through tools, and
> observing the result — in pursuit of a goal, rather than following a fixed,
> developer-specified path.

The load-bearing phrase is *directs its own actions in a loop*. Everything else
(memory, multiple sub-agents, planning) is an elaboration of that core idea.

## Workflows vs. agents

Anthropic's *Building Effective Agents* draws a distinction worth internalizing,
because it changes how you architect and how you debug:

- **Workflows** orchestrate LLMs and tools through **predefined code paths**. The
  control flow is written by you. The LLM fills in steps, but *you* decide the
  sequence. Prompt chaining, routing, and parallelization are workflows.
- **Agents** let the **model decide the control flow** — which tools to call, in
  what order, and when the task is done. The path is discovered at runtime.

Neither is "better." Workflows are more predictable, cheaper, and easier to
evaluate. Agents trade that predictability for flexibility on open-ended tasks.
A mature system usually contains both: deterministic workflow scaffolding around
a bounded agentic core.

## The agent loop

Strip away the branding and almost every agent is the same loop:

```text
   ┌────────────┐
   │   GOAL     │
   └─────┬──────┘
         ▼
   ┌────────────┐     observation      ┌──────────────┐
   │   MODEL    │◀─────────────────────│  ENVIRONMENT │
   │  (decide)  │──────action/tool────▶│   (tools)    │
   └─────┬──────┘                      └──────────────┘
         │  done?
         ▼
   ┌────────────┐
   │   RESULT   │
   └────────────┘
```

Each turn the model receives the goal plus the history so far, decides on the
next action (often a tool call), the environment executes it, and the result is
fed back. The loop ends when the model emits a final answer or a stop condition
trips (max steps, budget, a guard).

This is why the two hardest engineering problems in agents are **what goes into
the context each turn** (context engineering) and **what stops the loop safely**
(harnessing, guardrails). We treat both as first-class topics.

## The four capabilities that make it an agent

1. **Reasoning / planning** — decomposing a goal into next actions.
2. **Tool use** — acting on the world: search, code execution, API calls, file
   edits. Standardized increasingly through the [Model Context
   Protocol](/frameworks/model-context-protocol).
3. **Memory** — carrying state across turns (context window) and across sessions
   (external stores).
4. **Autonomy** — the model, not a fixed script, chooses the next step.

Remove autonomy and you have a pipeline. Remove tools and you have a chatbot.
Remove memory and you have a stateless function. An agent is the combination.

## A litmus test

When someone shows you an "agent," ask: *At runtime, does the model decide the
next action, or did a developer hard-code the sequence?* If the answer is
"hard-coded," it's a workflow — which may be exactly the right choice. If the
model decides, you have a genuine agent, with all the flexibility and all the
failure modes that come with it.

## Where to go next

- The [pre-agentic era](/foundations/pre-agentic-era) — why this isn't as new as
  it looks, and what we can reuse.
- [From LLMs to agents](/foundations/llm-to-agent-evolution) — how we got the
  reasoning + tool-calling that makes the loop work.
- [Agent anatomy](/foundations/agent-anatomy) — the components in detail.
- When you're ready to build: [tool use](/patterns/tool-use) and
  [multi-agent orchestration](/patterns/multi-agent-orchestration).
