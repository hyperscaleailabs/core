# Bringing the model pipeline home: integrating train/bench/serve into the monorepo

Audience: Architect, PM. Project trail:
[issue #7](https://github.com/hyperscaleailabs/core/issues/7) ->
[PR #8](https://github.com/hyperscaleailabs/core/pull/8) -> merge `820dc85`.
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../../sdlc/LIFECYCLE.md#stages).

## Goal

The working model pipeline - golden datasets, LoRA fine-tuning, a benchmark
runner, vLLM/K3s serving, and its CI checks - lived in a standalone
repository with its own methodology, while `models/` in this monorepo was a
placeholder. The project moved the pipeline into `models/` without losing a
single check, and used the move to land process machinery the whole
repository now runs on.

## What was built

- **The integration itself**: 40 tracked files (model registry, three golden
  dataset configs with schema and streaming pull, LoRA fine-tune entrypoint,
  benchmark runner, inference containers, domain packs, K3s manifests and
  scripts, docs with evidence and lessons) now live under
  [models/](../../../README.md). Caches, weights, and the standalone
  repo's superseded methodology files were deliberately left behind; runtime
  identifiers were deliberately kept, with the rename recorded as separate
  future work.
- **All three source CI jobs** run in core, path-scoped to `models/**`:
  static checks, golden-smoke auto-evidence (pulls real golden slices on
  every models PR and publishes the transcript), and policy guards (no
  hardcoded registries; no committed weights, checkpoints, or kubeconfigs).
- **Process machinery**: per-subproject acceptance criteria templates
  ([models/ACCEPTANCE.md](../../../ACCEPTANCE.md) is the first),
  issue-anchored projects with CI-enforced `Issue: #N` linkage, the
  [repository graph](../../../../sdlc/GRAPH.md) with the root README as entrance
  node, a cleanup-and-refinement stage in every project, and the
  [executive/](../../../../executive/README.md) CEO and CTO validation charters.

## QA results

Every check green on every commit: repo policy (gitleaks + PII), PR
discipline, markdown link/anchor guard, and the three models jobs. The
**compact regression** defined in
[models/ACCEPTANCE.md](../../../ACCEPTANCE.md#compact-regression-per-pr-scale)
was executed against the previous accepted baseline:

| Metric | Baseline (2026-07-26) | Regression (2026-07-28) | Delta |
|--------|----------------------|-------------------------|-------|
| First / final / min loss | 3.82 / 3.43 / 3.34 | 3.818 / 3.434 / 3.344 | < 0.005 |
| `train_loss` | 3.647 | 3.649 | +0.002 |

**PASS** - the golden -> fine-tune -> adapter path is unchanged by the move
([full record](../../evidence/2026-07-28-regression-lora-smoke.md),
evidence tier: smoke).

## Axis alignment check

- **Strategic** ([AXIS.md](../../../../AXIS.md)): short horizon - reproducible
  ML infrastructure on open models and public datasets. The project moves the
  train/evaluate/serve loop into the platform where its evidence, gates, and
  replay live. Horizon declared short; no mid/long work smuggled in.
- **Tactical**: the integration was the week's bounded single-PR project; the
  pipeline's checks became monorepo QA, which is exactly what the tactical
  level needs to size future model projects at several hours each.
- **Drift**: one instance found and corrected during the project itself - the
  first project template restated mission and vision per project; alignment
  verification moved into outputs (this article's check is that mechanism).

## Lessons

Carried in [docs/lessons/2026-07-28-models-integration.md](../../lessons/2026-07-28-models-integration.md):
sweep migrated docs for the old repo's filenames; capture evidence
screenshots logged-out and sanitize transcripts; module evidence lives in the
module; path-filtered CI cannot block merges by itself; the article intake
this file inaugurates was the last unenforceable stage.
