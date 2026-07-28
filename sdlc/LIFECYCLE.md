# Project lifecycle

This is the **project level** of the [four-level SDLC](README.md): the strategic
level sets the axis, the tactical level fills the backlog, the daily level frames
the day; this document is the method for executing one project.

Direction comes from [AXIS.md](../AXIS.md); this document is only the method for
moving along it. Every PR declares a horizon (short / mid / long) in its Purpose
section. The mix across PRs holds 80% short, 15% mid, 5% long.

Roles: **Architect** (goals, PRD/ADR review, acceptance LGTMs) and **AI implementers**.
People are referred to by role, never by name.

Two modes: the **current mode** (one PR at a time, in effect during initial setup) and
the **north star** (parallel multi-PR projects) that every practice aims toward.
Graduation: once the single-PR flow is mastered, PRs get chunked into longer projects.

## Current mode: one PR at a time

The flow is optimized for one fully-mastered step, in the three phases every
project passes through regardless of mode:

**Initiation**

1. Branch against `main`.
2. Discuss **PRD** and **ADR** with the architect; draft **acceptance criteria**.

**Agentic execution**, behind verification and quality gates:

3. Work in a dedicated **worktree**.
4. Pass all acceptance checks in **CI/CD**.

**Architectural review**

5. Architect reviews the acceptance checks; LGTM merges (squash) to `main`.

Every PR carries: Purpose, Tasks, Acceptance criteria (checkboxes), Evidence
(committed artifacts under `docs/evidence/`), Lessons learned. The PR template
enforces the structure and CI verifies it (`sdlc / pr-discipline`).

## Project shape

A project is **one or several PRs**, follow-ups included, sized at **several
hours of work** for the Architect with the AI agentic coding system. Every
project is **templated**; its full arc:

```text
intent (from the human Architect), captured in the project template:
  header restating mission, vision, and goal
  (the strategic touch and tactical outlook) + the specific challenge
  -> Architect review: product and architecture solution,
     handed off as PRD and spec (prd.md, ard.md, plan.md, handoff.md)
  -> agent team: implement, verify against the definition of done,
     present results, commit, wait for acceptance
  -> LGTM -> squash merge to main
  -> article
```

The template header carries the alignment down: mission, vision, and goal
restated from the strategic and tactical context, then the specific challenge
this project answers. The Architect reviews the templated project and produces
the product and architecture solution as the handoff pack: `prd.md`
(requirements), `ard.md` (architecture decisions and trade-offs), `plan.md`
(execution plan), `handoff.md` (implementation handoff). That initial spec goes
to the agents for implementation and verification: agents work **as a team**,
verify against the definition of done, present the results with evidence,
commit, and wait for acceptance; the Architect's LGTM merges to `main`.

A multi-PR project carries the pack as files; a single-PR project may carry the
PRD/ARD content in the PR body, as today - only repo-shaping decisions get a
standalone entry in [docs/adr/](../docs/adr/).

Every project ends in an **article** at the Architect and Builder levels, and
generating it triggers the [Atlas](../atlas/) update. The article **includes the
project's lessons**; its other sources are the PR bodies, their evidence, and the
[lessons](../docs/lessons/) entries. The [daily level](DAILY.md) aggregates the
day's articles into its executive and whitepaper publications.

## North star (direction, not yet in effect)

A **project** is one architect-approved iteration on `sdlc/<project>`, executed as
multiple worktrees running in parallel, returned to `main` as a single reviewed merge.

1. **Goal setting** - architect fixes scope, priorities, constraints. No code.
2. **PR0: the project pack** (`prd.md`, `ard.md`, `plan.md`, `handoff.md`) -
   documents only; 5-10 PRs with dependency graph and per-PR acceptance criteria.
   *Sizing: each PR under ~10 minutes of coding-model execution; whole project
   fits a 1-2 hour runway.*
3. **Execution** - PRs in dependency order across parallel worktrees; each PR CI-gated
   and leaves the branch working. **Whole-project review every 1-2 hours against
   the pack; 4 planning/review sessions per day.** Drift corrected or plan amended.
4. **Final PR: white paper** - goals, built, results, all PR links, lessons,
   deviations. This is the long form behind the project article.
5. **Merge acceptance via control surfaces** - merge PR accepted on the *running
   product*. The link targets below are the specific evidences required to approve:

   | Surface | Link target | Gate |
   |---|---|---|
   | PRODUCT | live env + walkthrough, feedback creates PR-linked tickets | LGTM |
   | API | replay dashboard: regression per endpoint + golden-set runs | LGTM |
   | ARCHITECTURE | executable notebook, before/after diagrams, live cells | LGTM |
   | CI/CD + REGRESSION | full pipeline with screenshot evidence | automatic |
   | WHITE PAPER | draft updated from review | LGTM |

   Tooling is pluggable; until it exists, the closest manual equivalent. Gates apply
   regardless.
6. **Release** - merge to main triggers: staging (operational evidence, human gate) ->
   canary -> ramped production. The lifecycle ends at operated production, not at merge.

## Standing rules (both modes)

- **Declare the horizon** - every PR states short, mid, or long in Purpose. Ambiguous
  work is short. Mid-horizon work without its short-horizon foundation is deferred.
- **No PII, ever** - CI-guarded, not just stated (docs, machine artifacts, tool output).
- **Evidence or it didn't happen.** Smoke scale fine; fabrication is not.
- **Review the review loop** - every mechanical review finding becomes a CI guard in
  the same correction PR.
- **Methodology docs are reference, not journal** - notes live in PR bodies and
  `docs/lessons/`; lessons aggregate into Atlas white papers.
