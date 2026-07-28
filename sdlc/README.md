# SDLC

Software development lifecycle for the whole monorepo. This subproject defines the
top-level loops that every other subproject plugs into, plus the tooling that runs them.

The lifecycle operates at **four levels**. Each level has its own cadence, its own
artifacts, and a defined hand-off to the levels above and below it. Direction flows
down; lessons flow up. A level that neither informs nor is informed by its
neighbors is decoration.

| Level | Cadence | Defines | Publishes |
|-------|---------|---------|-----------|
| [Strategic](STRATEGIC.md) | 1 / 3 / 6-12 months; templated research monthly | The axis: mission, vision, method; short/mid/long horizons; iterative research on the platform and its apps | Strategic context and template for the weekly tactical review; realignment log; AXIS and DIRECTION updates |
| [Tactical](TACTICAL.md) | monthly, reviewed weekly | Architecture lifecycle; templated weekly review: strategic context + current system status -> the next ~20 projects as a prioritized dependency graph | Monthly architecture review; weekly digest (daily decks and whitepapers + market research) to Webinars, Atlas weekly overview, and stakeholder mailing lists |
| [Daily](DAILY.md) | daily | Priorities backlog: 3-5 projects drawn from the weekly graph | Scheduled daily update: executive deck (CEO level) and whitepaper (CTO level), to Atlas |
| [Project](LIFECYCLE.md) | per project: several hours, one or several PRs | Staged flow (Architect -> MGMT -> BUILDER -> QA -> acceptance review -> RESEARCHER/PUBLISHER -> MGMT final review); templated initiation anchored on a GitHub issue, with the acceptance template (`ACCEPTANCE.md`) of every touched subproject; evidence, CI/CD at module and monorepo levels | Article with lessons and the axis-alignment check (MD for Architect/PM + LinkedIn variant for CTO/Architect/PM), triggering Atlas updates |

Every level is **templated**: the initial templates are extracted from documents
already in the repository (starting with the strategic packages) and improved
with each iteration.

## Closing the loops

```text
direction:  axis -> epics -> weekly project graph -> daily 3-5 -> project scope
lessons:    project articles -> daily deck + whitepaper -> weekly digest
            -> monthly review -> realignment
```

Downward, each level scopes the one below it: the axis bounds what an epic may be,
epics bound projects, the weekly project graph bounds the day. Upward, every project
ends in an article that includes its [lessons](../docs/lessons/) and checks that
axis alignment held; the daily deck and whitepaper aggregate the day's articles
and name any drift from the axis, the weekly digest combines the dailies with
external market updates and research, the monthly architecture review aggregates
the month, and the strategic checkpoints consume the aggregate. Publications are
scheduled, not occasional - an unpublished level is an open loop.

## Status

The **operative level today is Project**: [LIFECYCLE.md](LIFECYCLE.md), current
mode, one PR at a time, enforced by the PR template, the `sdlc / pr-discipline` CI
check, and the repo skills (`pr-flow`, `pr-verify`, `lessons`). The strategic,
tactical, and daily documents are first-iteration scaffolding: references for
alignment now, activated as their cadences begin. Each document carries its own
activation status.

## Development-to-production loops

Highest level loops, each with its own sub-loops:

1. **Development cycle** (defined here, applies to all subprojects): iterative
   development with a rotating AI Architect review on PRs, cycling across projects.
2. **Models**: a group of agents training, benchmarking, and optimizing models, with
   explicit work planning, execution, and acceptance criteria at the end. Accepted
   models are published for use by the other subprojects.
3. **Prod**: pre-release simulation with internal dashboard and configuration,
   promotion to canary, then ramped-up production.
4. **Agents**: run as APIs and LiveKit agents, pluggable and configurable into Meet.
5. **D-twins**: containerized service with autoscale and startup/shutdown orchestration
   via API and command line, operable by agents.
6. **Atlas**: publishes the lifecycle's aggregated outputs - project articles, daily
   slides and whitepaper summaries, and white papers built from lessons learned.
7. **Deployment**: models, prod, meet, agents, dtwins, and atlas are exposed as
   Kubernetes services/deployments, internal or external per the access tiers in the
   root [README](../README.md).

Status: placeholder. Structure and code migrate here in upcoming iterations.
See the root [README](../README.md) for repository rules (public repo: no PII, squash merges, policy checks required).
