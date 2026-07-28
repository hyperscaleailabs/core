---
title: "Strands Agents"
name: "Strands Agents"
description: "A model-driven, lightweight SDK that builds agents from three parts — model, tools, and prompt — and lets the model plan the loop, with MCP and multi-agent support."
level: intermediate
readingTime: 6
category: sdk
language: [python]
homepage: "https://strandsagents.com/"
docs: "https://strandsagents.com/"
codeLicense: "Apache-2.0"
maturity: beta
maintainer: "Open source (AWS-originated)"
supportsMcp: true
supportsMultiAgent: true
updated: 2026-06-30
tags: [sdk, model-driven, mcp, multi-agent, aws]
sources:
  - title: "Strands Agents"
    url: "https://strandsagents.com/"
    publisher: "Strands Agents"
    accessed: "2026-06-30"
  - title: "Model Context Protocol — Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
---

**Strands Agents** is a lightweight, **model-driven** SDK: you define an agent
from three ingredients — a **model**, a set of **tools**, and a **prompt** — and
let the model drive the loop rather than encoding the control flow yourself. The
philosophy is to keep the framework thin and lean on increasingly capable models
to plan and use tools.

## The model-driven idea

Where graph frameworks make you specify transitions, Strands bets that a capable
model can plan the sequence itself given good tools and a good prompt. You supply
the *what* (goal, tools); the model figures out the *how* (order of actions).
This keeps simple agents genuinely simple while still supporting complex ones.

## What it provides

- **Minimal agent definition** — model + tools + prompt, then run.
- **Tools** — Python callables as tools, plus
  [MCP](/frameworks/model-context-protocol) servers for external capabilities.
- **Multi-agent** — patterns for agents that call other agents (delegation,
  workflows), enabling [orchestration](/patterns/multi-agent-orchestration).
- **Provider flexibility** — works across multiple model providers.

## When to reach for it

- You want the smallest possible surface area to stand up a tool-using agent.
- You prefer to trust the model's planning over hand-authored control flow.
- You want MCP-native tooling without heavy framework ceremony.

## Tradeoffs

- **Model-dependent reliability.** Delegating control flow to the model means
  reliability tracks model capability; weaker models may need more scaffolding.
- **Less explicit control.** For workflows that must be deterministic and
  auditable step-by-step, an explicit-graph framework like
  [LangGraph](/frameworks/langgraph) offers tighter guarantees.

## How it fits the landscape

Strands sits at the "lightweight and model-driven" end of the spectrum, versus
the "explicit and durable" end occupied by LangGraph, with the
[Claude Agent SDK](/frameworks/claude-agent-sdk) offering a vendor-hardened
middle. Many teams prototype in a model-driven SDK and add explicit orchestration
only where a workflow demands determinism.

## See also

- [Framework comparison matrix](/comparisons/framework-matrix)
- [Agent swarms](/patterns/agent-swarms)
