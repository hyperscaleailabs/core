---
title: "Effective Harnesses for Long-Running Agents"
description: "What changes when an agent runs for hours or days - durability, checkpointing, context compaction, and human-in-the-loop - and how to build a harness that survives it."
level: advanced
readingTime: 10
updated: 2026-06-30
tags: [harness, durability, long-running, checkpointing, hitl]
sources:
  - title: "Effective Harnesses for Long-Running Agents"
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Effective Context Engineering for AI Agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "AIDLC Workflows"
    url: "https://github.com/awslabs/aidlc-workflows"
    publisher: "AWS Labs"
    accessed: "2026-06-30"
---

A five-step agent and a five-hour agent are different engineering problems. Short
agents can be stateless request/response; long-running agents accumulate context,
outlive process lifetimes, and must survive failures without losing progress. The
**harness** - the code around the model - is where that reliability is won or
lost.

## What "long-running" breaks

As task horizon grows from seconds to hours or days, four things stop being free:

1. **The context window fills.** History outgrows the window; naive agents rot
   ([context engineering](/patterns/context-engineering)).
2. **Processes die.** Deployments restart, spot instances vanish, networks blip.
   Work must survive process death.
3. **Errors accumulate.** Over hundreds of steps, a 1%-per-step error rate is
   near-certain failure without recovery.
4. **Humans need to intervene.** Long tasks cross approval boundaries and need
   correction mid-flight.

## The pillars of a long-running harness

### Durability & checkpointing
Persist agent state - plan, progress, key observations - to durable storage so a
run can **pause and resume** across process restarts. The agent's state lives in
a store, not in memory; the loop reads it back on resume. Frameworks like
[LangGraph](/frameworks/langgraph) provide checkpointing primitives; the pattern
mirrors decades-old workflow orchestration
([pre-agentic era](/foundations/pre-agentic-era)).

### Context compaction
Continuously compress older history into compact state and keep the window lean,
so a task that spans thousands of turns never blows the budget. Summarize
decisions and outcomes; discard raw deliberation. Externalize the plan and
findings to a file/store the agent re-reads, rather than holding everything in
context.

### Idempotency & safe retries
Assume any step may run more than once (after a crash, a retry, a resume). Make
side-effecting tools **idempotent** or guard them so re-execution is safe. This
is the same discipline distributed systems demand - agents are no exception.

### Bounded autonomy
Enforce global budgets: max steps, max cost, max wall-clock, and a top-level
abort. Long-running does not mean unbounded - it means *checkpointed within
bounds*. Without this, a looping agent quietly runs up a bill
([failure modes](/production/failure-modes)).

### Human-in-the-loop gates
Insert explicit interruption points where a human approves risky actions or
corrects course, then the agent resumes from the checkpoint. Essential for tasks
that touch money, production systems, or external communication
([guardrails](/production/guardrails-safety)).

### Observability across the whole run
A long run is only debuggable if every step, tool call, and decision is traced
under one run id. You cannot reconstruct an eight-hour failure from logs you
didn't keep ([observability](/production/observability)).

## A reference loop

```text
resume(run_id):
  state = store.load(run_id)              # durable checkpoint
  while not done(state) and within_budget(state):
     ctx    = compact(state)              # context engineering
     action = model.decide(ctx)
     if risky(action): await_human(action)   # HITL gate
     result = run_idempotent(action)      # safe on retry
     state  = update(state, action, result)
     store.save(run_id, state)            # checkpoint every step
     trace(run_id, action, result)        # observability
  return finalize(state)
```

Every line maps to a pillar. The shape is deliberately boring - durable,
bounded, observed. Boring is what survives a week in production.

## Where this shows up

Software-engineering agents are the canonical long-running case: multi-file
changes, test loops, and iterative debugging over long horizons. AWS Labs'
[AIDLC workflows](https://github.com/awslabs/aidlc-workflows) explore
agent-driven development lifecycles, which exercise exactly these durability and
checkpointing needs. Anthropic's
[harness guidance](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
distills the patterns from building Claude Code.

## The takeaway

Long-running reliability is not a model property; it's a **harness property**.
Durable state, compaction, idempotency, bounded autonomy, human gates, and full
tracing turn a capable-but-fragile agent into one you can trust to run unattended.

## Next

- [Context engineering](/patterns/context-engineering) - the compaction pillar in
  depth.
- [Observability](/production/observability) - tracing long runs.
- [Guardrails & safety](/production/guardrails-safety) - the HITL and permission
  pillars.
