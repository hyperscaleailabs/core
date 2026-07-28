# Project lifecycle

This is the **project level** of the [four-level SDLC](README.md): the strategic
level sets the axis, the tactical level fills the backlog, the daily level frames
the day; this document is the method for executing one project.

Direction comes from [AXIS.md](../AXIS.md); this document is only the method for
moving along it. Every PR declares a horizon (short / mid / long) in its Purpose
section. The mix across PRs holds 80% short, 15% mid, 5% long.

Roles: the **Human Architect** (intent, epic/project definitions, reviews,
acceptance LGTMs) and four agent groups - **MGMT** (business analysis, product,
review, alignment decisions), **BUILDER** (implementation), **QA**
(verification and quality gates), **RESEARCHER/PUBLISHER** (summaries,
articles, publications). Roles overlap, yet the flow stays consistent during
project execution to establish the cadence. People are referred to by role,
never by name.

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
(committed artifacts under the touched module's `docs/evidence/`; top-level
`docs/` only for cross-module content), Lessons learned. The PR template
enforces the structure and CI verifies it (`sdlc / pr-discipline`).

## Project shape

A project is **one or several PRs**, follow-ups included, sized at **several
hours of work** for the Architect with the AI agentic coding system. Every
project is **templated**; its full arc:

```text
intent (from the human Architect), captured as a GitHub issue
  from the project template:
  links to mission, vision, and the strategic axis (links only)
  + the goal and the specific challenge
  + the acceptance template of every subproject touched
  -> Architect review: product and architecture solution,
     handed off as PRD and spec (prd.md, ard.md, plan.md, handoff.md)
  -> agent team: implement, verify against the definition of done,
     present results, commit, wait for acceptance
  -> acceptance review (trail on the issue and PR) -> LGTM
  -> article: analysis, summary, and the axis-alignment check
  -> final review -> squash merge to main
```

### Stages

1. The **Human Architect** defines the epic or project description, high
   level. It is captured as the project's GitHub issue.
2. **MGMT** (business analysis, product, review, alignment decisions) forms
   the structured suggested document group: `prd.md`, `ard.md`, and the spec
   (`plan.md`, `handoff.md`).
3. The **BUILDER** group of agents implements.
4. **QA** runs the verification cycle at the **PRODUCT, ARCHITECTURE, CODE,
   PRODUCTION, and DOCUMENTS** levels. Quality assurance is CI/CD at the
   module level (e.g. the `models` workflow on `models/**`) and at the
   overall monorepo integration level; the checks verify that every project
   has its GitHub issue and its PR with evidences, and its article, before
   merge into `main`. QA includes **regression testing**: a compact
   regression on defined example sets at module-appropriate scale (for
   models: golden-slice train / evaluate / infer against the previous
   accepted baseline, per [models/ACCEPTANCE.md](../models/ACCEPTANCE.md)),
   with the regression output attached as evidence.
5. **Cleanup and refinement**: every project removes the complexity it added
   before it is accepted. Simplify what the implementation grew, relocate
   misplaced artifacts (module evidence into the module - see
   [GRAPH.md](GRAPH.md#placement-rules)), repair vocabulary and link drift,
   compact documents, and **re-verify from the root README**: everything the
   project touched still traces from the entrance node with no inconsistency
   introduced. Gradual complexity increase and drift are the failure mode
   this stage exists to stop.
6. The **Human Architect and MGMT** review back and forth to accept the
   project. Comments and notes are collected on the GitHub issue and PR: they
   are the project's trail in the repository and part of the project history.
7. **RESEARCHER/PUBLISHER** follows up: reviews what changed, summarizes, and
   produces the **article** - MD format for the Architect and PM audiences,
   plus a platform-neutral `post.md` (LinkedIn format assumed) for the CTO /
   Architect / PM audiences. Special
   project types produce their level's artifacts instead: the daily summary
   produces the executive whitepaper (CTO) and the exec deck/brief (CEO); the
   weekly summary produces the weekly digest in the form of a short book
   (CTO and CEO).
8. **MGMT final review**: project goals, implementation, QA results,
   published materials, cross-module project checks, overall regression and
   integrity - prior to the merge and its follow-ups.

Context for every stage is pulled from the [repository graph](GRAPH.md):
enter at the node closest to the task, read outward only as needed.

**Every project has a GitHub issue**, opened at initiation from the project
template; it is the project's anchor, and every PR of the project references
it (`Issue: #<number>` in Purpose - the `sdlc / pr-discipline` check enforces
the field).

The template header stays light: **links only** to mission, vision, and the
strategic axis - never restated statements - plus the goal and the specific
challenge this project answers. The alignment lives at the end instead: the
article carries the check that alignment with the axis held during
implementation, at the strategic and tactical levels.

**Subproject acceptance templates**: each subproject (each top-level
directory) carries an `ACCEPTANCE.md` - its acceptance criteria template. The
project template includes the instantiated criteria of every subproject the
project touches; cross-project work spanning several subdirectories includes
each touched subproject's template. First instance:
[models/ACCEPTANCE.md](../models/ACCEPTANCE.md).

The Architect reviews the templated project and produces the product and
architecture solution as the handoff pack: `prd.md` (requirements), `ard.md`
(architecture decisions and trade-offs), `plan.md` (execution plan),
`handoff.md` (implementation handoff). That initial spec goes to the agents
for implementation and verification: agents work **as a team**, verify against
the definition of done, present the results with evidence, commit, and wait
for acceptance; the Architect's LGTM merges to `main`.

A multi-PR project carries the pack as files; a single-PR project may carry the
PRD/ARD content in the PR body, as today - only repo-shaping decisions get a
standalone entry in [docs/adr/](../docs/adr/).

**Module-bounded PRs**: work is bounded to a specific module or app (e.g.
`models`, `prod`, `apps/astragrid`) to keep boundaries clear and avoid
coupling. This lifecycle is the **generic process template**; each module
carries its specific adjustments in its `ACCEPTANCE.md` and module docs.
Artifacts follow the boundary: the article lands in the owning module
(`<module>/docs/articles/<date>-<project>/`), and cross-module narratives are
separate articles in their own PRs cross-referencing each other; genuinely
cross-module publications (whitepapers, weekly short books) land in
[docs/projects/](../docs/projects/) and [docs/weekly/](../docs/weekly/).

**Module CI/CD DAGs and two-tier regression**: every module has its own CI/CD
DAG. On every PR and merge, change detection (path filters) decides depth: a
**modified module** runs its full extensive verification - complete evidence
collection including the product screenshot and the regression run (for
models: the training, evaluation, and inference pipelines against the
accepted baseline) - while the **top API level** runs a less extensive
regression across all modules regardless of what changed.

Every project ends in an **article** as `article.md` (MD format, Architect
and PM audiences) plus `post.md` (platform-neutral social variant, LinkedIn
format assumed, CTO / Architect / PM audiences) under
`<module>/docs/articles/<date>-<project>/`; publishing it triggers the
[Atlas](../atlas/) update. The article contains the analysis and summary of
the project, **includes the project's lessons**, and **checks that alignment
with the axis remained** through implementation, at the strategic and
tactical levels. Its other sources are the PR bodies, their evidence, and the
lessons entries (module lessons in `<module>/docs/lessons/`, process lessons
in [docs/lessons/](docs/lessons/)). The [daily level](DAILY.md) aggregates
the day's articles into its executive and whitepaper publications.

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
   Written out in [PROMOTION.md](PROMOTION.md), which applies in both modes.

## Standing rules (both modes)

- **Declare the horizon** - every PR states short, mid, or long in Purpose. Ambiguous
  work is short. Mid-horizon work without its short-horizon foundation is deferred.
- **No PII, ever** - CI-guarded, not just stated (docs, machine artifacts, tool output).
- **Evidence or it didn't happen.** Smoke scale fine; fabrication is not.
- **Review the review loop** - every mechanical review finding becomes a CI guard in
  the same correction PR.
- **Methodology docs are reference, not journal** - notes live in PR bodies,
  module lessons in `<module>/docs/lessons/`, and process lessons in
  `sdlc/docs/lessons/`; lessons aggregate into Atlas white papers.
