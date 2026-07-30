# A missing link is invisible to a broken-link checker

Audience: Architect, PM. Project trail:
[issue #16](https://github.com/hyperscaleailabs/core/issues/16) and
[pull request #17](https://github.com/hyperscaleailabs/core/pull/17).
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../LIFECYCLE.md#stages).

The repository link check was green while the root deployment table named four
modules without linking to their documentation. Every declared edge worked.
Four required edges did not exist.

## Goal

The deployment table is a reader-facing map from a public or gated surface to
the module that implements it. Its `Backed by` column should not merely name a
directory. It should take the reader to the module contract.

This project makes those navigation edges explicit and ensures the omission
cannot recur silently.

## What the review found

Meet, Agents, Models, and D-twins appeared as inline code in three table cells:

```text
Meet -> `meet/`
APIs -> `agents/`, `models/`
D-twins -> `dtwins/`
```

The Markdown link checker correctly reported `markdown links OK`. It checks the
targets and anchors of links that are present. No target existed for it to
validate in these cells.

The documentation graph itself remained connected through the root subproject
table. That made this a navigation defect rather than an orphaned-document
defect: a reader could eventually find each module, but not from the table that
claimed to explain the deployment surface.

## What changed

The four module names now link directly to their module READMEs. The link policy
also gained a narrow assertion: every data row in the deployment table must
contain a Markdown link in its `Backed by` cell.

The guard was added first and run against the original table. It named all three
bad cells and exited nonzero. After the links were added, the same command
passed, and the existing target checker verified each new path.

The project article itself then revealed a second blind spot. A broken link in
the new, untracked file passed because the checker enumerated only files already
known to Git. The scan now includes tracked and non-ignored untracked Markdown.
That catches a new document before staging without returning to the older
filesystem walk that scanned third-party dependency READMEs.

The guard is intentionally attached to the semantic table and column rather
than to a list of current module names. A future surface can use any backing
module, but it cannot omit the documentation edge.

## QA results

| Check | Result |
|-------|--------|
| Navigation guard before correction | failed on 3 cells |
| Navigation guard after correction | passed |
| Untracked-document scan before correction | failed to inspect the new article |
| Untracked-document scan after correction | found the planted broken path, then passed after repair |
| Markdown targets and anchors | clean |
| Repository documentation graph | reachable from the root entrance |
| Atlas static output | 49 pages, 36 indexed documents |
| Atlas internal route and fragment crawl | 1,625 checked, 0 broken |

Full record:
[evidence](../../evidence/2026-07-29-doc-navigation.md).
Evidence tier: **process**.

## Lesson

A link target check and a navigation completeness check are complements. The
first validates declared graph edges. The second asserts that a required edge
exists.

The reusable lesson is recorded in
[the process lesson](../../lessons/2026-07-29-doc-navigation.md), with the
codification target and failing-direction evidence.

## Axis alignment

Horizon: **short**. The change strengthens deterministic repository tooling and
the graph contributors use to find module contracts. It adds no mid- or
long-horizon product scope.

The work follows the axis guardrail that evidence must support claims: the
article reports only source inspection, deterministic checks, and a static-site
crawl. It makes no simulation or physical-system claim.

## What remains outside scope

External web links remain outside the repository link policy because their
availability is nondeterministic and often affected by authentication, robots
rules, or rate limits. Module-internal site links remain covered by the Atlas
build and route crawl.
