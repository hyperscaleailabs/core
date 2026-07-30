---
title: "Evaluating Agents: Measuring What You Can't See Otherwise"
description: "Why agent evaluation is the real bottleneck, and how to build it — task suites, trajectory vs. outcome metrics, LLM-as-judge, and online evaluation in production."
level: advanced
readingTime: 9
updated: 2026-06-30
tags: [evaluation, testing, metrics, llm-as-judge]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Hugging Face — Learn"
    url: "https://huggingface.co/learn"
    publisher: "Hugging Face"
    accessed: "2026-06-30"
---

You cannot improve — or safely ship — what you can't measure, and agents are
unusually hard to measure. Output is non-deterministic, "correct" is often
fuzzy, and the same task can succeed via many different paths. Evaluation is the
discipline that turns "it seemed to work in the demo" into "it works 94% of the
time and here's where it fails." It is, in practice, the bottleneck for shipping
reliable agents.

## Start before you build

The most common mistake is building the agent first and figuring out evaluation
later. Invert it: define what success looks like — a set of representative tasks
with checkable outcomes — *before* iterating on prompts and topology. Your eval
suite is the spec.

## Two things to measure

### Outcome evaluation — did it get the right result?
Judge the final answer against a criterion:

- **Programmatic checks** where truth is checkable: tests pass, JSON validates,
  the number matches, the file compiles. Cheapest and most reliable — prefer
  these.
- **Reference comparison** against known-good answers.
- **LLM-as-judge** for subjective quality (helpfulness, tone, completeness),
  using a separate model with a rubric. Powerful but itself needs validating —
  spot-check the judge against human labels, or it just launders bias.

### Trajectory evaluation — how did it get there?
Two agents can reach the right answer with wildly different cost and safety. Also
measure the *path*:

- **Efficiency** — steps, tokens, cost, latency to completion.
- **Tool correctness** — did it choose the right tools with valid arguments?
- **Adherence** — did it stay within guardrails and avoid unsafe actions?
- **No thrashing** — did it loop or drift ([failure
  modes](/production/failure-modes))?

Outcome tells you *if*; trajectory tells you *how well* — and trajectory is where
cost and risk live.

## Build a task suite

- **Representative** — mirror real user tasks and real data distributions.
- **Graded difficulty** — easy/medium/hard, including known adversarial cases
  (prompt injection, ambiguous goals, missing information).
- **Checkable** — each task has an automatable success criterion where possible.
- **Versioned** — the suite lives in Git and grows with every bug you find; a
  production failure becomes a new eval case.

## Offline and online

- **Offline (pre-deploy)** — run the suite on every change to prompts, tools,
  topology, or model. This is your regression gate; a prompt tweak that fixes one
  task often breaks three others, and only the suite catches it.
- **Online (in production)** — sample real traffic and evaluate live: success
  signals, human feedback, guardrail trips, cost per task. Production is a
  distribution your offline suite never fully anticipates.

## Tie it to observability

Evaluation runs on **traces** — the recorded prompts, tool calls, and results
from [observability](/production/observability). No traces, no trajectory eval.
Instrument first; evaluate on the instrumentation.

## Practical guidance

- **Automate the gate.** Wire the eval suite into CI so no change ships without
  passing (this repo does exactly that for its content pipeline).
- **Prefer objective signals.** Reach for LLM-as-judge only when no programmatic
  check exists, and validate the judge.
- **Track cost as a first-class metric.** An agent that's 2% more accurate and 5×
  more expensive may be a regression.
- **Close the loop.** Every production failure → a reproduction → a new eval case
  → a fix verified by the suite.

Hugging Face's [Learn](https://huggingface.co/learn) courses include hands-on
agent evaluation if you want to build a suite from scratch.

## Next

- [Observability](/production/observability) — the traces evaluation runs on.
- [Failure modes](/production/failure-modes) — what your suite should probe for.
