---
title: "Failure Modes of Agentic Systems: A Field Catalog"
description: "The characteristic ways agents go wrong in production — looping, hallucinated tool use, context poisoning, cascading multi-agent errors — with causes and mitigations."
level: advanced
readingTime: 12
updated: 2026-06-30
tags: [failure-modes, reliability, debugging, production]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Effective Harnesses for Long-Running Agents"
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Effective Context Engineering for AI Agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Multi-Agent Planning in AI"
    url: "https://www.geeksforgeeks.org/artificial-intelligence/multiagent-planning-in-ai/"
    publisher: "GeeksforGeeks"
    accessed: "2026-06-30"
---

Agents don't fail like ordinary software. They fail *plausibly* — producing
confident, well-formed output that is wrong, or wandering off task while looking
busy. This catalog names the recurring failure modes so you can recognize them in
a trace, and pairs each with its usual cause and mitigation. Treat it as a
checklist when designing, reviewing, or debugging.

## Single-agent failure modes

### 1. Infinite / thrashing loops
**Symptom:** the agent repeats similar actions without progress, or oscillates
between two states, burning tokens and budget.
**Cause:** no meaningful stopping condition; a plan with no success criterion; a
tool that never returns the information the model expects.
**Mitigation:** hard caps on steps and cost; a defined "done" check; detect
repeated states and break out; make [reflection](/patterns/reflection) decide
termination rather than the same generation loop.

### 2. Hallucinated or wrong tool use
**Symptom:** the agent calls the wrong tool, invents a tool that doesn't exist, or
fabricates arguments.
**Cause:** vague/overlapping tool descriptions; loose parameter schemas; too many
tools.
**Mitigation:** narrow, well-described tools; tight JSON schemas with enums; fewer
tools; validate calls before executing ([tool use](/patterns/tool-use)).

### 3. Goal drift
**Symptom:** the agent gradually optimizes for the wrong thing or forgets the
original objective on a long task.
**Cause:** the goal scrolls out of the effective context; interleaved planning
with no persistent objective.
**Mitigation:** keep the goal and plan in persistent state re-injected each turn;
periodic re-grounding ([context engineering](/patterns/context-engineering)).

### 4. Context rot / degradation
**Symptom:** quality falls as a session lengthens; the agent fixates on stale or
irrelevant content.
**Cause:** an ever-growing window packed with low-signal tokens.
**Mitigation:** compress history, isolate sub-tasks, retrieve on demand — the core
of [context engineering](/patterns/context-engineering).

### 5. Overconfident fabrication
**Symptom:** fluent, authoritative answers that are simply false.
**Cause:** ungrounded generation; no retrieval; no verification.
**Mitigation:** ground with [RAG/GraphRAG](/patterns/graphrag); require citations;
add an evaluator/verification step; prefer programmatic checks where truth is
checkable.

### 6. Unsafe or irreversible actions
**Symptom:** the agent deletes, spends, sends, or overwrites something it
shouldn't.
**Cause:** side-effecting tools without gating; non-idempotent writes; over-broad
permissions.
**Mitigation:** human-in-the-loop for risky actions; idempotency; least-privilege
scoping; separate read vs. write tools ([guardrails](/production/guardrails-safety)).

### 7. Prompt injection / tool-result poisoning
**Symptom:** content fetched by a tool (a web page, a document, an email)
contains instructions the agent obeys.
**Cause:** treating retrieved/tool content as trusted instruction rather than
untrusted data.
**Mitigation:** clearly delimit and label untrusted content; never grant
retrieved text authority over the system prompt; constrain the action space;
sandbox tools. A top security concern for any agent that reads the open web.

## Multi-agent failure modes

These compound the above — see
[multi-agent orchestration](/patterns/multi-agent-orchestration) and
[swarms](/patterns/agent-swarms).

### 8. Cascading errors
**Symptom:** one agent's wrong output is accepted downstream and corrupts the
final result.
**Cause:** no validation at handoff boundaries; blind trust between agents.
**Mitigation:** validate inputs/outputs at each boundary; treat peer output as
untrusted; add a verification stage before synthesis.

### 9. Context handoff loss
**Symptom:** a worker flails because it didn't receive the context it needed, or
drowns because it received too much.
**Cause:** underspecified or bloated handoffs.
**Mitigation:** define exactly what transfers on each handoff; pass the minimal
sufficient context.

### 10. Coordination breakdown (deadlock / duplication / ping-pong)
**Symptom:** agents wait on each other, redo the same work, or hand a task back
and forth.
**Cause:** the classic [multi-agent planning](https://www.geeksforgeeks.org/artificial-intelligence/multiagent-planning-in-ai/)
problems — conflicting goals, no clear ownership, no global termination.
**Mitigation:** clear task ownership; global step/cost budget and abort signal
above the fleet; a coordinator that owns "done."

### 11. Emergent, non-reproducible behavior
**Symptom:** the system does something nobody specified and you can't reproduce
it.
**Cause:** decentralized, non-deterministic interactions (especially swarms).
**Mitigation:** constrain emergence with boundary guardrails; record everything
for replay; prefer bounded topologies unless emergence is the point.

## Cross-cutting: the two failure amplifiers

- **Cost/latency blow-ups.** Loops and multi-agent fan-out multiply token spend
  and wall-clock time. Budget them explicitly ([cost & latency in
  comparisons](/comparisons/failure-mode-tradeoffs)).
- **Invisible failure.** The worst version of every mode above is the one you
  can't see. Without [observability](/production/observability) — full traces of
  prompts, tool calls, and results — you can't diagnose any of them.

## How to use this catalog

1. **At design time** — walk the list and ask "which of these can happen here,
   and what's my mitigation?" Absence of an answer is a risk you've accepted
   silently.
2. **At review time** — map a proposed system to the modes it's exposed to.
3. **At debug time** — match the symptom in your trace to a mode, then apply the
   mitigation rather than guessing.

Reliability in agents is not a smarter model; it's **systematically closing off
these modes** with harness, context, and evaluation.

## Next

- [Long-running harnesses](/production/long-running-harnesses) — durability that
  prevents whole categories of failure.
- [Evaluation](/production/evaluation) — measuring whether your mitigations work.
- [Failure-mode & tradeoff comparison](/comparisons/failure-mode-tradeoffs)
