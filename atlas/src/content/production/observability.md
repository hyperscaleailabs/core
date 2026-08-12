---
title: "Observability for Agents: If You Can't Trace It, You Can't Ship It"
description: "Agents fail invisibly. What to instrument - traces, spans, token and cost accounting, tool telemetry - and why the trace is the primary debugging artifact."
level: advanced
readingTime: 8
updated: 2026-06-30
tags: [observability, tracing, telemetry, debugging, cost]
sources:
  - title: "Effective Harnesses for Long-Running Agents"
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "LangGraph - Overview"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

Traditional software fails loudly - an exception, a 500, a stack trace. Agents
fail *quietly and plausibly*: a confident wrong answer, a subtly wrong tool call,
a slow drift off task. There's often no error at all. That makes **observability
non-optional**: the trace is not a debugging convenience, it's the only way to
know what your agent actually did.

## The unit of observability: the trace

A **trace** is the complete, ordered record of one agent run:

- Every **model call** - the full prompt/context in, the completion out.
- Every **tool call** - name, arguments, result, latency, success/failure.
- Every **decision point** - why the loop continued or stopped.
- **Token counts and cost** per step and per run.
- **Timings** - latency of each step and the whole run.
- A **run id** correlating all of it, including across sub-agents.

If you can replay a run from its trace and understand every decision, you have
enough. If you're guessing, you don't.

## What to instrument

### Spans and hierarchy
Model the run as nested spans: run → step → (model call, tool call). For
[multi-agent systems](/patterns/multi-agent-orchestration), child agents are
child spans under the parent's run id - otherwise a distributed failure is
impossible to reconstruct.

### Token & cost accounting
Attribute tokens and dollars to every step. This is how you catch
[loop and fan-out blow-ups](/production/failure-modes) and how you make the
cost/latency tradeoffs in [comparisons](/comparisons/failure-mode-tradeoffs) with
real numbers instead of vibes.

### Tool telemetry
Track per-tool call volume, error rate, and latency. A flaky or slow tool is a
top cause of thrashing and timeouts; you want it on a dashboard, not discovered
in an incident.

### Quality signals
Log guardrail trips, human interventions, and (where available) success/failure
outcomes so [evaluation](/production/evaluation) can run on real traffic.

## Standards and tooling

Prefer open standards - **OpenTelemetry**-style tracing generalizes agent
telemetry to the observability stack you already run. Framework-native tracing
(e.g. the streaming/inspection built into
[LangGraph](/frameworks/langgraph)) and agent-focused platforms (LangSmith,
Langfuse, Arize Phoenix, and others) give agent-aware trace views out of the box.
The principle matters more than the vendor: **capture the full trajectory, keep
it, and make it searchable.**

## Instrument first, then everything else

Two capabilities depend entirely on observability:

- **[Evaluation](/production/evaluation)** runs on traces - no traces, no
  trajectory metrics.
- **[Long-running harnesses](/production/long-running-harnesses)** are only
  debuggable if every checkpointed step was traced.

So instrument on day one, not after the first production mystery. The teams that
treat tracing as foundational debug in minutes; the teams that bolt it on later
debug by re-running and hoping.

## A minimal checklist

- [ ] Every run has a correlating id, propagated to sub-agents.
- [ ] Full prompt/context and completion captured per model call.
- [ ] Tool name, args, result, latency, and status captured per tool call.
- [ ] Tokens and cost attributed per step and per run.
- [ ] Guardrail trips and human interventions logged.
- [ ] Traces retained and searchable long enough to investigate incidents.

## Next

- [Evaluation](/production/evaluation) - turn traces into measurement.
- [Failure modes](/production/failure-modes) - what to look for in a trace.
