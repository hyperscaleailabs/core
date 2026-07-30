---
title: "Planning: From Goal to Ordered Action"
description: "How agents decompose goals into steps — plan-then-execute vs. interleaved planning, multi-agent planning, and why plans must be revisable."
level: intermediate
readingTime: 8
problem: "Open-ended goals require a sequence of dependent steps the agent must derive, order, and adapt as it learns."
alsoKnownAs: [task-decomposition, plan-and-execute]
updated: 2026-06-30
tags: [planning, decomposition, multi-agent-planning]
sources:
  - title: "Multi-Agent Planning in AI"
    url: "https://www.geeksforgeeks.org/artificial-intelligence/multiagent-planning-in-ai/"
    publisher: "GeeksforGeeks"
    accessed: "2026-06-30"
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
---

**Planning** is how an agent turns "book me a trip" into an ordered set of
dependent actions. It's the difference between an agent that flails and one that
makes steady progress on multi-step work.

## Two styles

### Plan-then-execute
The agent produces a full plan up front, then executes each step (often
dispatching steps to tools or sub-agents). Benefits: the plan is inspectable,
approvable, and parallelizable. Risk: reality diverges from the plan, so you need
a way to **re-plan**.

### Interleaved (ReAct-style) planning
The agent plans one step at a time, acting and observing before deciding the next
move. Benefits: naturally adaptive. Risk: can lose the thread on long horizons or
wander without a global objective. This is the default of a plain
[tool-use](/patterns/tool-use) loop.

Most robust systems combine them: a lightweight high-level plan for direction,
interleaved execution for adaptivity, and periodic re-planning.

## Plans must be revisable

A plan is a hypothesis, not a contract. When a step fails or an observation
contradicts the plan, the agent must revise rather than plow ahead. Encode this:
make re-planning an explicit action, and set stopping conditions so a thrashing
agent doesn't loop forever (a classic [failure
mode](/production/failure-modes)). Frameworks like
[LangGraph](/frameworks/langgraph) make the plan/execute/replan cycle an explicit
graph you can checkpoint and resume.

## Multi-agent planning

When several agents act in a shared environment, planning becomes **multi-agent
planning** — a mature subfield with problems that predate LLMs:

- **Coordination** — ordering actions so agents don't conflict or duplicate work.
- **Conflict resolution** — reconciling agents with incompatible sub-goals or
  contended resources.
- **Centralized vs. distributed** — a planner that assigns everyone's actions
  (simpler to reason about, a bottleneck) vs. agents that plan locally and
  negotiate (scalable, harder to guarantee).
- **Communication cost** — more coordination messages mean more latency and
  tokens; over-communication is its own failure.

These are the same problems classical distributed AI studied — see
[the pre-agentic era](/foundations/pre-agentic-era) — now instantiated with LLM
agents. The [GeeksforGeeks overview of multi-agent
planning](https://www.geeksforgeeks.org/artificial-intelligence/multiagent-planning-in-ai/)
is a concise primer on the taxonomy.

## Design tips

- **Externalize the plan.** Keep it in state/memory the agent can read and edit,
  not buried in a single context turn — so it survives compaction and can be
  audited.
- **Make steps checkable.** A step with a success criterion enables
  [reflection](/patterns/reflection) and clean retries.
- **Bound the horizon.** Cap steps and cost; require re-planning at checkpoints
  for long tasks ([long-running harnesses](/production/long-running-harnesses)).
- **Prefer the simplest topology.** Add multi-agent planning only when a single
  planner genuinely can't cope — coordination overhead is not free.

## Next

- [Multi-agent orchestration](/patterns/multi-agent-orchestration) — turning
  plans into delegated work.
- [Long-running harnesses](/production/long-running-harnesses) — planning across
  hours or days.
