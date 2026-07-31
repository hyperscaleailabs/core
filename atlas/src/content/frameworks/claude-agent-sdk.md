---
title: "Claude Agent SDK"
name: "Claude Agent SDK"
description: "Anthropic's SDK for building agents on the same harness that powers Claude Code - tool use, MCP, subagents, and long-running loops with production ergonomics."
level: intermediate
readingTime: 6
category: sdk
language: [python, typescript]
homepage: "https://code.claude.com/docs/en/agent-sdk/overview"
docs: "https://code.claude.com/docs/en/agent-sdk/overview"
codeLicense: "See vendor terms"
maturity: stable
maintainer: "Anthropic"
supportsMcp: true
supportsMultiAgent: true
created: 2026-06-30
updated: 2026-07-01
tags: [sdk, anthropic, claude, mcp, subagents]
sources:
  - title: "Claude Agent SDK - Overview"
    url: "https://code.claude.com/docs/en/agent-sdk/overview"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
  - title: "Building with the Claude API (Anthropic Academy)"
    url: "https://anthropic.skilljar.com/claude-with-the-anthropic-api/"
    publisher: "Anthropic Academy"
    accessed: "2026-07-01"
---

> **Updated 2026-07-01** - added a pointer to the API primitives underneath the
> SDK (source: [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api/)).

The **Claude Agent SDK** exposes the agent harness Anthropic built for Claude
Code so you can build your own agents on top of it. Its value proposition is a
**batteries-included, production-tested loop**: the tool-execution cycle, context
management, permissions, and subagents are handled for you, so you focus on tools
and instructions rather than rebuilding the runtime.

## What it provides

- **The agent loop** - a robust decide→act→observe runtime with sensible stopping
  behavior, retries, and streaming.
- **Tool use** - first-class function calling, including file, shell, and code
  tools, with a **permission model** for gating risky actions.
- **[MCP](/frameworks/model-context-protocol) support** - connect external tools
  and data via MCP servers rather than bespoke glue.
- **Subagents** - spawn specialized child agents for delegated tasks, enabling
  [orchestrator–worker](/patterns/multi-agent-orchestration) topologies.
- **Context management** - built-in handling of long sessions, aligned with
  Anthropic's guidance on [context
  engineering](/patterns/context-engineering).

## When to reach for it

- You're targeting Claude models and want the shortest path to a solid harness.
- You value the permission/guardrail model for tools that touch a filesystem,
  shell, or external APIs.
- You want subagents and MCP without wiring an orchestration framework yourself.

## Tradeoffs

- **Model alignment.** It's designed around Claude; if you need heavy
  multi-provider routing, a provider-agnostic framework may fit better.
- **Opinionated harness.** You get Anthropic's design decisions - a benefit for
  speed, a constraint if your requirements diverge.

## How it fits the landscape

Where [LangGraph](/frameworks/langgraph) gives you a general graph runtime and
[Strands](/frameworks/strands-agents) a model-driven loop, the Claude Agent SDK
gives you the specific, hardened harness behind a shipping agentic product. It
pairs naturally with Anthropic's engineering guidance on
[effective agents](https://www.anthropic.com/engineering/building-effective-agents)
and [long-running harnesses](/production/long-running-harnesses).

## Learn the primitives underneath

The SDK is a hardened wrapper over the raw Claude API. If you want to understand
what it's automating - messages and context, tool use, extended thinking, prompt
caching, and building MCP servers/clients - [Building with the Claude
API](/foundations/building-with-the-claude-api) walks those primitives bottom-up,
following Anthropic Academy's free course. Knowing them is what lets you debug the
SDK rather than treat it as a black box.

## See also

- [Framework comparison matrix](/comparisons/framework-matrix)
- [Guardrails & safety](/production/guardrails-safety)
