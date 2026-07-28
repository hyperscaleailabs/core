# SDLC lifecycle

Direction comes from [AXIS.md](../AXIS.md); this document is only the method for
moving along it. Every PR declares a horizon (short / mid / long) in its Purpose
section. The mix across PRs holds 80% short, 15% mid, 5% long.

Roles: **Architect** (goals, PRD/ADR review, acceptance LGTMs) and **AI implementers**.
People are referred to by role, never by name.

Two modes: the **current mode** (one PR at a time, in effect during initial setup) and
the **north star** (parallel multi-PR projects) that every practice aims toward.
Graduation: once the single-PR flow is mastered, PRs get chunked into longer projects.

## Current mode: one PR at a time

The flow is optimized for one fully-mastered step:

1. Branch against `main`.
2. Discuss **PRD** and **ADR** with the architect; draft **acceptance criteria**.
3. Work in a dedicated **worktree**.
4. Pass all acceptance checks in **CI/CD**.
5. Architect reviews the acceptance checks; LGTM merges (squash) to `main`.

Every PR carries: Purpose, Tasks, Acceptance criteria (checkboxes), Evidence
(committed artifacts under `docs/evidence/`), Lessons learned. The PR template
enforces the structure and CI verifies it (`sdlc / pr-discipline`).

## North star (direction, not yet in effect)

A **project** is one architect-approved iteration on `sdlc/<project>`, executed as
multiple worktrees running in parallel, returned to `main` as a single reviewed merge.

1. **Goal setting** - architect fixes scope, priorities, constraints. No code.
2. **PR0: PRD + ADR + PLAN** - documents only; 5-10 PRs with dependency graph and
   per-PR acceptance criteria. *Sizing: each PR under ~10 minutes of coding-model
   execution; whole project fits a 1-2 hour runway.*
3. **Execution** - PRs in dependency order across parallel worktrees; each PR CI-gated
   and leaves the branch working. **Whole-project review every 1-2 hours against
   PRD/ADR/plan; 4 planning/review sessions per day.** Drift corrected or plan amended.
4. **Final PR: white paper** - goals, built, results, all PR links, lessons, deviations.
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
