# Atlas

The lab's **public publication surface**: a technical field guide to AI agents
for the engineers and architects who ship agentic systems to production, and the
place where this repository's own projects are published as lessons the outside
world can read.

Two audiences, one site. **Agentic Atlas** is the outward half - foundations,
a framework catalog, architectural patterns, production failure modes and
tradeoffs, and case studies drawn from public engineering writing. **Lab Notes**
is the inward half: every project in this monorepo ends in a module article, and
that article becomes an entry here with its evidence trail attached.

- Public surface, Apache-2.0 code and CC BY 4.0 content by design (see
  [Licensing](#licensing)).
- Static Astro 5 build, deployed on Vercel from this directory; migration into
  the shared k3d deployment happens where it makes sense, not before.
- Incorporated work is referenced with careful attention to its original
  license: Atlas summarizes, analyzes, and links; it does not republish.

Acceptance criteria template for projects touching this subproject:
[ACCEPTANCE.md](ACCEPTANCE.md).

All command examples in this subproject's docs are written relative to `atlas/` -
run them from this directory (`cd atlas`), not the repo root.

## Layout

| Path | Purpose |
|------|---------|
| `src/content/` | The corpus: one Markdown file per article, in typed collections. The build validates every file's frontmatter against [`src/content/config.ts`](src/content/config.ts) |
| `src/pages/`, `src/layouts/`, `src/components/` | The Astro site. Section index and article pages are generic over the collections, so a new collection is a schema plus a `SECTION_META` entry |
| `src/lib/repo.ts` | Single source of truth for every "view / edit / report on GitHub" link. CI fails the build on a hardcoded repository URL anywhere else in `src/` |
| `pipeline/` | The ingestion pipeline: diff `sources.yaml` against the registry, fetch (robots-aware), extract, plan, draft, index, open a PR. Nothing auto-publishes |
| `scripts/build-search-index.mjs` | Rebuilds `public/search-index.json` from the corpus. Committed and CI-verified against a fresh rebuild |
| `scripts/intake-module-article.mjs` | Module article -> Lab Notes entry; also the `--check` guard that CI runs |
| `scripts/check-policy.sh`, `scripts/check-collections.mjs` | The module's guards, in scripts so `make verify` runs exactly what CI runs |
| `docs/` | Content guide, site architecture, pipeline reference, deployment - plus this module's `articles/`, `evidence/`, and `lessons/` |

## Quick start

```bash
cd atlas
make install      # npm ci
make dev          # live preview at http://localhost:4321
make verify       # index + astro check + build - exactly what CI runs
```

Without `make`, the underlying commands are `npm ci`, `npm run dev`, and
`npm run index && npm run check && npm run build`.

The ingestion pipeline is optional for site work:

```bash
cd atlas
python3 -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
cp .env.example .env                              # ANTHROPIC_API_KEY enables drafting
python pipeline/ingest.py --dry-run --limit 3     # see what it would do
```

## Content model

Everything is Markdown under `src/content/`, one file per article, in collections
whose frontmatter the build **enforces** - a schema violation fails
`npm run build`, which is what keeps the corpus consistent without a style
police.

| Collection | What it holds |
|------------|---------------|
| `foundations/` | What an agent is, the pre-agentic era, LLM-to-agent evolution, anatomy, glossary |
| `frameworks/` | Catalog: LangChain, LangGraph, Claude Agent SDK, Strands, MCP, A2A, GraphRAG Toolkit |
| `patterns/` | Tool use, reflection, planning, multi-agent orchestration, swarms, context engineering, RAG/GraphRAG |
| `production/` | Failure modes, long-running harnesses, evaluation, observability, guardrails |
| `comparisons/` | Framework matrix, failure-mode and tradeoff tables |
| `case-studies/` | Other people's deployments, from public engineering writing |
| `lab/` | **Our own projects**, one entry per module article, with module, issue, PR, evidence tier, and the path back to the source article |
| `news/` | Aggregated ecosystem developments (pipeline-generated) |
| `learning-paths/` | Curated tracks: beginner to first agent, and the architect's track |

Every article is sized for a 5-15 minute read and records `level`, `tags`,
`updated`, `sources` (attribution), and `license`. See
[docs/content-guide.md](docs/content-guide.md) for how to write one.

## From module article to Atlas entry

The [project lifecycle](../sdlc/LIFECYCLE.md#stages) ends every project with an
article in its owning module, and states that publishing it triggers the Atlas
update. This is that trigger, as a mechanism rather than a sentence.

Per-project articles live in their owning module as
`<module>/docs/articles/<YYYY-MM-DD>-<project>/` (`article.md` for the Architect
and PM audiences, `post.md` as the platform-neutral social variant), produced by
the RESEARCHER/PUBLISHER stage. Atlas aggregates and publishes; it does not host
the sources.

```bash
cd atlas
node scripts/intake-module-article.mjs \
     ../models/docs/articles/2026-07-28-models-integration/article.md \
     --issue 7 --pr 8 --tier smoke
```

The script writes `src/content/lab/<date>-<project>.md` with the title, a
description, provenance (`module`, `project`, `articlePath`, `issue`, `pr`), the
`evidenceTier`, a source entry pointing at the module article, and a summary
skeleton built from the article's own headings. It marks the new entry
`draft: true`: **the intake drafts, a writer publishes.** Re-running on an
existing entry refreshes only the frontmatter it owns and keeps the body, so
hand-written prose survives.

The lab note is a rewrite for an outside reader, not a copy. The module article
is the record of what happened for people with repository context; the lab note
answers "why would a stranger care", and links back for the rest.

Enforcement: `node scripts/intake-module-article.mjs --all --check` fails when a
module article has no Lab Notes entry, or when an entry's `articlePath` no
longer resolves. The atlas CI workflow runs it on every PR. Cross-module
publications are different artifacts and do not pass through here: whitepapers
live in [docs/projects/](../docs/projects/) and weekly digests in
[docs/weekly/](../docs/weekly/).

## The ingestion pipeline

The outward half of the corpus extends itself. Add a link to
`pipeline/sources.yaml`; on the next run the pipeline diffs it against
`pipeline/registry.json` by content hash, ETag, and a declared `version`, fetches
what is new (honoring `robots.txt`), extracts the readable content, classifies
section and level, drafts a 5-15 minute article, rebuilds the search index, and
opens a pull request.

Everything it writes is marked `draft: true` and `aiGenerated: true`, and
**nothing auto-publishes** - a human reviews every draft, and the PR goes through
the same [lifecycle](../sdlc/LIFECYCLE.md) as any other change: full PR template,
issue linkage, Architect LGTM, squash merge. Details in
[docs/pipeline.md](docs/pipeline.md).

## Deployment

The site is a static build deployed on Vercel from this directory. The Vercel
project's **Root Directory is `atlas`**; the rest of the configuration comes from
[vercel.json](vercel.json) - install `npm ci`, build
`npm run index && npm run build`, output `dist`. `SITE_URL` overrides the
canonical/sitemap/RSS origin. [docs/deployment.md](docs/deployment.md) covers
custom domains, secrets, and static hosts other than Vercel.

Because the output is a static directory, the eventual move into the shared k3d
deployment ([infra/](../infra/)) is a hosting change, not a rewrite.

## Licensing

This module deviates from the repository default and carries its own notices:

- **Code** (site, components, scripts, ingestion pipeline): Apache-2.0, the
  repository default - [LICENSE](../LICENSE).
- **Written content** under `src/content/`: CC BY 4.0 -
  [LICENSE-CONTENT](LICENSE-CONTENT), unless an article's frontmatter declares a
  different `license`.
- **Third-party material**: referenced, never republished. Each article records
  its sources with publisher and, where known, license. Provenance and trademark
  notice: [NOTICE.md](NOTICE.md).

## Provenance

Agentic Atlas was developed as a standalone public repository and integrated
here as the `atlas/` module. The site, corpus, pipeline, and docs came across
intact; the standalone repository's publishing methodology did not - its agent
skills auto-merged green PRs with no human gate, and this repository's
[lifecycle](../sdlc/LIFECYCLE.md) is canonical. The equivalent skills
(`.claude/skills/atlas-add-source/`, `.claude/skills/atlas-changelog-post/`) run
the repository's flow instead.

See the root [README](../README.md) for repository rules (public repo: no PII,
squash merges, policy checks required).
