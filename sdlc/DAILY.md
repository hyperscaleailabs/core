# Daily level

Cadence: **daily**. The daily level frames the day's execution and publishes its
results. It holds a backlog of **3-5 projects** drawn from the
[weekly backlog](TACTICAL.md#weekly---project-backlog-and-digest); each project runs the
[project lifecycle](LIFECYCLE.md).

## The day

1. **Open**: pull the day's 3-5 projects from the top of the weekly backlog.
   Fewer is fine; needing more is a sign projects are sized wrong.
2. **Execute**: each project runs the project lifecycle - initiation, agentic
   execution behind verification and quality gates, architectural review -
   producing its PRs, evidence, lessons entry, and article.
3. **Close - publish to Atlas**, derived from the day's project articles:

| Publication | Audience level | Content |
|-------------|----------------|---------|
| Executive deck | CEO | The day's goals, what shipped, the headline lesson, tomorrow's intent |
| Whitepaper | CTO | Executive overview aggregating the day's project articles: combined goals, implementations, and lessons, with overview and summary |

Both are derived from the project articles, never written from memory: a claim
that is not in an article backed by evidence does not appear in a publication.
The [weekly digest](TACTICAL.md#weekly---project-backlog-and-digest) aggregates
them in turn.

## Integration

- **Down**: the daily backlog is the only entry point for projects; work that is
  not on it is not started.
- **Up**: daily publications are the input to the weekly backlog ordering and the
  monthly architecture review. Unfinished projects roll forward explicitly, never
  silently.

## Status

First-iteration scaffolding. Publication starts agent-run at day close and
becomes a scheduled job; the [atlas/](../atlas/) subproject provides the
publication surface. Activates together with the tactical weekly backlog.
