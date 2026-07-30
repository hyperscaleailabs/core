---
title: "Building with the Claude API: From First Request to Agents"
description: "A foundations map of the Claude API primitives — messages, system prompts, tool use, extended thinking, prompt caching, and MCP — and how they stack up into agents, anchored to Anthropic Academy's free course."
level: beginner
readingTime: 9
created: 2026-07-01
updated: 2026-07-01
tags: [claude, api, tool-use, mcp, rag, education]
draft: false
aiGenerated: true
license: CC-BY-4.0
sources:
  - title: "Building with the Claude API (Anthropic Academy)"
    url: "https://anthropic.skilljar.com/claude-with-the-anthropic-api/"
    publisher: "Anthropic Academy"
    license: "© Anthropic — course materials"
    accessed: "2026-07-01"
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-07-01"
---

Most of the atlas talks about agents at the level of *concepts* — the loop,
autonomy, harnesses. But every agent eventually bottoms out in concrete API
calls: a request with messages, a system prompt, a set of tool definitions, and a
response you have to parse. This page maps the **Claude API primitives** to the
[capability ladder](/foundations/llm-to-agent-evolution) so the jump from "I can
call a model" to "I built an agent" stops feeling like magic.

It's organized around Anthropic Academy's free, hands-on course
[*Building with the Claude API*](https://anthropic.skilljar.com/claude-with-the-anthropic-api/) —
a good vendor-specific complement to vendor-neutral primers. You need working
Python and comfort with JSON; you don't need prior ML experience.

## Why the API layer is worth understanding

A framework can hide these primitives, but it can't hide their *consequences*.
Latency, cost, reliability, and most failure modes trace directly back to how you
use the raw API — how big your context is, whether you cache it, how you shape
tool results. Understanding the primitives is what lets you debug an agent instead
of just restarting it.

## The primitives, bottom to top

Each rung below is a concrete API capability. The higher rungs are the ones that
turn a text generator into something [agentic](/foundations/what-is-an-agent).

### 1. Messages and multi-turn context

The core call is a list of `messages` (alternating user/assistant turns) that you
resend each request — the API is stateless, so *you* own the conversation. Getting
message formatting and context handling right is the unglamorous foundation
everything else sits on. Every extra turn you carry is tokens you pay for and
latency you wait on, which is why [context
engineering](/patterns/context-engineering) becomes a first-class concern the
moment conversations get long.

### 2. System prompts and behavior controls

A `system` prompt sets role, constraints, and format up front. Alongside it,
`temperature` trades determinism for variety, streaming trades total latency for
time-to-first-token, and structured-output techniques push the model toward
machine-parseable responses. This is the rung that turns a chatbot into a
*callable component* you can put inside code.

### 3. Prompt engineering and evaluation

Reliable behavior comes from technique, not luck: XML-tag structuring to separate
instructions from data, worked examples, and unambiguous directives. Crucially,
the course pairs this with **evaluation** — generating test datasets and automated
graders. If you take one habit from it, take this one: an agent without an eval
harness is a demo, not a system. See [evaluation](/production/evaluation).

### 4. Tool use — the pivotal rung

Tool use is where a model stops answering and starts *acting*. You pass tool
definitions (name, description, JSON-schema parameters); the model may emit a tool
call instead of prose; your code runs it and feeds the result back on the next
turn. The course covers custom tools, batch operations, and built-in web search.
This is the mechanism behind the entire [agent loop](/foundations/what-is-an-agent)
— the atlas covers its design tradeoffs in depth under [tool use](/patterns/tool-use).

```jsonc
// The model emits a tool call; your harness executes it and returns an observation.
{ "type": "tool_use", "name": "search_docs",
  "input": { "query": "vector index recall vs latency" } }
```

### 5. Retrieval-augmented generation (RAG)

To ground answers in your own data, the course builds RAG from parts: chunking,
embeddings, BM25 keyword search, and **contextual retrieval** (prepending
chunk-level context before embedding to fight the "lost snippet" problem). This is
the API-level view of what the atlas treats architecturally under
[GraphRAG](/patterns/graphrag) and retrieval patterns.

### 6. Extended features — thinking, multimodal, citations

Beyond text: **extended thinking** (spending inference-time compute before
answering — the concrete form of ["reasoning before
acting"](/foundations/llm-to-agent-evolution)), image analysis, PDF processing,
and citation generation. These widen what a single call can ingest and how
verifiable its output is.

### 7. Prompt caching — the cost/latency lever

Caching a stable prefix (a long system prompt, a document, a tool schema) so
repeated requests skip re-processing it is one of the highest-leverage
optimizations in production. In agent loops that resend a growing context every
turn, caching is often the difference between viable and unaffordable.

### 8. MCP — standardized tools and resources

The [Model Context Protocol](/frameworks/model-context-protocol) standardizes how
tools and data are exposed to a model, so integrations are portable across hosts
instead of bespoke glue. The course has you build both MCP **servers** and
**clients** — the same protocol the [Claude Agent
SDK](/frameworks/claude-agent-sdk) and Claude Code speak.

### 9. Agent architectures

The top rung composes everything below into workflows: **chaining**,
**routing**, and **parallelization**. Note the framing — these are the *workflow*
patterns from [*Building Effective
Agents*](https://www.anthropic.com/engineering/building-effective-agents), the
predictable scaffolding you reach for before handing full control to an
autonomous loop. The atlas expands this under [multi-agent
orchestration](/patterns/multi-agent-orchestration).

## A suggested path through it

1. **Rungs 1–3** first — get a reliable single call *and* an eval before adding
   moving parts. Most agent bugs are really prompt or context bugs.
2. **Rung 4 (tools)** next — this is the conceptual jump to agency; everything
   after is elaboration.
3. **RAG and caching** when real data and real bills show up.
4. **MCP and agent architectures** once a single tool-using loop is solid — don't
   orchestrate multiple agents before one works.

## Tradeoffs to keep in mind

- **Vendor-specific by design.** These are Claude API mechanics. The *concepts*
  transfer to any provider; the exact parameters and MCP specifics are Anthropic's.
- **Primitives, not a harness.** The API gives you the pieces; production
  durability — retries, checkpoints, budgets — is the [harness
  layer](/production/long-running-harnesses) you build (or adopt via the
  [Claude Agent SDK](/frameworks/claude-agent-sdk)) on top.

## Next

- [From LLM to Agent](/foundations/llm-to-agent-evolution) — the capability ladder
  these primitives climb.
- [Tool use](/patterns/tool-use) — designing tools a model can actually use well.
- [Claude Agent SDK](/frameworks/claude-agent-sdk) — the batteries-included harness
  over these same primitives.
