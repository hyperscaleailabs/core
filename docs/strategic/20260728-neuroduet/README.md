---
document: Package Index
package: Neural-Interface Direction and Market Research
version: 0.1.0
status: Direction and research; no PRD, plan, or handoff yet
date: 2026-07-28
---

# Neural-interface package

This package holds the research and the deferred direction behind a second
application for HSAILabs/core, chosen to test whether the core contracts
generalize beyond the embodied-rover shape of
[AstraGrid](../20260727-astragrid/). No PRD, plan, or handoff exists yet.

NeuroDuet itself has landed as an application: its direction document is
[`apps/neuroduet/README.md`](../../../apps/neuroduet/README.md) at the repository
root, the same place AstraGrid's golden use case lives. This package is not a
second copy of it.

## Package structure

```text
docs/strategic/20260728-neuroduet/
├── README.md
├── research/
│   └── 20260728-NANOTECH-ADVANCED-BCI.md
└── apps/
    └── signalmatter/
        └── direction.md
```

## Contents

| Document | Project | Status |
|----------|---------|--------|
| [`research/20260728-NANOTECH-ADVANCED-BCI.md`](research/20260728-NANOTECH-ADVANCED-BCI.md) | Market research: AI × bio/nanotech × advanced materials × BCI, Jan-Jul 2026 review with outlook to early 2028 | Input |
| [`apps/neuroduet/README.md`](../../../apps/neuroduet/README.md) | NeuroDuet: open language-aligned BCI simulation and evaluation lab. Two people converse through Meet while virtual brain models visualize the predicted cortical response to each utterance | Proposed golden application, lives under `apps/` |
| [`apps/signalmatter/direction.md`](apps/signalmatter/direction.md) | SignalMatter: neural-interface reliability lab studying how decoders behave as recording conditions and interface properties degrade | Deferred, depends on NeuroDuet |

## Why this direction

The research identifies chronic neural interfaces as fundamentally a materials
and reliability problem rather than a decoding-algorithm problem, which places it
on the same axis as the rest of the lab: signal degradation over time, evaluation
under drift, and reproducible evidence. That makes it a genuine test of whether
core contracts written for a rover mission survive an application with no robot,
no terrain, and no battery - while still exercising training, serving,
distributed evaluation, replay, and human supervision.

Both documents visualize or simulate **model-predicted** activity from open
datasets. Neither collects, measures, or reconstructs a participant's own brain
signals, and the scientific-integrity boundary in the NeuroDuet direction
document is load-bearing, not decorative.

## Relationship to direction

Mid-horizon in [DIRECTION.md](../DIRECTION.md): the second application that tests
contract generality. Not a competing flagship - AstraGrid remains the first
proving ground.

## Next proposed action

Do not open a PRD until the AstraGrid vertical slice and Core Contract Pack v0.1
exist. Sequencing a second application before the first one has exercised the
contracts inverts the dependency this package is meant to test. Revisit at the
next realignment: if the contracts held for one application, this is the cheapest
way to find out whether they hold for two.
