# Deployment

Agentic Atlas is a static Astro site. It deploys to Vercel and reads its content
straight from the Markdown hierarchy in `atlas/src/content/`.

The site is one module of a monorepo, so the deployment is scoped to this
directory rather than to the repository root. Everything below assumes that.

## Vercel (recommended)

### One-time setup

1. In the [Vercel dashboard](https://vercel.com/new), **Add New → Project** and
   import the `core` repository.
2. **Set the project's Root Directory to `atlas`.** This is the one setting that
   is not in this repository and the one that breaks the build if it is missed:
   without it Vercel looks for `package.json` at the repository root, finds
   none, and fails. Everything else follows from it - `vercel.json`, the
   lockfile, and the content tree are all resolved relative to `atlas/`.
3. Vercel auto-detects **Astro**. The settings come from `vercel.json`:
   - **Install:** `npm ci`
   - **Build:** `npm run index && npm run build`
   - **Output:** `dist`
4. (Optional) **Environment variables:**
   - `SITE_URL` - your production URL (e.g. `https://agentic-atlas.vercel.app` or
     a custom domain). Drives canonical URLs, sitemap, and RSS.
5. **Deploy.** Every merge to `main` that touches `atlas/` triggers a production
   build; pull requests get preview deployments automatically.

Merging is what publishes. Nothing here bypasses the repository's
[lifecycle](../../sdlc/LIFECYCLE.md): the Architect's LGTM merges the PR, and
the merge deploys.

### Custom domain
Add it under **Project → Settings → Domains** and point DNS as Vercel instructs.
Then set `SITE_URL` to the custom domain and redeploy so metadata matches.

## How content reaches the site

The Markdown in `src/content/` is read **at build time** by Astro's content
collections. There is no runtime database and no external content fetch - the repo
*is* the CMS. To publish an edit: commit Markdown to `main`, and Vercel rebuilds.

The ingestion pipeline fits in cleanly: it opens PRs that add/modify Markdown;
merging a PR to `main` is what publishes that content, via the same rebuild.

## Secrets

- `ANTHROPIC_API_KEY` - **only** needed for the ingestion GitHub Action to draft
  articles with a model. Add it as a **repository secret** (Settings → Secrets and
  variables → Actions), *not* as a Vercel env var. The site build itself needs no
  secrets.

## Local production check

```bash
npm run index && npm run build   # exactly what Vercel runs
npm run preview                   # serve dist/ locally
```

If this passes locally, the Vercel build will pass.

## Alternative hosts

Because the output is a static `dist/`, any static host works (Netlify,
Cloudflare Pages, GitHub Pages, S3+CloudFront). Set the build command to
`npm run index && npm run build` and the publish directory to `dist`. Only Vercel
is configured out of the box via `vercel.json`.

## Troubleshooting

- **Build fails on a content error** - a frontmatter field is missing or the wrong
  type. The error names the file and field; fix per
  [content-guide.md](content-guide.md).
- **Links 404 in production but work locally** - check `trailingSlash`
  (`ignore` in `astro.config.mjs`, `cleanUrls` in `vercel.json`) and that
  internal links are root-relative (`/section/slug`).
- **RSS/sitemap URLs wrong** - set `SITE_URL` (or `site` in `astro.config.mjs`) to
  the real production URL.
