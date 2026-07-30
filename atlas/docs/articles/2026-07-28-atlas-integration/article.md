# The stage that named an artifact and never checked for it

Audience: Architect, PM. Project trail:
[issue #14](https://github.com/hyperscaleailabs/core/issues/14) ->
[PR #15](https://github.com/hyperscaleailabs/core/pull/15).
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../../sdlc/LIFECYCLE.md#stages).

## Goal

`atlas/` was a README describing an aggregation contract with no aggregator
behind it. The working site - an Astro 5 static build, 32 schema-validated
articles across eight collections, a robots-aware ingestion pipeline that opens
pull requests, deployed on Vercel - lived in a separate public repository with
its own SDLC and its own agent skills.

The project moved it in, merged the two publishing methodologies in the correct
direction, and closed the gap the lifecycle had been carrying since the models
integration: the stage that says *"publishing the article triggers the Atlas
update"* had a destination and no edge.

## What was built

- **The integration**: the site, the corpus, the pipeline, and its four docs
  under [atlas/](../../../README.md), internal structure intact. Left behind on
  purpose: the standalone repo's `LICENSE` (the repository default covers it),
  its `CONTRIBUTING.md`, build output, dependencies, and the ingestion cache.
- **Module furniture**: [ACCEPTANCE.md](../../../ACCEPTANCE.md), a `Makefile`
  whose `verify` target is exactly what CI runs, `NOTICE.md` and
  `LICENSE-CONTENT` for the dual license (code Apache-2.0, content CC BY 4.0),
  and `docs/evidence/`, `docs/lessons/`, `docs/articles/`.
- **A module CI/CD DAG**,
  [`.github/workflows/atlas.yml`](../../../../.github/workflows/atlas.yml),
  path-scoped to `atlas/**` **and** to every module's `docs/articles/**`:
  site build, index freshness, collection registration, the publication intake
  guard, the module policy guards, and the pipeline's static checks.
- **The publication intake**: a ninth content collection, `lab`, and
  [`scripts/intake-module-article.mjs`](../../../scripts/intake-module-article.mjs),
  which drafts an entry from a module article and, with `--check`, fails when
  one is missing.
- **Two skills, rewritten**: `atlas-add-source` and `atlas-changelog-post` keep
  the corpus-specific procedure and defer branch, PR, verification, and merge to
  `pr-flow`.

## What the SDLC merge actually decided

Same test as the prod integration: *would another module need this sentence?*

The source repository's skills published by opening a PR and merging it
themselves the moment CI went green. Deliberate, documented, and reasonable for
a solo content site. Nothing about it, though, is specific to publishing - it is
simply a different governance model, and this repository's is Architect LGTM,
one PR at a time, full template with issue linkage. So the skills came across
rewritten, and the same rule reached the automation: the ingestion workflow now
writes a PR body that satisfies `sdlc / pr-discipline` and refuses to start when
the standing issue variable is unset, rather than opening a red PR every Monday
until somebody switched the workflow off.

What moved *up* is smaller than in the prod integration, and that is the correct
result: this module's method is mostly its own. What did move up is the graph
edge. [GRAPH.md](../../../../sdlc/GRAPH.md#the-exit-node) now names Atlas the
**exit node** - the root README is where every agent enters, and this is where a
finished project leaves - with the intake as the mechanism and a CI guard behind
it.

## QA results

`make verify` and `make intake-check`, run locally, then the same checks on the
hosted runner. All green:

| Check | Result |
|-------|--------|
| Production dependencies | 0 high or critical advisories; CI guarded |
| Search index | 35 documents, unchanged by a fresh rebuild |
| Collection registration | 9 collections, consistent across schema and metadata |
| `astro check` | 0 errors, 0 warnings, 0 hints across 20 files |
| `astro build` | 48 pages |
| Publication intake | 3 of 3 module articles published |
| Module policy guards | 5 of 5 |
| Repo policy (gitleaks, PII, links) | clean |

The new guards were also run in the **failing** direction - a planted removal
for the collection guard, a planted repository reference for the policy guard,
and an isolated vulnerable lockfile for the dependency audit -
because a guard that has never been seen to fail is a guard nobody has tested.

Full record:
[docs/evidence/2026-07-28-atlas-integration-evidence.md](../../evidence/2026-07-28-atlas-integration-evidence.md).
Evidence tier: **process**.

## What went wrong, which is the interesting part

Three defects, none of which any build could see.

**Every outbound link in the site pointed at the repository it had just left.**
"View on GitHub", "Edit this page", the license link on the licensing page.
The build was green, the pages rendered, `astro check` reported nothing. A
reader clicking "Edit this page" would have landed in a repository that no
longer moves, and a license audit would have followed the same dead link. This
is the models-integration lesson about migrated docs carrying their old repo's
skeleton, arriving in the one place that checklist did not reach: it named old
filenames and command examples - text - while these were live URLs in
components, findable only by reading the rendered DOM.

**A collection registered in three of four places reported the wrong number.**
Adding `lab` needs the schema, the section metadata, the cross-section article
list, and the home page grid. The third was missed. Every page rendered, every
link worked, the section had its own index - and the home page said **32
articles** for a site that had 34. Nothing looked broken, which is worse than a
missing page. It surfaced only because this module's acceptance criteria require
walking the product surface, which is the prod-integration lesson about the
reviewer's path arriving one project early, in a module where the page *is* the
product.

**The new guards had nowhere to run before CI.** They shipped as inline steps in
the workflow. Everything runnable locally was run before pushing - build,
checks, all three repository policy scripts - and the PR still came back red on
its first run, because the guards themselves had never executed anywhere. Two
defects, both found by their own first execution: the stale-reference grep
matched its own source line, and the "URLs come from one module" rule
over-matched content, where absolute source URLs are precisely what attribution
*is*.

## What changed as a result

Every finding became a guard or a structural fix in the same PR:

- Repository links come from [`src/lib/repo.ts`](../../../src/lib/repo.ts), and
  two guards enforce it: no reference to the pre-integration repository anywhere
  (except `NOTICE.md`, which is the provenance record and says so), and no
  hardcoded repository URL in the site code.
- `getAllArticles` now derives its collection list from the section metadata, so
  that duplication is *gone* rather than guarded, and
  [`scripts/check-collections.mjs`](../../../scripts/check-collections.mjs)
  guards the one coupling that remains.
- All five module guards moved into
  [`scripts/check-policy.sh`](../../../scripts/check-policy.sh); `make policy`
  runs it, `make verify` includes it, and the workflow job is one line.
- Two repository-wide defects in `tools/policy/check_links.sh`, which this
  module was the first to expose: it scanned `node_modules` (hundreds of
  third-party failures) and read root-relative site URLs as broken paths. It now
  scans what git tracks, skips root-relative targets, and decodes
  percent-escaped paths.

Full write-up:
[docs/lessons/2026-07-28-atlas-integration.md](../../lessons/2026-07-28-atlas-integration.md).
The acceptance review correction is recorded separately in
[docs/lessons/2026-07-29-atlas-security-review.md](../../lessons/2026-07-29-atlas-security-review.md).

## Axis alignment

**Horizon: short**, and it holds. The [axis](../../../../AXIS.md) weights 80% of
effort on infrastructure that actually runs, and the test it offers - *does this
make a run reproducible, evaluable, or replayable?* - applies here to the
lifecycle rather than to a model: publication was the one stage that could be
skipped without anything noticing, and it can no longer be skipped.

*"Evidence or it didn't happen"* did real work again. Taken literally, it forced
walking the built pages instead of trusting a green build, which is what found
two of the three defects. The third guardrail exercised here is quieter:
**a lab note repeats the evidence tier of the claim it summarizes and never
upgrades it.** The published entry for the prod integration says
`simulation-demo`, because a release decision is a statement about a simulated
population - and the public-facing surface is exactly where that distinction is
most tempting to blur and most damaging to lose.

No mid- or long-horizon scope crept in. The move into the shared k3d deployment
stayed a note; the site remains a static build on Vercel, which is a hosting
change away from wherever it eventually runs.

## What is still open

- **The Vercel Root Directory** must be set to `atlas` in the Vercel dashboard.
  It is the one setting that lives outside this repository and the one that
  breaks the build if missed, so no deployed build is evidenced here.
- **The ingestion workflow has never run in this repository.** It needs the
  `ATLAS_CONTENT_ISSUE` repository variable, and it opens a pull request, so
  triggering it from an integration branch would have been theatre. Its first
  real run is its own evidence.
- **Two `.env.example` conventions now coexist**: the module keeps its own for
  the pipeline, while the repository's convention materializes runtime
  configuration under a host-local directory. They do not conflict today; they
  should be reconciled when Atlas leaves Vercel.
- **The upstream repository still exists.** Retiring or archiving it, and
  deciding whether the deployed site follows the module immediately, is a
  decision outside a module-bounded PR.
