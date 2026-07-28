# The pipeline that looked healthy and shipped nothing

Audience: Architect, PM. Project trail:
[issue #11](https://github.com/hyperscaleailabs/core/issues/11) ->
[PR #12](https://github.com/hyperscaleailabs/core/pull/12).
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../../sdlc/LIFECYCLE.md).

## Goal

A complete Agent Simulation Control Plane - 51 delivery issues, 15 merged PRs,
deployed end to end on local k3s - lived in a standalone repository, while
`prod/` in this monorepo was three README files describing directories that did
not exist. The project moved it in, merged its delivery system into core's
four-level SDLC in the correct direction, and proved the whole evidence chain by
running it rather than asserting it.

## What was built

- **The integration**: 200+ tracked files under [prod/](../../../README.md) -
  four contract packages, six services, the Flink job, Druid ingestion specs,
  dashboards, kustomize manifests and Helm values, GCP Terraform, golden
  fixtures, tests, seven ADRs, and the v0.1.0 product handoff. The project kept
  its internal structure; `ui`, `backend`, and `platform` became **roles mapped
  onto real paths** rather than a directory split imposed on working code.
- **A module CI/CD DAG**, `.github/workflows/prod.yml`, path-scoped to `prod/**`:
  static checks, contract-schema compatibility, unit tests, the golden workflow
  as a self-gate, policy guards, terraform validate, and a nightly deployed-evidence
  job on an ephemeral cluster.
- **[sdlc/PROMOTION.md](../../../../sdlc/PROMOTION.md)** - the promotion ladder,
  release evidence packet, deployment and rollback classes, and observability
  gates, promoted out of this module because none of it was specific to it.
- **An evidence collector**, `deploy/scripts/collect-evidence.sh`, that proves
  each hop by the delta a fresh run produces.

## What the SDLC merge actually decided

The instruction was that what is common moves up and what is specific stays
down. Applying it required a test, and the test that worked was: *would another
module need this sentence?*

Moved up, into [PROMOTION.md](../../../../sdlc/PROMOTION.md): the environment
ladder and its gates, the release evidence packet, deployment strategies,
the five rollback classes, and the observability gates. Core's lifecycle had
covered all of this in one line - *"merge to main triggers: staging -> canary ->
ramped production"* - while this project had practiced it.

One idea generalized further than expected. The project's "simulator as a check"
- the release-gating product running in its own pipeline - is an instance of
something `models` was already doing with its golden-slice run. It is now the
**self-gating** principle: *a module's product runs in its own delivery pipeline
as a check, and a module with nothing to run against itself has a gap in its
acceptance template, not an exemption.*

Stayed down, in [prod/](../../../README.md): the golden Purchase Ambiguity
workflow, the gate engine's decision semantics, the data and observability
planes, and the module's CI DAG.

## QA results

Every CI phase was run locally, iteratively, against a live cluster rather than
in a hosted runner. All green:

| Phase | Result |
|-------|--------|
| Ruff format and lint | 63 files clean |
| Handoff package intact | passed (after repair, below) |
| Contract schemas | up to date |
| Unit tests | 57 passed |
| In-process golden e2e | 4 passed |
| Golden workflow self-gate | Blocked / Passed, reproducing the accepted baseline exactly |
| Policy guards | no hardcoded registries, no home paths, dashboard credentials masked |
| PII and link scans | clean |

And the deployed chain, each hop verified by its delta over a fresh run:

| Hop | Delta |
|-----|-------|
| control-api | unsafe -> **Blocked**, safe -> **Passed** |
| Kafka `sim.iteration.events.v1` | 15318 -> 19525 (+4207 events) |
| Flink failure-stats job | RUNNING |
| Kafka `sim.failure.stats.v1` | 62 -> 71 (+9 aggregates) |
| ClickHouse `failure_stats` | 25 -> 34 rows |
| Superset | both charts return live rows |
| Grafana -> Tempo | 20 `control-api` traces with `asc.*` correlation attributes |

Full record: [docs/evidence/2026-07-28-prod-integration-evidence.md](../../evidence/2026-07-28-prod-integration-evidence.md).

## What went wrong, which is the interesting part

The first evidence pass reported a healthy pipeline. It was wrong in both
directions, and the way it was wrong is the finding.

**The control-api had emitted zero events for three days.** It builds its Kafka
emitter once at startup and falls back to a no-op if the broker is unreachable -
correct intent, so analytics can never fail a run. But the fallback is silent and
permanent. The pod had started while Kafka was still coming up. `/readyz` said
ready, `KAFKA_BOOTSTRAP` was set, the golden workflow ran correctly, and nothing
downstream received anything. A restart fixed it instantly.

**ClickHouse held zero rows**, because its storage is ephemeral and it had
restarted; the Kafka consumer group had already committed past the old messages,
so nothing would ever replay. Reading absolute counters would have reported
success from stale data in one direction and failure from an empty store in the
other.

**The Superset dashboard existed only inside one container.** `dashboards/superset/`
was an empty directory whose README described five dashboards that were never
built. The two that existed had been made by hand in the browser, on ephemeral
metadata - so "the data is visible in Superset" was true of one pod and
reproducible by nobody.

**An imported chart rendered but could not be queried.** Superset's importer
drops `query_context`, so the browser builds the query itself and the chart looks
perfect while `/api/v1/chart/<id>/data` answers *"Chart has no query context
saved"*. The human sees success; automation sees nothing.

**The regression baseline had drifted.** Regenerating the golden release
decisions produced identical decisions and identical metrics, plus a
`provisional` field added by a later feature and never rolled in. The baseline
had been stale for several PRs because nothing ever diffed it.

Five findings, one shape: **a surface reporting health over plumbing that
produces nothing.** Which is precisely the failure mode this module exists to
catch in other people's agent systems - and it was catching us.

Two more, less philosophical: `rsync --exclude 'README.md'` is not anchored and
silently dropped 21 nested READMEs (the markdown link guard caught it), and
`make verify` had been failing unnoticed against a docs layout that moved under
it, because it was a Makefile target and never a CI job.

## What changed as a result

Every finding became a guard in the same change, per the standing rule:

- The evidence collector proves hops by **delta**, and has a dedicated
  *telemetry not degraded* hop that fails when the emitter is configured but no
  events arrive.
- Degraded telemetry is now named explicitly in the repo-wide
  [observability gates](../../../../sdlc/PROMOTION.md).
- The Superset dashboard is **exported into the repository** and imported by
  `deploy/scripts/import-superset-dashboards.sh`, which also reconciles
  `query_context` so every chart is machine-queryable. An unqueryable chart is a
  failed hop.
- The `golden-workflow` CI job regenerates the release decisions and **fails on
  any diff** from the committed baseline.
- `scripts/verify_package.py` was repaired and promoted into CI.
- Excluded patterns are anchored, and the link guard is part of an integration's
  acceptance rather than a formality.

Full write-up: [docs/lessons/2026-07-28-prod-integration.md](../../lessons/2026-07-28-prod-integration.md).

## Axis alignment

**Horizon: short**, and it holds. The [axis](../../../../AXIS.md) weights 80% of
effort on reproducible infrastructure that actually runs - contracts, local
runtime, replay, release gates, CI. This project is entirely that: it made an
existing system's evidence chain reproducible from a clone, and closed five ways
it could lie about itself.

Two guardrails were exercised rather than cited. *"Learned policies and language
models propose; deterministic supervisors dispose"* is what this module **is** -
the gate engine is the deterministic supervisor, and its decisions are
reproducible from a seed; the golden decisions regenerate byte-for-byte against
a baseline recorded days earlier. *"Evidence or it didn't happen"* did real work
here: taken literally, it forced the discovery that the previous evidence,
though honestly recorded, described a pipeline that had since stopped carrying
data.

No mid- or long-horizon scope crept in. The GCP path stayed written and
CI-validated with a human-gated apply; the registry reference in the cloud
overlay was made a placeholder rather than a real host, keeping the repository
cloud-agnostic.

## What is still open

- The control-plane store is in-memory (ASC-091), so run IDs repeat after a
  restart and correlated evidence across Kafka, ClickHouse, and Tempo becomes
  ambiguous. This cost real debugging time and is the highest-value follow-up.
- The deployed-evidence job is nightly, not per-PR, and a path-filtered workflow
  cannot be a blanket required check in branch protection - the module gate is
  still partly review discipline.
- Three of the five specified Superset dashboards remain unbuilt, deferred to
  the x86 Druid path (ASC-099).
- `prod/infra/terraform/` and the repository's own `infra/` now overlap; the
  consolidation is deliberate follow-up work, kept out of a module-bounded PR.
