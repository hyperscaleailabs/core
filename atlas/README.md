# Atlas

Agentic research project. Aggregates lessons learned from all subprojects and produces
regular white papers and posts: text and video posts about agents, simulations, lessons
learned, experiment results, and webinar recordings.

- Public surface, Apache-2.0 by design.
- Currently deployed as a Vercel app; will be extended with blog post functionality and
  later migrated into the shared k3d deployment where it makes sense.
- Incorporated work is referenced with careful attention to its original license.

## Article intake

Per-project articles land in `articles/<YYYY-MM-DD>-<project>/` as `article.md`
(Architect and PM audiences) plus `linkedin.md` (CTO / Architect / PM variant),
produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../sdlc/LIFECYCLE.md#stages). Daily and weekly publications
(whitepapers, decks, digests) join here as their cadences activate. First
article: [2026-07-28-models-integration](articles/2026-07-28-models-integration/article.md).

Status: article intake active; app structure and code migrate here in upcoming iterations.
See the root [README](../README.md) for repository rules (public repo: no PII, squash merges, policy checks required).
