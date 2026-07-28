---
document: Directional Axis
scope: hsailabs core and apps
version: 0.1.0
status: Standing document, realigned each research cycle
last_realignment: 2026-07-28
next_realignment: 2027-01
---

# Directional axis

This is the standing answer to three questions. Strategic research sets the
**what**; the tech stack is the **how**; the mission is the **why**. Every
strategic package, PRD, and roadmap in this repository should be traceable to
one of the horizons below.

| Axis | Question | Where it is decided | Rate of change |
|------|----------|---------------------|----------------|
| **WHY** | What are we ultimately for? | [MISSION.md](../../MISSION.md) | Rarely |
| **WHAT** | Which direction do core and apps move? | This document, realigned from [research](#research-register) | Each cycle (~6 months) |
| **HOW** | What do we actually build with? | [Tech stack](../../README.md#tech-stack) | Continuously, but grounded |

## WHY - mission

> **Biological and synthetic intelligence expanding together toward the stars.**

Every horizon below is a step along that line. The near-term work is
deliberately ordinary infrastructure; the direction is not.

## Vision

An open lab where the loop from data to trained model to simulated world to
distributed evaluation to supervised operation to replay and back into training
runs reproducibly, in public, and can be pointed at progressively harder
physical and scientific problems - materials, energy, aerospace, robotics, and
eventually off-world operation.

The durable asset is that loop, not any single model:

```text
data or generated trajectories
        ↓
training and fine-tuning
        ↓
policy and model serving
        ↓
physics simulation
        ↓
distributed evaluation
        ↓
fault injection
        ↓
human supervision
        ↓
replay and qualification
        ↓
new training data
```

## WHAT - the directional axis

The July 2026 research cycle converges on one market transition:

> From models that generate information to systems that discover, manufacture,
> control, and operate physical assets.

Two findings set the direction for this repository specifically. The physical-AI
research ranks a **simulation and evaluation fabric** (scenario generation, large
simulation campaigns, fault injection, sim-to-real predictivity, hardware in the
loop, incident replay, release qualification) as its highest-demand,
shortest-time-to-market opportunity, and a **scientific-agent and autonomous-lab
control plane** immediately after it. Those two descriptions are what `core` is.
The infrastructure research adds the constraint that training and inference have
merged into one post-training loop, so a platform that separates them is already
behind.

The axis that follows:

```text
core  = the physical-AI simulation, evaluation, and supervision fabric
apps  = the proving grounds that create real requirements for it
```

Applications are chosen for how hard they push that fabric, not for domain
prestige. Core generalizes only what an application has actually demanded.

## Horizons

Horizons are capability stages, not delivery dates. Dates are the review points
where each stage is re-examined against fresh research.

### Short - through January 2027

**Reproducible AI/ML infrastructure at scale, on open models and open datasets.**

| Focus | Content |
|-------|---------|
| Practice | PyTorch, JAX, and Ray train / evaluate / serve loops that actually run |
| Substrate | Open-source models and public datasets only |
| Proof | Core Contract Pack v0.1, local runtime, Ray parity, replay, release gates |
| App | [AstraGrid](20260727-astragrid/) vertical slice: one seeded mission end to end |

Why this first: the infrastructure research shows the premium moving from
"can train a model" to "can make training efficient, recoverable, and
reproducible across accelerators," and from "can deploy an endpoint" to "can
operate distributed serving under latency and cost budgets." Nothing above this
horizon is credible without it.

Guardrail: local single-node semantics are the reference. Distribution changes
capacity, never meaning.

### Mid - through January 2028

**Physics-simulated environments and the sim-to-real control plane.**

| Focus | Content |
|-------|---------|
| Practice | MuJoCo/MJX and vectorized RL; domain randomization; fault injection at campaign scale |
| Substrate | Simulated environments with declared assumptions and evidence tiers |
| Proof | Distributed evaluation matrices, baseline-versus-learned comparison, sim-to-real predictivity as a measured quantity |
| Apps | AstraGrid robustness benchmarks; a second, deliberately different application ([NeuroDuet](../../apps/neuroduet/README.md)) to test that the contracts generalize |

Why here: the research names the unresolved problem plainly - simulation
fidelity does not guarantee real-world predictivity - and concludes that demand
will grow for evaluation systems that measure the **correlation** between
simulated and real outcomes, not simulated success alone. That measurement is a
core capability, and it is the bridge to the long horizon.

Guardrail: no simulated result is ever reported as physical validation. Evidence
tiers are part of every record.

### Long - beyond January 2028

**Materials, energy, aerospace, and robotics connected through one platform.**

| Focus | Content |
|-------|---------|
| Practice | Scientific agents, experiment planning, instrument and laboratory orchestration |
| Substrate | Scientific datasets and provenance graphs alongside simulation |
| Proof | Autonomous-laboratory scenarios; hardware-in-the-loop evidence; cross-embodiment and cross-simulator qualification |
| Direction | Remote and planetary operations: the environments where human intervention is delayed, expensive, dangerous, or unavailable |

Why this convergence: the research ranks materials × energy × autonomous labs,
materials × aerospace, robotics × energy infrastructure, and aerospace ×
robotics × sim-to-real among the highest-value intersections, and identifies the
scarce asset across all of them as reliable failure, recovery, and degradation
data - which is exactly what a simulation and evaluation fabric produces.

Guardrail: domain claims stay inside demonstrated evidence. The lab builds the
infrastructure between research and safe deployment; it does not claim validated
domain expertise it has not earned.

## HOW - the grounded stack

The stack is deliberately unglamorous and immediate. Full table in the
[root README](../../README.md#tech-stack). Its relationship to the horizons:

| Horizon | Load-bearing stack |
|---------|--------------------|
| Short | PyTorch, JAX, Ray, vLLM; open models and datasets; k3d, Kafka, ClickHouse, Prometheus, Grafana for evidence |
| Mid | MuJoCo/MJX, Isaac; Ray-distributed campaigns; LiveKit Meet for supervision; replay and telemetry at scale |
| Long | Scientific data adapters, instrument interfaces, hardware-in-the-loop rigs, provenance graphs |

Frameworks are adapters, not platform semantics. Any of them can be replaced
without changing what an experiment means.

## Research register

Direction is realigned from periodic market research. Each cycle reviews the
preceding window and produces an outlook; the horizons above are then adjusted.

| Cycle | Research | Window reviewed | Outlook |
|-------|----------|-----------------|---------|
| 2026-07 | [AI/ML infrastructure landscape](20260727-astragrid/research/20260727-AI-ML-INFRA-LANDSCAPE.md) | Jan-Jul 2026 | Aug 2026 - Jan 2027 |
| 2026-07 | [AI across science, energy, aerospace, physical systems](20260727-astragrid/research/20260727-AI-SCIENCE-ENERGY-AEROSPACE-PHYSICAL-SYSTEMS.md) | Jan-Jul 2026 | Aug 2026 - Jan 2028 |
| 2026-07 | [AI × bio/nanotech × advanced materials × BCI](20260728-neuroduet/research/20260728-NANOTECH-ADVANCED-BCI.md) | Jan-Jul 2026 | Aug 2026 - early 2028 |

Research documents cite secondary sources - market analyses, funding reports,
vendor benchmarks, and job postings. They record what the market appears to be
doing. They are inputs to direction, never evidence for a technical claim.

## Realignment cycle

Every ~6 months, aligned with the research review window:

1. Produce or refresh market research for the closing window.
2. Re-read this document against it. Name what changed and what did not.
3. Adjust the horizons - move capabilities between them, or retire them.
4. Record the realignment below, with what the research changed.
5. Re-scope open strategic packages against the adjusted horizons.

A horizon that survives a cycle unchanged is a finding worth recording, not a
skipped step.

## Realignment log

| Date | Cycle | Change |
|------|-------|--------|
| 2026-07-28 | 2026-07 | Initial axis established from the first research cycle. Short/mid/long horizons defined; core positioned as the physical-AI simulation and evaluation fabric; AstraGrid confirmed as first proving ground; NeuroDuet proposed as the generality test. |
