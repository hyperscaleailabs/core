# The Ingestion Pipeline

`pipeline/ingest.py` turns a curated list of reference links into reviewable draft
articles. This document explains how it works and how to operate it.

## Mental model

The pipeline is an **idempotent producer of Markdown**. Run it as often as you
like; it only does work for sources that are *new* or *changed* since last time,
and it never publishes on its own — output is always a draft in Git awaiting
review.

```
sources.yaml ─┐
              ├─▶ diff (registry.json) ─▶ fetch ─▶ extract ─▶ plan ─▶ draft ─▶ write .md
registry.json ┘                                                                    │
                                                        rebuild index ◀────────────┘
                                                        update registry
```

## Inputs

### `pipeline/sources.yaml`
The one file you edit to add content. Each entry is a URL, optionally with
overrides:

```yaml
sources:
  - https://example.com/simple-link            # bare URL, everything auto-classified
  - url: https://example.com/detailed
    section: patterns          # foundations|frameworks|patterns|production|
                               # comparisons|case-studies|news|learning-paths
    level: advanced            # beginner|intermediate|advanced
    title: "Optional title override"
    publisher: "Example Corp"  # attribution
    license: "Apache-2.0"      # license of the ORIGINAL material
    tags: [retrieval, rag]
    version: 1                 # bump to force reprocessing on a content refresh
```

### `pipeline/config.yaml`
Pipeline behavior: the Claude `model`, `max_output_tokens`, reading-time band,
draft policy, networking (user agent, timeout, `respect_robots`), the content
license, and the **classification rules** used when a source has no explicit
section/level.

### `pipeline/registry.json`
The processed-state, committed to Git so it's shared across CI runs. Keyed by
URL; records content hash, ETag/Last-Modified, version, and where the article was
written. This is what makes runs incremental.

## The stages

### 1. Diff
For each source, the pipeline looks up its registry entry. It will process the
source when any of these hold: it's new, the `version` was bumped, `--force`/
`--force-all` was passed, or the fetched content hash differs from what's on
record.

### 2. Fetch
A conditional `GET` (sends `If-None-Match`/`If-Modified-Since` from the registry).
A `304 Not Modified` short-circuits the source. **robots.txt is honored** when
`respect_robots: true` — disallowed URLs are skipped and logged. A snapshot of
the extracted text is cached under `pipeline/cache/` for provenance.

### 3. Extract
Main-content extraction via `readability-lxml` when available, falling back to a
BeautifulSoup text extraction. Produces a `(title, text)` pair; text is truncated
to a sane length before it's fed to the model.

### 4. Plan
Classifies the source into a section and level (respecting explicit overrides,
else the rules in `config.yaml`), then produces a plan: title, description, tags,
slug, an outline of H2s, and key points. With an API key this is a model call
using [`prompts/plan.md`](../pipeline/prompts/plan.md); without one it's a safe
heuristic plan.

### 5. Draft
With `ANTHROPIC_API_KEY` set, the pipeline drafts the article body with the
configured Claude model using [`prompts/draft.md`](../pipeline/prompts/draft.md) —
original prose that summarizes and analyzes the source (never copies it), sized
to 5–15 minutes. Without a key, it writes a **structured outline stub** with the
planned headings and TODOs for a human to complete.

Every generated file gets frontmatter with `draft: true`, `aiGenerated: true`, a
computed `readingTime`, and a `sources` block for attribution — so it validates
against the content schema and is clearly labeled in the UI.

### 6. Index + registry
Rebuilds `public/search-index.json` and writes the updated `registry.json`.

## Running it

```bash
# From atlas/, with pipeline deps installed:
python pipeline/ingest.py                 # full incremental run
python pipeline/ingest.py --dry-run       # fetch + plan, write nothing
python pipeline/ingest.py --plan-only     # print JSON plans, no drafting
python pipeline/ingest.py --limit 5       # process at most 5 new sources
python pipeline/ingest.py --force <url>   # reprocess one URL
python pipeline/ingest.py --force-all     # ignore the registry entirely
python pipeline/ingest.py --index-only    # only rebuild the search index
```

Enable model drafting by exporting a key (or putting it in `.env`):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## In CI

[`.github/workflows/atlas-ingest.yml`](../../.github/workflows/atlas-ingest.yml)
runs weekly and on manual dispatch (with `limit` / `force_all` inputs). It
installs deps, runs the pipeline, validates the site still builds, and opens a
pull request labeled `content`, `automated`, `needs-review`. Add
`ANTHROPIC_API_KEY` as a repository secret to enable model drafting in CI;
without it the job still succeeds and produces stubs.

The PR it opens is an ordinary PR under this repository's
[lifecycle](../../sdlc/LIFECYCLE.md): full template, `Horizon: short`, and
`Issue: #N` taken from the `ATLAS_CONTENT_ISSUE` repository variable, because
`sdlc / pr-discipline` checks every PR and automation is not an exception. The
job fails before ingesting when that variable is unset, rather than spending a
model budget on a PR that cannot pass its own checks.

## Review workflow

1. The action opens a PR with new/changed drafts + registry update.
2. A human reviews each drafted article **against its primary source** - checking
   accuracy, attribution, and that no source text was copied.
3. To publish: remove `draft: true` (and, once verified, `aiGenerated: true` if
   you consider it human-owned), get the Architect's LGTM, and squash merge.
   Merging is what deploys.

## Design notes & safety

- **Graceful degradation.** Missing `readability`/`anthropic` libs or API key
  never crash the run; the pipeline downgrades cleanly.
- **No copying.** Prompts instruct summarize-and-link only; the attribution block
  and per-article `sources` make provenance explicit.
- **Respectful crawling.** robots.txt-aware, identifiable user agent, conditional
  requests to avoid re-downloading unchanged pages.
- **Deterministic placement.** A source always maps to `/{section}/{slug}`, so
  re-runs update the same file rather than duplicating.
