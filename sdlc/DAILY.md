# Daily level

Cadence: **daily**. The daily level is the **priorities backlog**: it frames the
day's execution and publishes its results. It holds **3-5 projects** drawn from
the ~20-project dependency graph of the
[weekly tactical review](TACTICAL.md#weekly---tactical-review-and-digest); each
project runs the [project lifecycle](LIFECYCLE.md).

## The day

1. **Open**: pull the day's 3-5 projects from the weekly graph, in priority and
   dependency order. Fewer is fine; needing more is a sign projects are sized
   wrong.
2. **Execute**: each project runs the project lifecycle - templated initiation,
   Architect handoff, agent-team execution behind verification and quality
   gates, acceptance - producing its PRs, evidence, lessons entry, and article.
3. **Close - the daily update**, published to Atlas on schedule, derived from
   the day's project articles:

| Publication | Audience level | Content |
|-------------|----------------|---------|
| Executive deck | CEO | The day's goals, what shipped, the headline lesson, tomorrow's intent |
| Whitepaper | CTO | Executive overview aggregating the day's project articles, combined with the tactical directionality: how the 3-5 delivered projects moved core and the apps in the intended direction. Evaluates strategic and tactical alignment - how the day's work balanced the short/mid/long horizons against their proportional weighting, and whether any drift from the axis appeared |

Both are scheduled parts of the daily update and are derived from the project
articles, never written from memory: a claim that is not in an article backed by
evidence does not appear in a publication. Daily whitepapers and decks
accumulate, and the [weekly digest](TACTICAL.md#weekly---tactical-review-and-digest)
aggregates them.

## Integration

- **Down**: the daily backlog is the only entry point for projects; work that is
  not on it is not started.
- **Up**: daily publications are the input to the weekly digest, the weekly
  backlog ordering, and the monthly architecture review. Unfinished projects roll
  forward explicitly, never silently.

## Status

First-iteration scaffolding. Publication starts agent-run at day close and
becomes a scheduled job; the [atlas/](../atlas/) subproject provides the
publication surface. Activates together with the weekly tactical review.
