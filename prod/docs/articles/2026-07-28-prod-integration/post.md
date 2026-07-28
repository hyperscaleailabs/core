# Post: the pipeline that looked healthy and shipped nothing

Platform-neutral social variant (LinkedIn format assumed). Audience: CTO,
Architect, PM. Long form: [article.md](article.md).

---

We integrated a working agent-simulation control plane into our monorepo this
week. The interesting part wasn't the move. It was what the move found.

The system tests non-deterministic AI agents under injected failures and returns
an explainable release decision - Blocked, Passed, Manual review. It had been
deployed end to end on a local cluster for days. Dashboards were up. Health
checks were green.

It had emitted zero telemetry for three days.

The control-api builds its Kafka emitter once at startup, and falls back to a
no-op if the broker isn't reachable yet - so that an analytics problem can never
fail a simulation run. Good intent. But the fallback was silent and permanent.
The pod had come up before Kafka did. Readiness said ready. The golden workflow
ran correctly and produced correct decisions. Nothing downstream received
anything, and no surface anywhere said so.

Then it kept going:

- ClickHouse held zero rows - ephemeral storage, restarted, and the Kafka
  consumer group had already committed past the old messages. Nothing would ever
  replay.
- The Superset dashboard existed only inside one container. Hand-built in the
  browser, on ephemeral metadata. "The data is visible in Superset" was true of
  one pod and reproducible by nobody.
- An imported chart rendered perfectly in the browser while returning "no query
  context saved" to the API. Humans saw success; automation saw nothing.
- The regression baseline had silently drifted, because nothing ever diffed it.

Five findings, one shape: a green surface over plumbing that produces nothing.

Which is exactly the failure mode this product exists to catch in other people's
agent systems. It was catching us.

Three things we changed, and would recommend to anyone running a data or
evaluation pipeline:

**1. Prove hops with deltas, not snapshots.** Our evidence collector now records
every counter before and after a fresh run, and a hop only passes on a positive
change. "There is data in the store" proves something worked once. That is not
the claim you are making.

**2. Make degraded modes loud.** A fallback is a state. An unreported state turns
every downstream claim into something you cannot falsify. "Analytics must never
block a run" does not imply "and must never be mentioned."

**3. Verify the surface a machine will use.** Where the human view and the
automated view disagree, the automated one is the one that has to pass. A
dashboard you cannot query from CI is a dashboard you cannot trust in CI.

None of this was exotic. Every one of them was a component behaving exactly as
written, with no error anywhere - and an evidence chain that was quietly not
carrying anything.

If your pipeline can't tell you the difference between "working" and "not
currently failing," it isn't telling you much.
