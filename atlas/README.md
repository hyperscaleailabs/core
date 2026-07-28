# Atlas

Agentic research project. Aggregates lessons learned from all subprojects and produces
regular white papers and posts: text and video posts about agents, simulations, lessons
learned, experiment results, and webinar recordings.

- Public surface, Apache-2.0 by design.
- Currently deployed as a Vercel app; will be extended with blog post functionality and
  later migrated into the shared k3d deployment where it makes sense.
- Incorporated work is referenced with careful attention to its original license.

## Aggregation sources

Atlas aggregates and publishes; it does not host the sources. Per-project
articles live in their owning module as
`<module>/docs/articles/<YYYY-MM-DD>-<project>/` (`article.md` for Architect
and PM audiences, `post.md` as the platform-neutral social variant), produced
by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../sdlc/LIFECYCLE.md#stages). Cross-module publications
live in [docs/projects/](../docs/projects/) (whitepapers) and
[docs/weekly/](../docs/weekly/) (digests as short books). First module
article:
[models/docs/articles/2026-07-28-models-integration](../models/docs/articles/2026-07-28-models-integration/article.md).

Status: aggregation sources defined; app structure and code migrate here in upcoming iterations.
See the root [README](../README.md) for repository rules (public repo: no PII, squash merges, policy checks required).
