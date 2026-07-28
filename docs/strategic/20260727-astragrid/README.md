---
document: Package Index
package: HSAILabs Core and AstraGrid Initiation Documents
version: 0.1.0
status: Draft for implementation and iterative refinement
date: 2026-07-27
---

# HSAILabs Core and AstraGrid Documentation Package

This package separates the reusable **HSAILabs/core platform** from the flagship
**AstraGrid application**.

HSAILabs/core provides reusable contracts and capabilities for model training,
serving, simulation, distributed evaluation, agent orchestration, human
supervision, telemetry, replay, governance, and infrastructure.

AstraGrid consumes a selected subset of those capabilities to demonstrate one
clear mission:

> Through a LiveKit Meet room, a human directs a simulated rover to inspect and
> restore a degraded lunar power or thermal node, verify recovery, and return
> while preserving a safe energy reserve.

The application creates real requirements for the platform. The platform
generalizes recurring requirements into reusable contracts without importing
AstraGrid-specific domain logic.

## Package structure

```text
docs/strategic/20260727-astragrid/
├── README.md
├── research/
│   ├── 20260727-AI-ML-INFRA-LANDSCAPE.md
│   └── 20260727-AI-SCIENCE-ENERGY-AEROSPACE-PHYSICAL-SYSTEMS.md
├── core/
│   ├── handoff.md
│   ├── pland.md
│   ├── prd.md
│   └── ref-architecture.md
└── apps/
    └── astragrid/
        ├── handoff.md
        ├── pland.md
        ├── prd.md
        └── ref-architecture.md
```

## Research inputs

Two market-research documents from the 2026-07 cycle set the direction this
package implements:

| Document | Reviews | Outlook |
|----------|---------|---------|
| [AI/ML infrastructure landscape](research/20260727-AI-ML-INFRA-LANDSCAPE.md) | Jan-Jul 2026 | Aug 2026 - Jan 2027 |
| [AI across science, energy, aerospace, physical systems](research/20260727-AI-SCIENCE-ENERGY-AEROSPACE-PHYSICAL-SYSTEMS.md) | Jan-Jul 2026 | Aug 2026 - Jan 2028 |

Their combined conclusion - that a physical-AI simulation and evaluation fabric
is the highest-demand, shortest-time-to-market opportunity, and that training and
inference have merged into one post-training loop - is what positions core the way
this package's PRD describes it. The axis derived from them is in
[DIRECTION.md](../DIRECTION.md); this package sits on the short horizon and reaches
into the mid.

Research cites secondary sources and is an input to direction, never evidence for
a technical claim.

## Recommended reading order

1. Both documents in `research/` (or the summary in [DIRECTION.md](../DIRECTION.md))
2. `core/prd.md`
3. `core/ref-architecture.md`
4. `apps/astragrid/prd.md`
5. `apps/astragrid/ref-architecture.md`
6. Both `pland.md` files
7. Both `handoff.md` files

## Shared design rules

1. Core never imports application code.
2. Applications declare required and optional core capabilities.
3. Contracts are versioned independently from implementations.
4. Local single-node execution is required before distributed execution.
5. Simulation evidence is never described as physical-world validation.
6. Learned policies operate behind deterministic safety constraints.
7. Every experiment records datasets, models, policies, environment versions,
   seeds, parameters, interventions, and outcomes.
8. AstraGrid is a proving ground, not the definition of the platform.
9. Core improvements should benefit at least one additional plausible
   application or remain explicitly experimental.
10. Progress is demonstrated through reproducible runs, benchmarks, replays,
    architecture decisions, and public technical artifacts.

## Next proposed action

Review the two PRDs together and approve the first contract-review gate:
`ApplicationManifest`, `Environment`, `Policy`, `Trajectory`, and
`ExperimentRecord` (per the core plan), followed by the remaining contracts of
Core Contract Pack v0.1 (see `core/handoff.md`).
