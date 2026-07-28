---
title: "The Pre-Agentic Era: Everything We Built Before the Loop"
description: "Expert systems, RPA, dialogue managers, and orchestration pipelines already solved parts of the agent problem. What carries forward, and what the LLM actually changed."
level: beginner
readingTime: 10
order: 2
updated: 2026-06-30
tags: [history, expert-systems, rpa, orchestration, context]
sources:
  - title: "Multi-Agent Planning in AI"
    url: "https://www.geeksforgeeks.org/artificial-intelligence/multiagent-planning-in-ai/"
    publisher: "GeeksforGeeks"
    accessed: "2026-06-30"
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
---

The 2023–2026 wave of AI agents can feel like it arrived from nowhere. It didn't.
"An autonomous system that senses, decides, and acts toward a goal" is a
**decades-old** definition. Understanding what came before tells you which
problems are genuinely new (few) and which are old problems wearing new clothes
(most). It also tells you which battle-tested ideas to steal.

## The classical agent, before LLMs

The **sense–plan–act** loop is foundational to classical AI and robotics. An
agent perceives its environment, maintains some model of the world, selects an
action via a policy or planner, acts, and repeats. Russell & Norvig were teaching
"rational agents" as the organizing metaphor for AI long before transformers
existed. The modern LLM agent is a specific, powerful instantiation of that same
loop — with a language model as the policy.

Multi-agent systems are equally old: distributed problem solving, the
contract-net protocol for task allocation, blackboard architectures, and
BDI (belief–desire–intention) agents all predate the current wave. **Multi-agent
planning** — coordinating several agents whose actions interfere, with shared or
conflicting goals — is a mature subfield with known hard problems (coordination,
conflict resolution, credit assignment) that reappear unchanged when you wire up
LLM sub-agents today.

## Four ancestors you'll recognize in every "agent" demo

### 1. Expert systems (1970s–80s)
Rule engines like MYCIN encoded human expertise as `if–then` rules and chained
them with an inference engine. They were **explainable** (you could trace the
rules that fired) and **brittle** (knowledge acquisition was manual and didn't
generalize). The modern echo: a prompt full of policies is a soft, probabilistic
rule base. The old lesson still bites — rules that aren't maintained rot.

### 2. Robotic Process Automation (2000s–2010s)
RPA bots automate deterministic, repetitive UI/workflow tasks by scripting exact
click paths. They are reliable when the environment is stable and shatter the
moment a form field moves. LLM agents are, in one framing, **RPA that can
tolerate variation** — they read the screen or API and adapt. The tradeoff: you
swap brittleness for unpredictability.

### 3. Dialogue systems and chatbots
Intent classification + slot filling + a dialogue manager (a hand-authored state
machine) powered a generation of assistants. The dialogue manager *is* the
control flow — the pre-LLM version of a [workflow](/foundations/what-is-an-agent).
LLMs collapsed the intent/slot machinery into one model but inherited the same
need for state management and grounding.

### 4. Orchestration and data pipelines
Airflow, Step Functions, and BPM engines gave us durable, observable,
retry-able **DAGs of tasks**. This is the single most underused body of prior art
in agent engineering. When people rediscover that long-running agents need
checkpointing, idempotency, retries, and human-in-the-loop approvals, they are
rediscovering workflow orchestration — which is why frameworks like
[LangGraph](/frameworks/langgraph) look a lot like durable state machines.

## What actually changed with the LLM

Three things are genuinely new, and they're the reason this wave is different:

1. **Open-ended natural-language understanding and generation.** The policy no
   longer needs a fixed ontology of intents. It can handle inputs nobody
   enumerated in advance.
2. **In-context learning.** Behavior can be steered with examples and
   instructions at runtime, without retraining — turning "programming" into
   "prompting and context engineering."
3. **General tool use via function calling.** One model can drive arbitrary APIs
   described to it in text, which is what makes the [agent
   loop](/foundations/what-is-an-agent) general-purpose rather than task-specific.

## What did *not* change (and you shouldn't pretend it did)

- **Coordination is still hard.** Multi-agent planning's classic problems —
  conflicting goals, deadlock, communication overhead — apply directly to
  [agent swarms](/patterns/agent-swarms).
- **State, durability, and idempotency still matter.** Long-running agents need
  the same guarantees your payment pipeline needs.
- **Brittleness didn't vanish; it moved.** Expert systems failed by omission;
  agents fail by confident improvisation ([failure
  modes](/production/failure-modes)).
- **Evaluation is still the bottleneck.** You can't manage what you can't
  measure — see [evaluation](/production/evaluation).

## The takeaway for architects

Treat an LLM agent as a **new kind of policy inside an old kind of system**. Wrap
it in the orchestration, observability, and guardrails that decades of production
engineering already taught us to build. The teams that ship reliable agents are
usually the ones who recognized how much of the problem was already solved — and
reused it.

## Next

- [From LLMs to agents](/foundations/llm-to-agent-evolution) — the capability
  jump that made the loop viable.
- [Multi-agent orchestration](/patterns/multi-agent-orchestration) — the modern
  form of classical distributed problem solving.
