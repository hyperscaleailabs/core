# Lessons from the atlas integration project

Source: [issue #14](https://github.com/hyperscaleailabs/core/issues/14), the
project that moved the Agentic Atlas publication site into `atlas/` and turned
the lifecycle's publication stage into a mechanism. Each lesson states the
correction and where it is now codified.

The theme: **the third integration was the one where the prior lessons paid.**
Two of the findings below were predicted by the models and prod lessons and cost
minutes instead of hours because a checklist already existed. The two that were
new are both about *derived state that no build error can see* - a wrong number
on a page, and a link that resolves to the wrong repository.

## L1. A migrated site's links are a migration surface the build cannot check

Every "view on GitHub", "edit this page", and licensing link in the site pointed
at the standalone repository it came from. The build was green. The pages
rendered. `astro check` reported zero problems. A reader clicking "Edit this
page" would have landed in a repository that no longer moves, and a license
audit would have followed the same dead link.

This is the models lesson L1 ("migrated docs carry their old repository's
skeleton") in the one place that lesson's checklist did not reach: it named old
filenames, working-directory assumptions, and historical plans - all *text* -
while these were live URLs in components, and the sweep for them has to run
against the rendered DOM, not the source.

**Lesson:** a migrated web surface needs its outbound links read from the page a
reader gets, and the URLs need one home so the next move is one edit.

**Codified:** [`atlas/src/lib/repo.ts`](../../src/lib/repo.ts) holds
`REPO_URL`, the module path, and the derived browse/issues/license/edit URLs;
every component imports from it. Two CI guards in
[`.github/workflows/atlas.yml`](../../../.github/workflows/atlas.yml): no
reference to the pre-integration repository anywhere in the tree (except
[NOTICE.md](../../NOTICE.md), which is the provenance record and says so), and
no hardcoded repository URL in `src/` outside `repo.ts`. Verified by reading the
links out of the rendered DOM, recorded in the
[evidence](../evidence/2026-07-28-atlas-integration-evidence.md#walked-surfaces).

## L2. A new collection registered in one of two places builds green and counts wrong

Adding the `lab` collection needs four edits: the schema in `config.ts`, the
`SECTION_META` entry, the cross-section list in `getAllArticles`, and the home
page's section grid. Three landed. The missing one was `getAllArticles`, whose
only visible symptom was the home page reporting **32 articles** when the site
had 34.

Every page rendered. Every link worked. The section had its own index and its
articles were reachable. The single wrong number was the whole defect - and it
is a worse failure than a missing page, because nothing looks broken.

It surfaced only because the acceptance criteria for this module require walking
the product surface, which is the prod lesson L9 ("the reviewer's path is a
surface too") arriving one project early, in a module where the *page is the
product*.

**Lesson:** derived counts are claims, and a claim needs a check. Where a list
can be derived from an existing one, derive it; where it cannot, guard the
coupling.

**Codified:** `getAllArticles` now derives its keys from `SECTION_META` instead
of repeating them, so that duplication is gone rather than guarded.
[`scripts/check-collections.mjs`](../../scripts/check-collections.mjs) guards the
coupling that remains - schema versus `SECTION_META`, in both directions - and
runs in `make verify` and in CI. It was tested by removing the `lab` entry and
confirming it fails.

## L3. An automated PR is still a PR under the SDLC

The upstream ingestion workflow opened pull requests with a friendly free-form
body. In this repository, `sdlc / pr-discipline` checks every PR for five
sections, a checkbox, `Horizon:`, and `Issue: #N`. The bot's PR would have been
red on arrival, every week, until someone turned the workflow off - the failure
mode where automation is disabled rather than fixed.

**Lesson:** when automation opens PRs into a governed repository, its output has
to satisfy the same gates as a human's, and the *input* it needs for that (here,
a standing issue number) must be a configured, checked precondition rather than
an assumption.

**Codified:**
[`.github/workflows/atlas-ingest.yml`](../../../.github/workflows/atlas-ingest.yml)
writes the full template with `Horizon: short` and
`Issue: #${{ vars.ATLAS_CONTENT_ISSUE }}`, and fails **before** ingesting when
that repository variable is unset or non-numeric, with an error that says what
to set and why. A job that cannot produce a mergeable PR should not spend a
model budget first.

## L4. Two publishing methodologies met, and the merge direction was not symmetric

The standalone repository's agent skills published by opening a PR and merging
it themselves as soon as CI went green - deliberate, documented, and reasonable
for a solo content site. This repository merges on the Architect's LGTM, one PR
at a time. Importing the skills unchanged would have imported a competing
lifecycle into the same tree, which is the prod-integration problem again with
the arrow pointing the other way.

The test that worked there - *would another module need this sentence?* - works
here too, and answers no: nothing about auto-merge is specific to publishing, it
is just a different governance model.

**Lesson:** when an integration brings agent skills, the skills are methodology
and get merged like methodology. The module keeps what is specific to it (how to
register a source, how to place a chunk, what a house-style article looks like)
and defers everything procedural to the repository's flow.

**Codified:** `.claude/skills/atlas-add-source/` and
`.claude/skills/atlas-changelog-post/` keep the corpus-specific procedure and
delegate branch, PR, verification, and merge to `pr-flow` and `pr-verify`; both
state the non-negotiable explicitly - never merge your own PR.
`atlas-changelog-post` also drops the upstream's invented `marketing/`
directory and writes into `<module>/docs/articles/<date>-<slug>/`, the location
this repository already has for exactly that pair of artifacts.

## L5. A stage that names an artifact must also check that the artifact exists

The models lesson L6 established the article intake by creating the directory
the article lands in. That closed the gap halfway: the *place* existed, the
*edge* did not. Nothing anywhere would have noticed a module article that never
became a publication, and two such articles were already sitting unpublished
when this project started.

**Lesson:** the enforcement point is the check, not the destination. A stage is
landed when a build fails without it.

**Codified:** [`scripts/intake-module-article.mjs`](../../scripts/intake-module-article.mjs)
creates the entry; its `--check` mode fails when a module article has no entry
or when an entry's `articlePath` stops resolving; the `atlas` workflow runs it
on every PR, and its path filter includes `*/docs/articles/**` so the guard
fires on the PR that creates the debt rather than on some later atlas change.
The graph now names Atlas the [exit node](../../../sdlc/GRAPH.md#the-exit-node),
and both pre-existing articles were published as part of this project.

## L6. An anchored exclude and a link guard, costing nothing this time

The prod lesson L7 - `rsync --exclude 'README.md'` is not anchored and silently
dropped 21 nested READMEs - was applied directly: the copy used
`--exclude '/README.md'`, the module README survived, and the markdown link
guard was run before the copy was declared complete. Nothing broke, which is the
entire point of recording it here: the second integration paid for the first
one's debugging.

The same holds for the PII pre-scan. Scanning the source tree with the
repository's own patterns *before* copying found the only two violations
(co-author trailers inside the upstream skill files) while they were still
trivial to leave behind, rather than after they were in a commit.

**Lesson:** an integration checklist earns its keep on the integration after the
one that wrote it. Keep adding to it.

**Codified:** the sweep is now three steps, in this order - scan the source with
`tools/policy/check_pii.sh` and `gitleaks` before copying; copy with anchored
excludes; run `tools/policy/check_links.sh` before declaring the copy complete.
