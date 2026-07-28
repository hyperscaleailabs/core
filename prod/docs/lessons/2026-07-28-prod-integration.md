# Lessons from the prod integration project

Source: the project that moved the Agent Simulation Control Plane into `prod/` and
merged its delivery system into the repository SDLC. Each lesson states the
correction and where it is now codified.

The theme running through all of them: **a component can look healthy while producing
nothing.** Five of the seven findings below are silent failures - not crashes, not red
builds, but green surfaces over broken plumbing. That is the failure mode this module
exists to catch in other people's systems, and it was catching us.

## L1. A telemetry fallback that is not observable is a lie detector switched off

`control-api` builds its Kafka emitter once at startup and falls back to a no-op
emitter if the broker is unreachable, so that an analytics problem can never fail a
run. Correct intent. But the fallback is silent and permanent: the pod that started
while Kafka was still coming up served traffic for three days, reported healthy, ran
the golden workflow correctly - and emitted **zero** events. `/readyz` said ready.
`KAFKA_BOOTSTRAP` was set. Nothing anywhere said "telemetry is off".

The whole evidence chain downstream (Kafka, Flink, ClickHouse, Superset) was empty
for a reason that no surface reported. Restarting the pod fixed it instantly, which
is the tell: the failure was in startup ordering, and the system had no way to
recover or complain.

**Lesson:** degraded telemetry must be loud. A fallback is a state, and unreported
state becomes an unfalsifiable claim about everything built on it. "Analytics is
derived and must never block a run" does not imply "and must never be mentioned".

**Codified:** the observability gate in
[sdlc/PROMOTION.md](../../../sdlc/PROMOTION.md) now names degraded telemetry
explicitly; the evidence collector has a dedicated *telemetry not degraded* hop that
fails when the emitter is configured but no events arrive.

## L2. A dashboard built in a UI is not a deployed dashboard

The Superset dashboard existed only in the running pod's SQLite metadata, hand-built
through the browser. `dashboards/superset/` was an empty directory whose README
described five dashboards that were never built. So "the data is visible in Superset"
was true of one particular container and reproducible by nobody - and the metadata
store is ephemeral, so a restart would have erased it.

**Lesson:** if a surface is part of the acceptance evidence, it has to be
provisioned from the repository. The test is not "can I see it" but "can a clone
recreate it".

**Codified:** the dashboard is exported to
[prod/dashboards/superset/failure-analytics/](../../dashboards/superset/README.md)
and imported by `deploy/scripts/import-superset-dashboards.sh`; the evidence
collector fails when no charts are provisioned.

## L3. Rendering is not the same as being queryable

Superset's dashboard importer does not carry `query_context` onto the chart record.
An imported chart renders correctly in the browser - the frontend builds the query
itself - while `/api/v1/chart/<id>/data` answers *"Chart has no query context
saved"*. A human looking at the dashboard sees success; automation sees nothing.
This is the same shape as L1: two surfaces disagreeing, and only the quiet one
telling the truth.

**Lesson:** verify the surface a machine will use, not the one a human happens to
look at. Where they differ, the automated path is the one that must pass.

**Codified:** the importer reconciles `query_context` after import; the evidence
collector treats an unqueryable chart as a failed hop rather than a zero-row chart.

## L4. A regression baseline nobody compares against drifts silently

`artifacts/golden/*.json` was the accepted release-decision baseline. Regenerating it
produced a clean diff on every metric - identical decisions, identical gate values,
identical trajectory IDs - except for a `provisional` field added by a later feature
that was never rolled into the baseline. The baseline had been stale for several PRs
and nothing noticed, because nothing ever diffed it.

This is the models-integration lesson L4 ("a regression baseline is only useful if
the next run can find it") recurring in a new form: here the baseline was findable,
and still useless, because comparison was not automated.

**Lesson:** a baseline without an automated comparison is a file, not a gate.

**Codified:** the `golden-workflow` job regenerates the decisions and fails the build
on any diff from the committed baseline; the criterion is in
[prod/ACCEPTANCE.md](../../ACCEPTANCE.md).

## L5. Evidence must be a delta, not a snapshot

The first evidence pass read the counters and found data everywhere - all of it
produced days earlier. ClickHouse then turned out to hold **zero** rows, because its
storage is ephemeral and it had restarted; the Kafka consumer group had already
committed past the old messages, so nothing would ever be replayed. Reading absolute
values would have reported a working pipeline in both directions of wrong.

**Lesson:** prove a hop with the change a fresh run produces. Presence of data proves
that something worked once, which is not the claim being made.

**Codified:** `deploy/scripts/collect-evidence.sh` records every counter before and
after a fresh run and passes a hop only on a positive delta.

## L6. Identifiers that reset make correlated evidence ambiguous

The control-plane store is in-memory (a tracked gap, ASC-091). After a restart, run
IDs begin again at zero, so `run-exp-purchase-v3-3` names two different runs with
different harnesses. Traces from before and after the restart collide in Tempo, and
reading one in isolation suggests a telemetry bug that does not exist. Several
minutes went into chasing that ghost.

**Lesson:** an identifier used to correlate evidence across stores must be unique
across process restarts, or the evidence is not correlatable - which costs more than
the persistence it was avoiding.

**Codified:** recorded here against ASC-091; the evidence records state the run IDs
and their collection window so a reader can disambiguate.

## L7. Wildcards in a copy step match at every level

The integration copied the source tree with `rsync --exclude 'README.md'` to protect
the module's own README. The pattern is not anchored, so it silently dropped **21
nested READMEs** - every service, package, and component doc. The only reason it
surfaced is that the repository's markdown link guard failed on the dangling links.

**Lesson:** anchor exclude patterns (`/README.md`), and treat the link guard as part
of an integration's acceptance rather than a formality. A guard that catches a
mistake nobody suspected is the guard earning its keep.

**Codified:** noted here for the next integration; the models-integration sweep
checklist (L1 there) gains "anchored exclude patterns" and "run the link guard before
declaring the copy complete".

## L8. Screenshots carry identity the scanner cannot read

A committed product screenshot showed an operator avatar with a contributor's
initials, hardcoded in the MVP markup as `<div class="operator">CG</div>`. No text
scanner catches two letters inside a PNG, and the initials also sat in the HTML,
where they read as mock data rather than as identity.

**Lesson:** the models lesson L3 (screenshots are PII surfaces) extends to
*identifiers embedded in product markup*. People are referred to by role, including
in mock data - a placeholder avatar should say `OP`, never someone's initials.

**Codified:** the markup and the affected screenshot now use the role label; the
practice remains eyeball-every-image before commit, since no automated check covers
this.
