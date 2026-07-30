---
title: "Context Engineering: Managing the Agent's Working Memory"
description: "The context window is the agent's only view of the world each turn. How to curate it — selection, compression, isolation, retrieval — to avoid context rot."
level: advanced
readingTime: 9
problem: "Context windows are finite and quality degrades as they fill; agents on long tasks accumulate noise and lose the plot."
alsoKnownAs: [context-management, prompt-engineering-for-agents]
updated: 2026-06-30
tags: [context-engineering, memory, compression, retrieval]
sources:
  - title: "Effective Context Engineering for AI Agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Effective Harnesses for Long-Running Agents"
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
---

If prompt engineering is crafting the *instructions*, **context engineering** is
curating *everything the model sees each turn* — instructions, history, tool
results, retrieved documents, and state. For agents it's the single highest-impact
skill, because the [agent loop](/foundations/what-is-an-agent) feeds the model a
context that grows every step, and quality degrades as it fills.

## Why the context window is the whole game

The model has no memory beyond what's in the window. Each turn it decides based
solely on that snapshot. Two consequences:

- **Everything competes for space.** Tool results, history, and retrieved docs
  crowd out each other and the actual task.
- **More is not better.** Beyond a point, adding tokens *lowers* quality —
  "context rot": the signal gets buried, the model latches onto stale or
  irrelevant content, and it drifts.

Anthropic frames the goal as finding the **smallest set of high-signal tokens**
that lets the model do the task well — not stuffing the window because it's large.

## The four levers

### 1. Selection — what to include
Curate ruthlessly. Include the goal, the current plan, the last relevant
observations, and the specific retrieved facts needed *now*. Exclude everything
else. A tool that returns 5,000 rows should hand back the 5 that matter
([tool use](/patterns/tool-use)).

### 2. Compression — shrinking without losing signal
As history grows, **summarize** older turns into compact state and drop the raw
transcript. Keep decisions and outcomes; discard the deliberation. This is what
lets an agent run for hours without the window exploding.

### 3. Isolation — separate contexts for separate jobs
Give sub-tasks their own clean windows via sub-agents, then return only the
result to the parent. Context isolation is a primary reason to go
[multi-agent](/patterns/multi-agent-orchestration): a research worker can read ten
documents and hand back three sentences.

### 4. Retrieval — pull knowledge in on demand
Keep long-term knowledge *out* of the window and fetch just-in-time via
[RAG/GraphRAG](/patterns/graphrag) or a scratchpad the agent reads/writes. The
window holds working memory; the store holds everything else.

## Practical tactics

- **Externalize state to a file/store.** Let the agent persist its plan and
  findings outside the context, then read back only what's needed — essential for
  [long-running harnesses](/production/long-running-harnesses).
- **Structure the context.** Clear sections (goal, plan, recent observations,
  retrieved facts) help the model attend to the right part.
- **Trim tool output at the source.** Cheaper to return less than to summarize
  more later.
- **Budget the window.** Reserve space for the response and for the next few
  observations; don't fill to the brim.
- **Watch for rot in traces.** Rising token counts with falling quality is the
  signature; fix by compressing or isolating, not by upgrading the model.

## The mindset

Treat the context window like a **cache or a working set**, not a transcript. Your
job each turn is to assemble the minimal high-signal state that lets the model act
well, then get out of the way. Teams that internalize this ship agents that stay
coherent over long horizons; teams that don't watch quality quietly erode as the
window fills.

## Next

- [Long-running harnesses](/production/long-running-harnesses) — context
  engineering across hours and days.
- [RAG & GraphRAG](/patterns/graphrag) — the retrieval lever in depth.
