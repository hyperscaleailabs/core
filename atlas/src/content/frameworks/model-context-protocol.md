---
title: "Model Context Protocol (MCP)"
name: "Model Context Protocol"
description: "The open standard for connecting models to tools, data, and prompts - the 'USB-C for AI' that makes integrations portable across hosts and models."
level: intermediate
readingTime: 7
category: protocol
language: [python, typescript, other]
repo: "https://github.com/mcp"
homepage: "https://modelcontextprotocol.io/"
docs: "https://modelcontextprotocol.io/docs/getting-started/intro"
codeLicense: "MIT (spec & SDKs)"
maturity: stable
maintainer: "Anthropic + open community"
supportsMcp: true
supportsMultiAgent: false
updated: 2026-06-30
tags: [protocol, mcp, tools, integrations, standard]
sources:
  - title: "Model Context Protocol - Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
  - title: "MCP (GitHub organization)"
    url: "https://github.com/mcp"
    publisher: "Model Context Protocol"
    accessed: "2026-06-30"
  - title: "LangChain + MCP"
    url: "https://docs.langchain.com/oss/python/langchain/mcp"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

The **Model Context Protocol (MCP)** is an open standard for connecting AI
applications to external systems - tools, data sources, and reusable prompts.
Often described as "USB-C for AI," it replaces N×M bespoke integrations with a
single protocol: build an MCP **server** once, and any MCP-capable **host** (an
IDE, a chat app, an agent framework) can use it.

## The core abstractions

MCP defines a client–server protocol with a few primitives a server can expose:

- **Tools** - callable functions the model can invoke (the action surface).
- **Resources** - data the host can read into context (files, records, docs).
- **Prompts** - reusable, parameterized prompt templates the host can surface.

A **host** application runs MCP **clients** that connect to MCP **servers**.
Transport can be local (stdio) or networked, so servers run in-process, as
subprocesses, or as remote services.

## Why it matters for agents

- **Portability.** A tool you expose via MCP works across
  [LangChain](/frameworks/langchain)/[LangGraph](/frameworks/langgraph),
  the [Claude Agent SDK](/frameworks/claude-agent-sdk),
  [Strands](/frameworks/strands-agents), IDEs, and more - no per-framework glue.
- **Separation of concerns.** Tool authors and agent authors work independently
  against a stable contract.
- **Ecosystem.** A growing library of servers (databases, browsers, SaaS APIs,
  filesystems) means less integration code to own.

## When to use it

- You're integrating more than one or two external systems.
- You want tools reusable across multiple agents/hosts.
- You want a clean permission and audit boundary around external capabilities.

## Tradeoffs & considerations

- **Operational surface.** Each server is a component to run, secure, and
  monitor. Treat MCP servers as production services.
- **Security.** Tools can take real actions; scope permissions, validate inputs,
  and audit calls - see [guardrails & safety](/production/guardrails-safety).
  Untrusted servers are a supply-chain and prompt-injection risk.
- **Not an agent framework.** MCP standardizes *connectivity*, not orchestration.
  You still choose a harness/framework to run the loop.

## Getting started

The [official intro](https://modelcontextprotocol.io/docs/getting-started/intro)
walks through building a first server and connecting a host; the
[MCP GitHub org](https://github.com/mcp) hosts SDKs and reference servers.
Framework bridges like [LangChain's MCP
support](https://docs.langchain.com/oss/python/langchain/mcp) let you consume MCP
tools directly.

## See also

- [A2A protocol](/frameworks/a2a-protocol) - the complementary agent-to-agent
  standard.
- [Tool use](/patterns/tool-use) - designing the tools you expose over MCP.
