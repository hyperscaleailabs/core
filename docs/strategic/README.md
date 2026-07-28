# Strategic

Strategic work sets **direction**: what core and the apps move toward, and why.
It does not decide implementation - that is the tech stack and the SDLC.

| Question | Answered by |
|----------|-------------|
| **WHY** - what the lab is ultimately for | [MISSION.md](../../MISSION.md) |
| **WHAT** - the directional axis and horizons | [DIRECTION.md](DIRECTION.md) |
| **HOW** - what we build with, right now | [Tech stack](../../README.md#tech-stack) |

[DIRECTION.md](DIRECTION.md) is the standing document. It is realigned every
research cycle (~6 months) and carries the short, mid, and long horizons that
every package below should trace back to.

## How a cycle runs

```text
market research  →  realign DIRECTION.md  →  scope packages  →  ADRs  →  SDLC
```

Research reviews the closing window and produces an outlook. The horizons in
DIRECTION.md are adjusted against it and the realignment is logged. Packages are
then scoped or re-scoped. Approved decisions graduate into [ADRs](../adr/), and
implementation follows the lifecycle in [sdlc/](../../sdlc/).

## Package layout

One directory per initiative, `YYYYMMDD-<slug>/`, containing any of:

```text
README.md              package index: scope, contents, reading order
research/              market research inputs for the cycle
core/                  core-side prd, ref-architecture, pland, handoff
apps/<app>/            app-side prd, ref-architecture, pland, handoff
                       or direction.md for proposed, unscheduled applications
```

A full package carries four documents per affected project: `prd.md`
(requirements), `ref-architecture.md` (suggested architecture), `pland.md`
(execution plan), and `handoff.md` (implementation handoff). Early-stage
directions carry only `direction.md` until they are scheduled.

Packages are drafts for review. Their status field says how far they have moved.

## Packages

| Package | Scope | Horizon | Status |
|---------|-------|---------|--------|
| [`20260727-astragrid/`](20260727-astragrid/) | Core platform contracts and the AstraGrid flagship application, plus the AI/ML infrastructure and physical-systems research that set the axis | Short into mid | Draft for implementation |
| [`20260728-neuroduet/`](20260728-neuroduet/) | NeuroDuet and SignalMatter neural-interface directions, plus bio/nanotech/materials/BCI research. Tests whether core contracts generalize to a second application | Mid | Proposed, not scheduled |

## Research register

Full register with review and outlook windows in
[DIRECTION.md](DIRECTION.md#research-register).

| Cycle | Research | Package |
|-------|----------|---------|
| 2026-07 | AI/ML infrastructure landscape | [`20260727-astragrid/research/`](20260727-astragrid/research/) |
| 2026-07 | AI across science, energy, aerospace, and physical systems | [`20260727-astragrid/research/`](20260727-astragrid/research/) |
| 2026-07 | AI × bio/nanotech × advanced materials × BCI | [`20260728-neuroduet/research/`](20260728-neuroduet/research/) |

Research documents cite secondary sources: market analyses, funding reports,
vendor benchmarks, and job postings. They are inputs to direction, never evidence
for a technical claim. Anything asserted about the lab's own systems needs
reproducible evidence, per the repository rule that evidence or it did not happen.
