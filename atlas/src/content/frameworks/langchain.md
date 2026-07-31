---
title: "LangChain"
name: "LangChain"
description: "The most widely adopted LLM application framework - model/tool abstractions, integrations, and the on-ramp to LangGraph for stateful agents."
level: intermediate
readingTime: 6
category: orchestration
language: [python, javascript]
repo: "https://github.com/langchain-ai/langchain"
homepage: "https://www.langchain.com/"
docs: "https://docs.langchain.com/"
codeLicense: "MIT"
maturity: mature
maintainer: "LangChain, Inc."
supportsMcp: true
supportsMultiAgent: true
updated: 2026-06-30
tags: [framework, orchestration, integrations, python, javascript]
sources:
  - title: "LangChain (GitHub)"
    url: "https://github.com/langchain-ai/langchain"
    publisher: "LangChain"
    license: "MIT"
    accessed: "2026-06-30"
  - title: "LangChain Documentation"
    url: "https://docs.langchain.com/"
    publisher: "LangChain"
    accessed: "2026-06-30"
  - title: "LangChain + MCP"
    url: "https://docs.langchain.com/oss/python/langchain/mcp"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

**LangChain** is the framework most engineers meet first. It provides
standardized abstractions over models, prompts, tools, retrievers, and vector
stores, plus one of the largest ecosystems of integrations in the space. Its main
role today is as the **component and integration layer** beneath
[LangGraph](/frameworks/langgraph), which handles stateful agent orchestration.

## What it gives you

- **Model & tool abstractions** - swap providers behind a consistent interface;
  bind tools to chat models with structured output.
- **Integrations** - hundreds of connectors for vector DBs, document loaders,
  APIs, and, increasingly, [MCP](/frameworks/model-context-protocol) servers as a
  tool source.
- **Retrieval** - building blocks for [RAG](/patterns/graphrag): loaders,
  splitters, embeddings, retrievers.
- **A path to agents** - for anything stateful or multi-step, LangChain points
  you to LangGraph rather than the older chain/agent-executor abstractions.

## When to reach for it

- You want breadth of integrations and a large community.
- You're prototyping RAG or tool-using apps and value ready-made connectors.
- You expect to graduate to graph-based orchestration (LangGraph) as complexity
  grows.

## Tradeoffs

- **Abstraction cost.** The generality that helps prototyping can obscure what's
  actually sent to the model; for tight control some teams drop to the SDK level.
- **Churn.** A fast-moving API surface has historically meant migration work.
- **Right tool for the job.** For a single well-scoped agent, the raw provider
  SDK plus a small harness may be simpler; LangChain shines when integration
  breadth matters.

## Relationship to LangGraph

Think of LangChain as the **components** (models, tools, retrievers) and
[LangGraph](/frameworks/langgraph) as the **runtime** (durable, stateful,
multi-actor orchestration). They're designed to be used together and share
documentation at [docs.langchain.com](https://docs.langchain.com/).

## See also

- [Framework comparison matrix](/comparisons/framework-matrix)
- [Multi-agent orchestration](/patterns/multi-agent-orchestration)
