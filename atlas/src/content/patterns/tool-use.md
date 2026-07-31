---
title: "Tool Use: Designing an Action Space an Agent Can Actually Use"
description: "The single-agent pattern everything builds on. How to define, scope, and describe tools so the model calls the right one with the right arguments."
level: intermediate
readingTime: 9
problem: "An agent needs to affect the world - search, compute, call APIs, edit files - reliably and safely."
alsoKnownAs: [function-calling, ReAct]
updated: 2026-06-30
tags: [tool-use, function-calling, react, design]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Model Context Protocol - Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
---

Tool use is the pattern the entire field rests on. An agent without tools is a
chatbot; with well-designed tools it can search, compute, transact, and build.
The catch: the model only knows a tool from its **name, description, and
parameter schema**, so tool design is really **interface design for a
non-human, probabilistic caller**.

## The mechanic (ReAct in one breath)

Each turn the model either emits a final answer or a **tool call** - a structured
request naming a tool and its arguments. The harness executes it, appends the
result as an observation, and loops. Reasoning interleaved with acting is the
ReAct pattern, and it's the default shape of a tool-using agent.

## Design principles

### 1. Tools are prompts
The name and description are how the model decides *whether and when* to call a
tool. `get_data` is a coin flip; `search_customer_orders(customer_id, status?)`
is self-documenting. Write descriptions for the model, not for your API docs.

### 2. Narrow beats broad
Prefer several sharply-scoped tools over one god-tool with a `mode` switch. A
model picks well among distinct options and badly among overloaded ones. If a
tool's description needs the word "and" three times, split it.

### 3. Return signal, not noise
Tool results consume the context window. Return the useful slice - the 5 rows,
not the 5,000; the extracted field, not the raw HTML. Noisy results cause
[context rot](/patterns/context-engineering) and downstream mistakes.

### 4. Make errors legible
When a tool fails, return an actionable message ("no customer with that id; try
search_customers") rather than a stack trace. The model can often recover if the
error tells it how.

### 5. Constrain arguments with schema
Tight JSON schemas (enums, required fields, formats) prevent whole classes of
malformed calls. The schema is a guardrail, not just documentation.

### 6. Guard side effects
Any tool that writes, spends, or sends needs authorization scoping and often
[human-in-the-loop](/production/guardrails-safety) approval. Separate read tools
(safe to retry) from write tools (must be idempotent or gated).

## Standardize with MCP

Rather than reimplementing tools per project, expose them via the
[Model Context Protocol](/frameworks/model-context-protocol) so they're portable
across agents and hosts, with a clean permission boundary. Build the tool once;
reuse it everywhere.

## A worked example

Bad - one overloaded tool:

```jsonc
{ "name": "db", "description": "run database operations",
  "parameters": { "op": "string", "payload": "object" } }
```

Better - narrow, described, schema-constrained, read/write separated:

```jsonc
{ "name": "find_orders",
  "description": "Return orders for a customer, optionally filtered by status.",
  "parameters": { "customer_id": "string",
                  "status": { "enum": ["open","shipped","cancelled"] } } }

{ "name": "cancel_order",
  "description": "Cancel an OPEN order. Requires human approval.",
  "parameters": { "order_id": "string", "reason": "string" } }
```

The model now reasons about *which* action fits and *what* arguments to pass,
and the write path is explicitly gated.

## Common failure modes

- **Wrong-tool selection** - usually vague/overlapping descriptions.
- **Hallucinated arguments** - loose schemas; tighten them.
- **Result overflow** - tools dumping raw payloads into context.
- **Unsafe writes** - missing idempotency or approval on side-effecting tools.

See [failure modes](/production/failure-modes) for the full catalog.

## Next

- [Reflection](/patterns/reflection) - let the agent check its own work.
- [Context engineering](/patterns/context-engineering) - keep tool results from
  drowning the signal.
