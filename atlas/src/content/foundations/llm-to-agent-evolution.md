---
title: "From LLM to Agent: The Capability Ladder"
description: "How a next-token predictor became something that can plan and act - instruction tuning, tool calling, reasoning, and the harness that closes the loop."
level: beginner
readingTime: 9
order: 3
created: 2026-06-30
updated: 2026-07-01
tags: [llm, tool-calling, reasoning, evolution]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Hugging Face - Learn"
    url: "https://huggingface.co/learn"
    publisher: "Hugging Face"
    accessed: "2026-06-30"
  - title: "Building with the Claude API (Anthropic Academy)"
    url: "https://anthropic.skilljar.com/claude-with-the-anthropic-api/"
    publisher: "Anthropic Academy"
    accessed: "2026-07-01"
---

> **Updated 2026-07-01** - added a Claude-API path for climbing these rungs
> hands-on (source: [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api/)).

An LLM by itself is a function: text in, text out, no memory, no side effects. An
agent acts on the world in a loop. Getting from one to the other took a specific
ladder of capabilities. Knowing the rungs helps you reason about *why* agents
behave the way they do - and where they break.

## Rung 0 - The base model

A pretrained language model predicts the next token over a huge corpus. It has
broad knowledge and pattern-matching ability but no notion of "following
instructions" or "being helpful." You can coax behavior out of it with clever
prompting, but it's unreliable as a component.

## Rung 1 - Instruction following

Instruction tuning and preference optimization (RLHF and its successors) align
the model to *do what you ask* in a *helpful, honest, harmless* way. This is the
rung that made prompting practical: you can now describe a task in plain language
and get a usable result. Everything agentic builds on this.

## Rung 2 - Structured output

To be a system component, a model must emit machine-parseable output on demand -
JSON matching a schema, a specific enum, a function signature. Reliable
structured output is what lets you put a model *inside* code instead of in front
of a human. It's the difference between a chatbot and a callable service.

## Rung 3 - Tool / function calling

The pivotal rung. The model is given a set of tool definitions (name,
description, JSON-schema parameters) and can choose to emit a *tool call* instead
of a final answer. Your code executes the tool and returns the result, which the
model reads on the next turn. This is what lets a model **act**: search the web,
run code, query a database, edit a file. The [Model Context
Protocol](/frameworks/model-context-protocol) standardizes how those tools are
described and served so they're portable across models and hosts.

```jsonc
// The model emits this instead of prose:
{ "tool": "search_docs", "arguments": { "query": "vector index recall vs latency" } }
// Your harness runs it, then feeds the result back as the next observation.
```

## Rung 4 - Reasoning before acting

Chain-of-thought and, more recently, models trained to spend inference-time
compute "thinking" before answering, dramatically improve multi-step tasks. For
agents this matters because each loop iteration involves a decision - *which tool,
with what arguments, or am I done?* Better reasoning means fewer wasted steps and
fewer confidently-wrong actions.

## Rung 5 - The loop and the harness

None of the above is an agent yet. The **harness** - the code around the model -
is what turns single decisions into autonomous behavior:

- It runs the tool the model asked for and appends the observation.
- It manages the context window: what history to keep, compress, or drop
  ([context engineering](/patterns/context-engineering)).
- It enforces stopping conditions, budgets, retries, and guardrails.
- For long tasks it adds durability: checkpoints, resumption, human approvals
  ([long-running harnesses](/production/long-running-harnesses)).

An agent is *model + harness*. Two teams using the same model can get wildly
different reliability because the harness is where most of the engineering lives.

## Rung 6 - Composition: multiple agents

Once a single agent works, you can compose them: a coordinator that delegates to
specialists, parallel workers, or a [swarm](/patterns/agent-swarms) of peers.
Composition buys you specialization and parallelism at the cost of coordination
overhead and new [failure modes](/production/failure-modes).

## The mental model to keep

Capability climbs, but **reliability is not free at any rung**. A more capable
model reduces some errors and introduces subtler ones. The job of the agent
engineer is less "pick the smartest model" and more "build the harness, context,
and evaluation that convert raw capability into dependable behavior."

## Learn the rungs hands-on

Hugging Face's free [Learn](https://huggingface.co/learn) courses (LLM Course,
Agents Course) are a solid, vendor-neutral way to build each rung yourself before
reaching for a framework. For a provider-specific counterpart that maps these
rungs onto concrete API calls - messages, tool use, extended thinking, prompt
caching, and MCP - see [Building with the Claude
API](/foundations/building-with-the-claude-api).

## Next

- [Agent anatomy](/foundations/agent-anatomy) - the components in detail.
- [Tool use](/patterns/tool-use) - designing tools an agent can actually use.
