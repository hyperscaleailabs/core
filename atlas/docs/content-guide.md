# Content Authoring Guide

How to write (or review) an article for Agentic Atlas.

## The contract

Every article is a Markdown file under `src/content/<collection>/<slug>.md`. The
filename is the URL slug. Frontmatter must satisfy the schema in
[`src/content.config.ts`](../src/content.config.ts) - the build fails otherwise.

### Base frontmatter (all collections)

```yaml
---
title: "Specific, concrete title (<= 120 chars)"
description: "1–2 sentence summary shown in cards and meta (<= 320 chars)."
level: intermediate            # beginner | intermediate | advanced
readingTime: 9                 # minutes; optional (computed if omitted). Keep 5–15.
updated: 2026-06-30            # ISO date
tags: [tool-use, design]       # short, kebab-case
draft: false                   # true hides it in production builds
aiGenerated: false             # true = machine-drafted, shows a review banner
license: CC-BY-4.0             # defaults to CC BY 4.0
sources:                       # attribution — one entry per referenced work
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    license: "—"               # license of the ORIGINAL, if known
    accessed: "2026-06-30"
---
```

### Collection-specific extras

- **frameworks** — also requires `name`, `category`
  (`orchestration|sdk|protocol|rag|runtime|observability|eval|toolkit`),
  `maturity` (`experimental|beta|stable|mature`), `supportsMcp`,
  `supportsMultiAgent`; optional `repo`, `homepage`, `docs`, `codeLicense`,
  `language`, `maintainer`.
- **case-studies** — requires `company`; optional `domain`.
- **lab** — requires `module`, `project`, `articlePath` (the repository-relative
  path of the module article it publishes), and `evidenceTier`; optional
  `issue`, `pr`. Do not hand-create these: run
  `scripts/intake-module-article.mjs` and write the body it drafts
  (see [../README.md](../README.md#from-module-article-to-atlas-entry)).
- **news** — requires `published`.
- **patterns** — optional `problem`, `alsoKnownAs`.
- **learning-paths** — optional `steps`.

## House style

- **Audience:** competent software engineers and architects. Assume they can
  code; don't explain what an API is.
- **Bias to tradeoffs.** Prefer "when to use / when not to", failure modes, and
  cost/latency/reliability implications over feature lists and hype.
- **Length:** a 5–15 minute read (~900–2200 words). Don't pad to hit a number.
- **Open with why it matters** in 1–2 sentences. No "In this article, we will…".
- **Structure** with `##` H2s (they populate the on-page table of contents) and
  `###` where useful.
- **Use the right representation.** A comparison → a table. A flow → a short ASCII
  or fenced diagram. A decision → a numbered heuristic. Avoid walls of prose.
- **End with a "Next" section** linking 2–3 related Atlas pages with relative
  links: `[tool use](/patterns/tool-use)`.

## Integrity rules (non-negotiable)

- **Summarize and link; never copy.** Articles are original prose that analyze
  primary sources. Do not reproduce source text or code beyond brief, attributed
  quotes.
- **Only assert what the source supports.** No invented APIs, numbers, or quotes.
  When unsure, hedge or omit.
- **Attribute everything.** Every external claim traces to an entry in `sources`.
  The site renders these as a "Sources & attribution" block automatically.

## Linking

Use root-relative links between articles: `/production/failure-modes`,
`/frameworks/langgraph`. This keeps links valid regardless of deployment domain
and lets the build catch typos indirectly (dead internal links surface in review).

## Preview before you commit

```bash
npm run dev       # live preview at localhost:4321
npm run build     # validates frontmatter across the whole corpus
```

A failed build almost always means a frontmatter field is missing or the wrong
type — read the error; it names the file and field.

## Reviewing a machine-drafted article

When a pipeline PR arrives:

1. Open each `aiGenerated: true` file and its primary source side by side.
2. Verify every claim is supported and no source text was copied.
3. Fix tone/accuracy; tighten to the 5–15 min band.
4. Remove `draft: true` to publish. Keep or remove `aiGenerated` per your policy
   on labeling reviewed-but-machine-originated content.
