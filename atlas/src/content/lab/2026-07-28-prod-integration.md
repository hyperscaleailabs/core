---
title: "The pipeline that looked healthy and shipped nothing"
description: "Five findings from integrating an agent simulation control plane, all with the same shape: a green surface reporting health over plumbing that was producing nothing. Including an API that had emitted zero telemetry for three days behind a passing readiness probe."
level: "advanced"
updated: 2026-07-28
created: 2026-07-28
tags: [lab-notes, prod, observability, failure-modes, evidence, kafka, clickhouse]
module: "prod"
project: "prod-integration"
articlePath: "prod/docs/articles/2026-07-28-prod-integration/article.md"
issue: 11
pr: 12
evidenceTier: "simulation-demo"
draft: false
aiGenerated: false
license: "CC-BY-4.0"
sources:
  - title: "The pipeline that looked healthy and shipped nothing (module article)"
    url: "https://github.com/hyperscaleailabs/core/blob/main/prod/docs/articles/2026-07-28-prod-integration/article.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
  - title: "Lessons from the prod integration project"
    url: "https://github.com/hyperscaleailabs/core/blob/main/prod/docs/lessons/2026-07-28-prod-integration.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
---

> Field notes from the `prod` module of our open monorepo - the Agent Simulation
> Control Plane, which runs non-deterministic agents under injected failures and
> returns an explainable release decision. Full article, per-hop evidence, and
> review trail in
> [the module article](https://github.com/hyperscaleailabs/core/blob/main/prod/docs/articles/2026-07-28-prod-integration/article.md).

We moved a complete, deployed control plane into the monorepo and set out to
collect evidence that the whole chain worked: operator UI to Kafka, Flink to
ClickHouse, out to Superset and Grafana. The first evidence pass reported a
healthy pipeline. It was wrong in both directions, and how it was wrong is the
entire finding.

## Five ways a system lied about itself

**The control API had emitted zero events for three days.** It builds its Kafka
emitter once at startup and falls back to a no-op emitter if the broker is
unreachable - correct intent, because an analytics problem must never fail a
run. But the fallback is silent and permanent. The pod had started while Kafka
was still coming up. The readiness probe said ready. The bootstrap environment
variable was set. The golden workflow ran and produced correct decisions. And
nothing downstream ever received a single event. A restart fixed it instantly,
which is the tell: the failure was startup ordering, and the system had no way
to recover or to complain.

**The OLAP store held zero rows.** ClickHouse storage was ephemeral and it had
restarted; the Kafka consumer group had already committed past the old messages,
so nothing would ever replay. Reading absolute counters would have reported
success from stale data in one direction and failure from an empty store in the
other.

**The dashboard existed only inside one container.** It had been hand-built in
the browser, on ephemeral metadata, while the repository directory that was
supposed to hold it was empty behind a README describing five dashboards that
were never built. "The data is visible in the dashboard" was true of exactly one
pod and reproducible by nobody.

**An imported chart rendered but could not be queried.** Superset's importer
does not carry `query_context` onto the chart record, so the browser builds the
query itself and the chart looks perfect, while the chart data API answers
*"Chart has no query context saved"*. A human sees success; automation sees
nothing.

**The regression baseline had drifted.** Regenerating the golden release
decisions produced identical decisions and identical gate metrics - plus one
field added by a later feature and never rolled into the baseline. It had been
stale for several PRs, because nothing ever diffed it.

One shape, five times: **a surface reporting health over plumbing that produces
nothing.** Which is precisely the failure mode this module exists to catch in
other people's agent systems. It was catching us.

## What we changed, in the same change

Every finding became a guard, not a note:

- Evidence proves a hop by **delta**, never by presence. The collector records
  every counter before and after a fresh run and passes a hop only on a positive
  change. Presence of data proves something worked once, which is not the claim
  being made.
- Degraded telemetry became a **loud, checked state**. There is now a dedicated
  *telemetry not degraded* hop that fails when the emitter is configured but no
  events arrive. A fallback is a state, and unreported state becomes an
  unfalsifiable claim about everything built on top of it.
- The dashboard is **exported into the repository** and imported by a script
  that also reconciles `query_context`, so every chart is machine-queryable. The
  test is not "can I see it" but "can a clone recreate it".
- The golden workflow job **regenerates the release decisions and fails on any
  diff** from the committed baseline. A baseline without an automated comparison
  is a file, not a gate.
- **Verify the surface a machine will use**, not the one a human happens to look
  at. Where the two disagree, the automated path is the one that must pass.

## The reviewer's path is a surface too

Preparing the environment for review - not the tests, the *review* - turned up
three more defects that every automated check had passed over, because no check
opens a browser and clicks around. The API documentation page was broken behind
the reverse proxy while the API itself was perfectly healthy. A script printed
URLs that did not answer, because it assumed a port and hostnames instead of
discovering them. An image build could not push on an ordinary laptop.

A URL printed but unreachable is worse than one not printed. Scripts that report
environment facts should discover them, never assume them - and someone has to
walk the reviewer's path before handoff, because it is part of the deliverable.

## What stayed open

The control-plane store is in-memory, so run identifiers repeat after a restart
and correlated evidence across the event log, the OLAP store, and the trace
backend becomes ambiguous. That cost real debugging time chasing a telemetry bug
that did not exist, and it is the highest-value follow-up. The deployed-evidence
job runs nightly rather than per-PR. Three of five specified dashboards remain
unbuilt. All of it is written down as a gap rather than half-fixed, which is the
only honest way to carry an unfinished thing across a merge.
