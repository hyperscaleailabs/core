---
title: "Bringing a model pipeline home: what 'integrated' has to mean"
description: "A train/benchmark/serve pipeline moved from a standalone repository into a monorepo without losing a single check - and the move was used to land the process machinery the whole repository now runs on."
level: "advanced"
updated: 2026-07-28
created: 2026-07-28
tags: [lab-notes, models, migration, ci, evidence, monorepo]
module: "models"
project: "models-integration"
articlePath: "models/docs/articles/2026-07-28-models-integration/article.md"
issue: 7
pr: 8
evidenceTier: "smoke"
draft: false
aiGenerated: false
license: "CC-BY-4.0"
sources:
  - title: "Bringing the model pipeline home: integrating train/bench/serve into the monorepo (module article)"
    url: "https://github.com/hyperscaleailabs/core/blob/main/models/docs/articles/2026-07-28-models-integration/article.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
  - title: "Lessons from the models integration project"
    url: "https://github.com/hyperscaleailabs/core/blob/main/models/docs/lessons/2026-07-28-models-integration.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
---

> Field notes from the `models` module of our open monorepo. Full article,
> evidence tables, and review trail in
> [the module article](https://github.com/hyperscaleailabs/core/blob/main/models/docs/articles/2026-07-28-models-integration/article.md).

A working model pipeline - golden datasets, LoRA fine-tuning, a benchmark runner,
vLLM serving on K3s, and the CI that checked all of it - lived in its own
repository with its own methodology. The monorepo directory meant to hold it was
a placeholder. Moving it is the kind of task that looks like an afternoon of
`git mv` and turns out to be the moment you discover what your definition of
"integrated" actually is.

## The bar we set

Not "the files are in the new place". Three things had to be true before the
move counted:

1. **No check was lost.** All three CI jobs from the source repository run in
   the monorepo, path-scoped so they fire only when the module changes: static
   checks, a golden-smoke job that pulls real dataset slices on every PR and
   publishes the transcript, and policy guards (no hardcoded container
   registries; no committed weights, checkpoints, or kubeconfigs).
2. **The pipeline still produced the same numbers.** A compact regression re-ran
   the golden-slice fine-tune against the previously accepted baseline. Every
   loss metric landed within 0.005 - first, final, and minimum loss, plus
   `train_loss` at +0.002. Sixteen optimizer steps on a fixed slice: cheap
   enough to run per-PR, specific enough to prove the path survived.
3. **What was left behind was left behind deliberately.** Caches and weights
   did not come. The source repository's superseded methodology files did not
   come. Runtime identifiers *did* come, unchanged, with the rename recorded as
   separate future work rather than smuggled into a migration diff.

## The lesson that generalizes

**Migrated docs carry their old repository's skeleton.** The moved subproject
referenced its old repo's methodology files, its command examples silently
assumed the old repository root, and its implementation plan presented the old
repo's PR numbers as current state.

None of that breaks a build. All of it misleads the next reader. So an
integration now carries a sweep checklist beyond the secret scan: old filenames,
working-directory assumptions in command examples, and historical plans and
checkboxes. Historical records get a preface, never a rewrite - a plan that was
true in March is not a lie, it is a dated document, and editing it to look
current destroys the only thing it was still good for.

Three more findings, each now codified rather than remembered:

- **Evidence has a home, and misplacement is a broken graph edge.** Module
  evidence first landed in a top-level directory, where nothing that needed it
  would look. Evidence lives with what it evidences.
- **Screenshots and transcripts are identity surfaces.** A screenshot captures
  whatever identity the browser session carries; a training transcript embeds
  absolute home paths. A text scanner cannot read an image. Capture logged-out,
  eyeball every image, and pipe transcripts through a path sanitizer.
- **A regression baseline is only useful if the next run can find it.** The
  comparison worked because the earlier baseline recorded exact commands, model,
  slice, step count, and metrics. A baseline that does not name its own
  reproduction instructions is a number without a method.

## What stayed open

Path-filtered CI cannot gate by itself. A workflow that runs only when the
module changes cannot be a blanket required check in branch protection, so a red
module job blocks nothing structurally. Until there is an always-running summary
gate or a path-scoped ruleset, the gate is review discipline - which is worth
writing down precisely because it is the kind of gap that otherwise gets
described as "CI is green".
