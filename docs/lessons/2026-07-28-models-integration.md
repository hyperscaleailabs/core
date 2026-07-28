# Lessons from the models integration project

Source: [issue #7](https://github.com/hyperscaleailabs/core/issues/7) and
[PR #8](https://github.com/hyperscaleailabs/core/pull/8) (merged `820dc85`),
the first full practice run of the staged project lifecycle. Each lesson
states the correction and where it is now codified.

## L1. Migrated docs carry their old repository's skeleton

The moved subproject referenced its standalone repo's `SDLC.md` and
`CLAUDE.md`, its command examples silently assumed the old repo root, and its
implementation plan presented the old repo's PR numbers as current state.

**Lesson:** integration has a sweep checklist beyond the PII scan: old repo's
filenames, CWD assumptions in command examples, and historical
plans/checkboxes. Historical records get a preface, never a rewrite.

**Codified:** [models/README.md](../../models/README.md) module-relative
command note; prefaces on the historical plan and lessons files; recorded
here for the next integration.

## L2. Evidence has a home, and misplacement is a broken graph edge

Module evidence (a models CI run, a golden-pull transcript) was first
committed to top-level `docs/evidence/`, where nothing that needs it would
look for it.

**Lesson:** evidence lives with what it evidences - module evidence in
`<module>/docs/evidence/`, process and cross-module evidence at the top. The
placement question is part of the cleanup-and-refinement stage, not an
afterthought.

**Codified:** [sdlc/GRAPH.md](../../sdlc/GRAPH.md#placement-rules) placement
rules; stage 5 in [sdlc/LIFECYCLE.md](../../sdlc/LIFECYCLE.md#stages).

## L3. Screenshots and transcripts are PII surfaces

CI screenshots capture whatever identity the browser session carries, and
training transcripts embed absolute home paths. The policy scanner cannot
read images.

**Lesson:** capture evidence screenshots logged-out, eyeball every image
before commit, and pass transcripts through a path-sanitizing filter
(`sed "s|$PWD|<repo>|g"`) before they leave the machine.

**Codified:** practiced in PR #8's evidence set; recorded here as the
standing method until a capture tool automates it.

## L4. A regression baseline is only useful if the next run can find it

The compact regression worked because the 2026-07-26 baseline evidence
recorded exact commands, model, slice, step count, and metrics - the new run
reproduced it within 0.005 on every loss metric.

**Lesson:** regression evidence must name its baseline and its tolerances
explicitly. The next step is baselines as data (small JSON + tolerances)
computed by CI rather than compared by hand - filed as a suggestion, not yet
built.

**Codified:** [models/ACCEPTANCE.md](../../models/ACCEPTANCE.md#compact-regression-per-pr-scale)
defines the compact regression against the previous accepted baseline.

## L5. Path-filtered CI cannot gate by itself

The `models` workflow only runs when `models/**` changes, so it cannot be a
blanket-required check in branch protection; a red models job blocks nothing
structurally.

**Lesson:** module workflows need either an always-running summary gate or a
ruleset scoped to the module's paths before "CI green" is enforceable at the
module level. Until then the gate is review discipline.

**Codified:** recorded here; tooling follow-up belongs to a future project.

## L6. An unenforceable stage is an unlanded stage

The lifecycle required an article before merge while Atlas had no intake
surface - the requirement was prose until
[atlas/articles/](../../atlas/articles/2026-07-28-models-integration/article.md)
existed.

**Lesson:** when a stage names an artifact, the same change must create the
place the artifact lands (the PR #5 lesson "a policy landing without an
enforcement point should be treated as unlanded", applied to publication).

**Codified:** `atlas/articles/<date>-<project>/` intake established by this
project's own article.
