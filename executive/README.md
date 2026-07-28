# Executive

Standing executive agents that continuously validate this repository from
their own perspective, plus the strategic and tactical outlook material and
the tooling for overall repo monitoring. Part of the
[repository graph](../sdlc/GRAPH.md): the root README links here, and each
agent's charter links to the artifacts it consumes and produces.

| Agent | Charter | Validates | Primary artifacts |
|-------|---------|-----------|-------------------|
| **CEO** | [CEO.md](CEO.md) | Direction: is the repo moving along the axis, at the declared effort mix, with externally legible results? | Consumes exec decks/briefs and weekly digests; drives realignment questions |
| **CTO** | [CTO.md](CTO.md) | Execution: is the platform sound - architecture, QA and regression discipline, graph integrity, evidence quality? | Consumes whitepapers, CI history, lessons; drives architecture review inputs |

Both agents run on the cadence of the levels that feed them
([daily](../sdlc/DAILY.md), [tactical](../sdlc/TACTICAL.md),
[strategic](../sdlc/STRATEGIC.md)): they read the scheduled publications, ask
their standing questions, and file findings as GitHub issues so every concern
enters the normal project flow.

## Monitoring tooling

Repo-monitoring tooling lands here as it is built (dashboards over CI
history, graph integrity reports, effort-mix tracking against
[AXIS.md](../AXIS.md)). Until then, the agents use the existing guards and CI
runs directly.

Status: first iteration - charters defined, invoked manually as part of the
daily and weekly cycles; scheduled runs follow with the daily-level
activation.
