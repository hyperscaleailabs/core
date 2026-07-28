# Evidence: atlas integration

Project: [issue #14](https://github.com/hyperscaleailabs/core/issues/14).
Collected 2026-07-28 on the integration branch, from a local production build.

**Evidence tier: process.** Nothing here is a claim about a physical or
simulated system - it is proof that the site builds from a clone, that the
corpus validates, that the publication intake works on real module articles, and
that the pages a reader will see actually render with links that resolve.

## Baseline

First accepted baseline for this module. Subsequent runs compare against it.

| Measure | Value |
|---------|-------|
| Pages built | 48 |
| Indexed documents | 35 |
| `astro check` diagnostics | 0 errors, 0 warnings, 0 hints |
| Collections registered | 9 (`case-studies`, `comparisons`, `foundations`, `frameworks`, `lab`, `learning-paths`, `news`, `patterns`, `production`) |
| Module policy guards | 5 of 5 |
| Module articles with Lab Notes entries | 3 of 3 |
| Toolchain | Node v24.18.0, npm 11.16.0, Astro 5.18.2 |

The counts include this project's own article and its published entry: the
intake was exercised on the project that built it, not only on the two it
inherited.

CI pins Node 20 (the version declared in `package.json` `engines`); this local
run used the host's Node 24, and both produce the counts above.

## Transcript

Host paths are replaced with `<repo>`. Per-page build lines are elided; the page
count is the assertion.

```text
$ node --version && npm --version
v24.18.0
11.16.0

$ make verify
npm run index

> agentic-atlas@0.1.0 index
> node scripts/build-search-index.mjs

Search index written: 35 documents -> public/search-index.json
node scripts/check-collections.mjs
collections registered consistently: case-studies, comparisons, foundations, frameworks, lab, learning-paths, news, patterns, production
npm run check

> agentic-atlas@0.1.0 check
> astro check

[content] Syncing content
[content] Synced content
[types] Generated 156ms
[check] Getting diagnostics for Astro files in <repo>/atlas...
Result (20 files):
- 0 errors
- 0 warnings
- 0 hints

npm run build

> agentic-atlas@0.1.0 build
> astro build

[build] output: "static"
[build] directory: <repo>/atlas/dist/
[vite] built in 379ms
 generating static routes
 ▶ src/pages/404.astro
 ▶ src/pages/[section]/[slug].astro
 ▶ src/pages/[section]/index.astro
 ▶ src/pages/about.astro
 ▶ src/pages/index.astro
 ▶ src/pages/licenses.astro
 λ src/pages/rss.xml.ts
[@astrojs/sitemap] `sitemap-index.xml` created at `dist`
[build] 48 page(s) built in 619ms
[build] Complete!
bash scripts/check-policy.sh
== no references to the pre-integration repository ==
ok
== repository URLs come from src/lib/repo.ts only (site code) ==
ok
== no committed build output, dependencies, or ingestion cache ==
ok
== no absolute home-directory paths ==
ok
== every article records at least one source ==
ok

atlas policy guards OK

$ make intake-check
node scripts/intake-module-article.mjs --all --check
ok  atlas/docs/articles/2026-07-28-atlas-integration/article.md -> atlas/src/content/lab/2026-07-28-atlas-integration.md
ok  models/docs/articles/2026-07-28-models-integration/article.md -> atlas/src/content/lab/2026-07-28-models-integration.md
ok  prod/docs/articles/2026-07-28-prod-integration/article.md -> atlas/src/content/lab/2026-07-28-prod-integration.md
```

## The publication intake, exercised

The guard is only worth its line in CI if it can fail. Both directions were
checked on this branch:

| Check | Command | Result |
|-------|---------|--------|
| Missing entry is caught | `--all --check` before the entries existed | **failed**, naming both module articles and where their entries belong |
| Entries resolve | `--all --check` after intake | **passed**, 3 of 3 |
| Drafting works from a real article | intake of the `models`, `prod`, and this project's own articles | entry written with title, description, provenance, tier, and a heading skeleton, marked `draft: true` |

The bodies were then written for an outside reader and published
(`draft: false`); re-running the intake on an existing entry refreshed only the
frontmatter and left the prose intact, which was verified by diff.

## The module policy guards, exercised

The five guards in `scripts/check-policy.sh` started life inline in the workflow
and failed on their own first CI run - the stale-reference grep matched its own
source line, and the URL rule over-matched content, where absolute source URLs
are the whole point of attribution. Moved into a script, scoped, and re-run:

```text
$ bash scripts/check-policy.sh
== no references to the pre-integration repository ==
ok
== repository URLs come from src/lib/repo.ts only (site code) ==
ok
== no committed build output, dependencies, or ingestion cache ==
ok
== no absolute home-directory paths ==
ok
== every article records at least one source ==
ok

atlas policy guards OK
```

Failing direction, with a reference to the origin repository planted in
`docs/architecture.md`:

```text
== no references to the pre-integration repository ==
./atlas/docs/architecture.md:98:<!-- decoy: ... -->
::error::reference to the pre-integration standalone repository; use atlas/src/lib/repo.ts
```

## The collection guard, exercised

The same test, applied to `scripts/check-collections.mjs`: the `lab` entry was
temporarily removed from `SECTION_META` and the guard was re-run.

```text
$ node scripts/check-collections.mjs
MISSING SECTION_META: collection 'lab' has a schema but no entry in src/lib/content.ts
exit=1
```

Restored, it passes. A guard that has never been seen to fail is a guard nobody
has tested.

## Walked surfaces

Captured from the local production build (`make preview`, `http://localhost:4321`)
with headless Chrome on a throwaway profile - logged out, no browser chrome, no
identity in the frame.

| Screenshot | What it proves |
|------------|----------------|
| [2026-07-28-atlas-home.png](2026-07-28-atlas-home.png) | The site builds and serves in the monorepo: hero, the article count reading **35**, `Lab Notes` in the navigation, and the section grid |
| [2026-07-28-atlas-lab-index.png](2026-07-28-atlas-lab-index.png) | The new `lab` section renders as a first-class section with all three entries, their levels, reading times, and tags |
| [2026-07-28-atlas-lab-article.png](2026-07-28-atlas-lab-article.png) | A published lab note end to end - this project's own: metadata, table of contents, provenance blockquote linking back to the module article, and the "Edit this page" link |

Outbound links were read from the rendered DOM of the `prod` lab note rather than
from the source, so the assertion is about what a reader would click:

```json
{
  "edit": "https://github.com/hyperscaleailabs/core/edit/main/atlas/src/content/lab/2026-07-28-prod-integration.md",
  "header/footer": "https://github.com/hyperscaleailabs/core/tree/main/atlas",
  "sources": [
    "https://github.com/hyperscaleailabs/core/blob/main/prod/docs/articles/2026-07-28-prod-integration/article.md",
    "https://github.com/hyperscaleailabs/core/blob/main/prod/docs/lessons/2026-07-28-prod-integration.md"
  ]
}
```

Every one points into this repository under `atlas/`. Before the repository
links were centralized in `src/lib/repo.ts`, all of them pointed at the
standalone repository the module came from - the site would have built, rendered,
and shipped readers to a tree that no longer moves.

## What this evidence does not cover

- **No deployed check.** The Vercel project's root directory has to be set to
  `atlas` for the deployment to follow the module; that is a dashboard setting
  outside this repository, so the deployed build is not evidenced here. The
  local run uses the exact command Vercel runs (`npm ci`, `npm run index && npm run build`).
- **No ingestion run.** `atlas-ingest.yml` was not executed: it opens a pull
  request and requires the `ATLAS_CONTENT_ISSUE` repository variable, neither of
  which is appropriate to trigger from an integration branch. Its Python entry
  point is syntax-checked in CI, and its guard for the missing variable is a
  plain `grep`. First real run will be its own evidence.
