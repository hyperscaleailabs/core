# Architecture

How Agentic Atlas is put together, and why.

## Design goals

1. **Content is Markdown in Git.** The source of truth is a hierarchy of `.md`
   files. Everything else (site, pipeline) is tooling around that.
2. **Static, fast, cheap to host.** A content site should be a static build that
   any CDN — Vercel here — can serve.
3. **Self-extending.** Adding knowledge should be as easy as adding a link; a
   pipeline turns links into reviewable draft articles.
4. **Human-reviewed.** Machine drafts never publish themselves. They land in Git
   as drafts and go through a pull request.
5. **Typed content.** Frontmatter is schema-validated at build time so the corpus
   can't silently drift.

## The three subsystems

```
┌───────────────────────┐     reads      ┌────────────────────────┐
│  Content (src/content)│◀───────────────│  Site (Astro, static)  │──▶ Vercel/CDN
│  Markdown + frontmatter│                └────────────────────────┘
└───────────▲───────────┘
            │ writes drafts (draft: true, aiGenerated: true)
┌───────────┴───────────┐
│  Pipeline (pipeline/)  │◀── sources.yaml (+ registry.json state)
│  fetch → plan → draft  │
└───────────────────────┘
```

### 1. Content
- One file per article under a collection directory (`foundations/`,
  `frameworks/`, …).
- [`src/content.config.ts`](../src/content.config.ts) defines a glob loader and Zod schema per
  collection. `astro build` fails if any file violates it — the guardrail that
  keeps `level`, `sources`, `tags`, reading-time, etc. consistent.
- The URL of an article is `/{collection}/{slug}` where `slug` is the filename.

### 2. Site (Astro)
- **Static output** (`output: 'static'`) — pure HTML/CSS/JS, no server.
- Dynamic routes generate one page per collection and per article:
  - [`src/pages/[section]/index.astro`](../src/pages/%5Bsection%5D/index.astro) —
    a section listing, grouped by level.
  - [`src/pages/[section]/[slug].astro`](../src/pages/%5Bsection%5D/%5Bslug%5D.astro) —
    an article, rendered through `ArticleLayout`.
- [`src/lib/content.ts`](../src/lib/content.ts) centralizes collection access,
  reading-time computation, and section metadata.
- Design system lives in [`src/styles/global.css`](../src/styles/global.css)
  (Tailwind 4 `@theme` tokens + a few component classes). Dark-first, engineering
  aesthetic.
- RSS at `/rss.xml`, sitemap via `@astrojs/sitemap`.

### 3. Pipeline (Python)
See [pipeline.md](pipeline.md) for the deep dive. Architecturally it is a pure
**producer of Markdown**: it never touches the running site, it only writes files
into `src/content/` and updates `registry.json` and the search index. That clean
separation means the site has no runtime dependency on the pipeline.

## Data flow at build time

1. Vercel (or CI) runs `npm run index && npm run build`.
2. `build-search-index.mjs` scans content → `public/search-index.json`.
3. Astro reads content collections, validates frontmatter, renders static pages.
4. Output in `dist/` is served by the CDN.

## Reading-time enforcement

The house rule (5–15 min) is enforced in two places:

- The pipeline estimates minutes from word count and writes `readingTime`.
- The content schema bounds `readingTime` and every field, so an out-of-contract
  article fails the build.

Articles authored by hand can omit `readingTime`; the site computes it from the
body via `reading-time` at render.

## Why Astro

For a content-hierarchy site, Astro's content collections give type-safe
frontmatter, first-class Markdown/MDX, near-zero client JS by default, and
trivial static deployment to Vercel — a better fit here than a heavier app
framework. The content is portable regardless: it's just Markdown, so the site
layer could be swapped without touching a single article.

## Extending the system

- **New section?** Add a collection to `config.ts`, a `SECTION_META` entry in
  `lib/content.ts`, and (optionally) a classification rule in
  `pipeline/config.yaml`. The dynamic routes and the cross-section article list
  pick it up automatically, and `scripts/check-collections.mjs` fails the build
  if only one of the two registrations lands - which happened, and whose only
  symptom was a wrong article count on the home page.
- **New UI?** Components are plain Astro; add to `src/components/`.
- **Search UI?** `public/search-index.json` is already generated — wire a
  client-side filter or Pagefind over it.
