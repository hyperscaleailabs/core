# Tactical level

Cadence: **monthly, broken down to weekly**. The tactical level turns strategic
packages into an ordered stream of executable projects. It expresses the
architecture lifecycle on a monthly rhythm and maintains the weekly project
backlog that feeds the [daily level](DAILY.md).

## Vocabulary

| Unit | Size | Defined at |
|------|------|------------|
| **Epic** | Large scope: a strategic package milestone or architecture move; weeks of projects | Monthly |
| **Project** | One architect-approved iteration per [LIFECYCLE.md](LIFECYCLE.md); hours to days | Weekly breakdown |

## Monthly - architecture lifecycle

1. **Architecture review**: read the month's project articles, daily summaries,
   and [lessons](../docs/lessons/) against the current architecture and
   [ADRs](../docs/adr/). Name what held and what fought back.
2. **Epic definition**: define or re-scope epics from the open strategic packages
   (their prd / ref-architecture / pland documents). Every epic declares its
   package, its horizon, and the architecture it advances.
3. **ADR graduation**: decisions surfaced by the month's work graduate into
   [docs/adr/](../docs/adr/).
4. **Hand-off up**: the review digest goes to the strategic
   [alignment check](STRATEGIC.md#checkpoints).

## Weekly - project backlog and digest

1. Break the active epics into projects sized for the
   [project lifecycle](LIFECYCLE.md), each with a draft goal, a horizon, and a
   rough acceptance shape.
2. Order the backlog: dependencies first, then horizon weighting - the 80/15/5
   mix is held by the backlog as a whole, not by any single project.
3. The top of the backlog feeds the daily level its 3-5 projects.
4. **Weekly digest**: aggregate the week's daily whitepapers and decks and
   combine them with the week's **market research** into the tactical weekly
   digest. Published to **Webinars** and the **Atlas weekly overview**, and
   shared via mailing lists to notify external stakeholders.

## Artifacts

First iteration: the epic register and weekly backlog are markdown tables kept in
this directory once the cadence activates; tracker tooling is pluggable and can
replace them without changing the method. Epics reference strategic packages,
projects reference epics, PRs reference projects - the chain must be walkable in
both directions.

## Status

First-iteration scaffolding. Epics currently live implicitly in the strategic
packages' pland documents; the explicit register and the weekly cadence activate
with the first monthly architecture review.
