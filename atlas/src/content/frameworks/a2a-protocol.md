---
title: "A2A: Agent-to-Agent Communication"
name: "Agent-to-Agent (A2A)"
description: "Standards and libraries for agents to discover and talk to each other across systems — the interoperability layer above single-agent tool use."
level: advanced
readingTime: 6
category: protocol
language: [python]
homepage: "https://python-a2a.readthedocs.io/en/latest/"
docs: "https://python-a2a.readthedocs.io/en/latest/"
codeLicense: "See project"
maturity: beta
maintainer: "Open source community"
supportsMcp: true
supportsMultiAgent: true
updated: 2026-06-30
tags: [protocol, a2a, interoperability, multi-agent]
sources:
  - title: "python-a2a Documentation"
    url: "https://python-a2a.readthedocs.io/en/latest/"
    publisher: "python-a2a"
    accessed: "2026-06-30"
  - title: "Model Context Protocol — Introduction"
    url: "https://modelcontextprotocol.io/docs/getting-started/intro"
    publisher: "Anthropic / MCP"
    accessed: "2026-06-30"
---

Where [MCP](/frameworks/model-context-protocol) standardizes how an agent talks to
**tools and data**, **Agent-to-Agent (A2A)** approaches standardize how agents
talk to **each other** — discovery, capability advertisement, task delegation,
and message exchange across independently built systems.

## The problem A2A solves

Multi-agent systems built inside a single framework can share memory and call
each other directly. But real organizations have agents built by different teams,
in different stacks, possibly across trust boundaries. A2A defines a common
contract so a coordinator can:

- **Discover** what another agent can do (an advertised capability/"card").
- **Delegate** a task with structured inputs and receive structured results.
- **Exchange messages** in a consistent envelope, independent of each agent's
  internal implementation.

This is the interoperability layer that makes cross-team, cross-vendor
[multi-agent orchestration](/patterns/multi-agent-orchestration) tractable.

## `python-a2a`

The [`python-a2a`](https://python-a2a.readthedocs.io/en/latest/) library provides
a Python implementation for building and connecting A2A-speaking agents —
defining an agent's interface, exposing it as a service, and calling other agents
over the protocol. It commonly interoperates with MCP so an agent can both *use
tools* (MCP) and *be called by peers* (A2A).

## When to reach for it

- Agents are owned by different teams/services and must interoperate.
- You want loose coupling between agents rather than a monolithic framework.
- You need discovery and standardized delegation across a fleet.

## Tradeoffs & cautions

- **Coordination overhead is real.** A2A doesn't remove the classic multi-agent
  problems — conflicting goals, deadlock, cascading errors — it just gives them a
  transport. See [failure modes](/production/failure-modes).
- **Trust and security.** Cross-boundary agent calls widen the attack surface;
  authenticate peers, validate payloads, and scope permissions
  ([guardrails](/production/guardrails-safety)).
- **Maturing space.** A2A standards are evolving; expect change and pin versions.

## MCP vs. A2A — the one-liner

- **MCP** = agent ↔ tools/data (vertical integration).
- **A2A** = agent ↔ agent (horizontal interoperability).

Most non-trivial fleets end up using both.

## See also

- [Multi-agent orchestration](/patterns/multi-agent-orchestration)
- [Agent swarms](/patterns/agent-swarms)
