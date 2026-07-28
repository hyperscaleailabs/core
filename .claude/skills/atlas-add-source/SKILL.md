---
name: atlas-add-source
description: Ingest one or more reference URLs into the Atlas corpus - register the source, run the ingestion pipeline, write schema-valid Markdown, gate on a local build, and hand the PR to the Architect. Use when asked to add links to the site, ingest sources, or turn a batch of URLs into articles.
---

# atlas-add-source

Turn a list of links into attributed Atlas articles. All work happens in
`atlas/`; the change ships through this repository's normal cycle, so run
`pr-flow` for the branch, PR, and review steps and use this skill only for what
is specific to the corpus.

**This is not an auto-merge flow.** The skill this was adapted from published by
merging its own green PR with no human gate. Here, the Architect's LGTM merges,
one PR is in flight at a time, and the PR carries the full template with
`Issue: #<number>` (see [sdlc/LIFECYCLE.md](../../../sdlc/LIFECYCLE.md)). Never
push to `main`, never merge your own PR, never bypass CI.

Ground rules for content live in
[`atlas/docs/content-guide.md`](../../../atlas/docs/content-guide.md) and the
enforced schema in
[`atlas/src/content/config.ts`](../../../atlas/src/content/config.ts). Read them;
they are not duplicated here.

## Inputs

One or more URLs. **All URLs in a batch go onto one branch and one PR** - a
batch is one unit of work, not one per link.

## Procedure

### 1. Frame and branch
Run `pr-flow` step 1 (horizon: short; the goal is corpus coverage, the
acceptance criteria are the ones in
[`atlas/ACCEPTANCE.md`](../../../atlas/ACCEPTANCE.md) instantiated for these
sources) and create the worktree.

### 2. Register and run the pipeline
Append an entry per URL to `atlas/pipeline/sources.yaml` with real metadata:
pick `section` and `level` using the classification rules in
`atlas/pipeline/config.yaml`, and set `publisher`, `tags`, and the `license` of
the *original* work when known. Then, from `atlas/`:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
export ANTHROPIC_API_KEY=...          # optional; enables model drafting
python pipeline/ingest.py --force <url>
```

The pipeline records each URL in `pipeline/registry.json`, caches a snapshot,
and drafts Markdown - or an outline stub when no key is set.

### 3. Handle skipped and thin sources
The pipeline honors `robots.txt` and skips disallowed URLs. If a URL is skipped,
or the extract is thin (JS-only page, login wall, stub output), fetch it
yourself and hand-author the article - but still record the URL in
`sources.yaml` and `registry.json` so state stays consistent. If content cannot
be sourced cleanly at all, **stop and report**; do not publish a stub.

### 4. Analyze, chunk, place
Compare the source against `atlas/src/content/**` and decide per chunk:

- **New article** - a genuinely additive topic.
- **Update** - an existing article covers it; extend that file.
- **Cross-link or glossary entry** - a small concept.

Prefer enriching and cross-linking over duplicating pages. One source often
yields one new page plus two enrichments.

### 5. Write schema-valid Markdown
- **New:** `created` and `updated` are today.
- **Updated:** preserve the original `created`, bump `updated`, and add a
  visible dated update note in the body.
- 5-15 minute reads. **Summarize and analyze; never copy source text.**
- Every file carries at least one `sources` entry - CI fails without it.
- Respect the original license, and record it.
- Set `aiGenerated: true` when a model drafted it. Leave `draft: true` until a
  human has read the article against its primary source; the Architect's review
  is that read.

### 6. Verify locally before pushing
From `atlas/`:

```bash
make verify        # index + astro check + build
make intake-check  # module articles all have Lab Notes entries
make preview       # walk the new pages; check the outbound links resolve
```

All must pass. Then run `pr-flow` step 4 (repo policy checks) and open the PR
with `pr-verify`.

### 7. Report
Report created versus updated articles, the sources registered, and the PR link.
State plainly which articles are still `draft: true` and what a reviewer has to
read to publish them.
