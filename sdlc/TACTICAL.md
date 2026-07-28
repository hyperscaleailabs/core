# Tactical level

Cadence: **monthly, reviewed weekly**. The tactical level turns strategic
packages into an ordered stream of executable projects. It expresses the
architecture lifecycle on a monthly rhythm and runs a **templated weekly
review** whose outcome feeds the [daily level](DAILY.md).

## Vocabulary

| Unit | Size | Defined at |
|------|------|------------|
| **Epic** | Large scope: a strategic package milestone or architecture move; weeks of projects | Monthly |
| **Project** | One architect-approved iteration per [LIFECYCLE.md](LIFECYCLE.md); several hours of work for the Architect with the AI agentic coding system | Weekly review |

## Monthly - architecture lifecycle

1. **Architecture review**: read the month's project articles, daily and weekly
   publications, and [lessons](../docs/lessons/) against the current architecture
   and [ADRs](../docs/adr/). Name what held and what fought back.
2. **Epic definition**: define or re-scope epics from the open strategic packages
   (their prd / ref-architecture / pland documents). Every epic declares its
   package, its horizon, and the architecture it advances.
3. **ADR graduation**: decisions surfaced by the month's work graduate into
   [docs/adr/](../docs/adr/).
4. **Hand-off up**: the review digest goes to the strategic
   [alignment check](STRATEGIC.md#checkpoints).

## Weekly - tactical review and digest

The weekly tactical review is **templated**. Its inputs:

- the **strategic context** and the strategic template from the monthly
  [research iteration](STRATEGIC.md#templated-iterative-research) - both are
  also used to frame discussions with reasoning assistants;
- a **current system status summary** of core and the apps.

Reasoning over these against the active epics produces the review's outcome:

1. The **next ~20 suggested projects**, formed as a **dependency graph with
   priorities**. Each project is sized at several hours of work for the
   Architect with the AI agentic coding system; the 80/15/5 horizon mix is held
   by the graph as a whole, not by any single project.
2. The top of the graph - highest priority, dependencies satisfied - feeds the
   [daily level](DAILY.md) its 3-5 projects.
3. **Weekly digest**: combine the week's daily summaries (CEO decks and CTO
   whitepapers) with **external market updates and research** into the tactical
   weekly digest, in the form of a **short book** (CTO and CEO audiences).
   Published to **Webinars** and the **Atlas weekly overview**, generating
   artifacts, and shared via mailing lists to notify external stakeholders.

## Artifacts

First iteration: the review template, epic register, and weekly project graph
are markdown documents kept in this directory once the cadence activates;
tracker tooling is pluggable and can replace them without changing the method.
Epics reference strategic packages, projects reference epics, PRs reference
projects - the chain must be walkable in both directions.

## Status

First-iteration scaffolding. Epics currently live implicitly in the strategic
packages' pland documents; the explicit register and the weekly cadence activate
with the first monthly architecture review.
