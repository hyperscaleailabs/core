---
title: "Framework Comparison Matrix: Choosing an Agent Stack"
description: "A side-by-side comparison of LangChain, LangGraph, the Claude Agent SDK, Strands, MCP, and A2A across control model, durability, multi-agent support, and lock-in."
level: intermediate
readingTime: 9
updated: 2026-06-30
tags: [comparison, frameworks, decision, matrix]
sources:
  - title: "LangChain Documentation"
    url: "https://docs.langchain.com/"
    publisher: "LangChain"
    accessed: "2026-06-30"
  - title: "LangGraph - Overview"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
    publisher: "LangChain"
    accessed: "2026-06-30"
  - title: "Claude Agent SDK - Overview"
    url: "https://code.claude.com/docs/en/agent-sdk/overview"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Strands Agents"
    url: "https://strandsagents.com/"
    publisher: "Strands Agents"
    accessed: "2026-06-30"
  - title: "Model Context Protocol - Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
---

There is no single best agent framework - there's a best fit for your control,
durability, and portability requirements. This matrix compares the tools in the
[frameworks catalog](/frameworks) along the axes that actually drive the decision.
Details for each are on its own page; this page is for choosing.

## At a glance

| | Type | Control model | Durability | Multi-agent | MCP | Best for |
| --- | --- | --- | --- | --- | --- | --- |
| [LangChain](/frameworks/langchain) | Framework / components | Components + light chains | Via LangGraph | Via LangGraph | Yes | Integrations, RAG, prototyping |
| [LangGraph](/frameworks/langgraph) | Orchestration runtime | Explicit graph / state machine | Checkpointing, resume | First-class | Yes | Stateful, durable, auditable agents |
| [Claude Agent SDK](/frameworks/claude-agent-sdk) | Vendor SDK | Model-driven loop + permissions | Session/context mgmt | Subagents | Yes | Fast path to a hardened harness on Claude |
| [Strands](/frameworks/strands-agents) | Lightweight SDK | Model-driven (model plans) | Lighter | Supported | Yes | Minimal-ceremony tool-using agents |
| [MCP](/frameworks/model-context-protocol) | Protocol | n/a (connectivity) | n/a | n/a | - | Portable tools/data across hosts |
| [A2A](/frameworks/a2a-protocol) | Protocol | n/a (agent interop) | n/a | Enables | Complements | Cross-team/vendor agent fleets |

*MCP and A2A are protocols, not runtimes - you use them **with** a framework, not
instead of one.*

## The decision axes explained

### Control model: explicit vs. model-driven
- **Explicit (LangGraph)** - you define nodes, edges, and transitions. Maximum
  control, auditability, and determinism; more up-front ceremony.
- **Model-driven (Strands, Claude Agent SDK loop)** - the model plans the
  sequence. Minimal ceremony; reliability tracks model capability.

Rule of thumb: the more a workflow *must* be deterministic and reviewable
step-by-step, the more you want explicit control.

### Durability: does it survive a crash?
For anything [long-running](/production/long-running-harnesses), checkpointing and
resume are essential. LangGraph makes this first-class; SDKs offer lighter
session/context management. If your task spans hours, weight this heavily.

### Multi-agent support
All support multiple agents, but differently: LangGraph via explicit graph
topologies, the Claude Agent SDK via subagents, Strands via delegation, and A2A
for cross-system interop. Match to the [topology](/patterns/multi-agent-orchestration)
you actually need - and remember a single agent is often enough.

### Portability & lock-in
- **Protocols first.** Building tools on [MCP](/frameworks/model-context-protocol)
  keeps them reusable across any host/framework - the strongest hedge against
  lock-in.
- **Provider coupling.** The Claude Agent SDK is optimized for Claude; LangGraph
  and Strands are provider-flexible. If multi-provider routing matters, favor the
  flexible options.

## A decision guide

1. **Prototyping RAG or tool apps, want max integrations?** Start with
   [LangChain](/frameworks/langchain).
2. **Need stateful, durable, auditable, resumable agents?**
   [LangGraph](/frameworks/langgraph).
3. **On Claude and want the shortest path to a production-grade harness?**
   [Claude Agent SDK](/frameworks/claude-agent-sdk).
4. **Want the smallest possible agent with model-driven planning?**
   [Strands](/frameworks/strands-agents).
5. **Integrating many tools/data sources or many teams' agents?** Layer in
   [MCP](/frameworks/model-context-protocol) and
   [A2A](/frameworks/a2a-protocol) regardless of the runtime you pick.

## The meta-point

Frameworks change fast; the **axes don't**. Decide on control model, durability,
multi-agent shape, and portability first - then pick the tool that fits, and
build your tools on open protocols so the tool is replaceable.

## Next

- [Failure-mode & tradeoff comparison](/comparisons/failure-mode-tradeoffs)
- [Multi-agent orchestration](/patterns/multi-agent-orchestration)
