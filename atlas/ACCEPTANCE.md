# Acceptance criteria template: atlas

Per the [project lifecycle](../sdlc/LIFECYCLE.md#project-shape), every project that
touches this subproject includes these criteria in its acceptance criteria,
instantiated for the specific change. Cross-project work includes the template of
every subproject it touches.

- [ ] **The site builds and the corpus validates**: `make verify` is green -
      search index rebuilt, collections registered consistently, `astro check`
      reports zero errors, `astro build` passes (so every article's frontmatter
      satisfies the schema in `src/content.config.ts`), and
      `scripts/check-policy.sh` passes. The transcript is committed as evidence.
      `make verify` runs exactly what the `atlas` workflow runs: a guard the
      author cannot run before pushing is a guard first exercised on a hosted
      runner.
- [ ] **The committed search index matches a fresh rebuild**: `npm run index`
      leaves `public/search-index.json` unchanged. A generated file that is
      committed and never compared is a file, not a baseline.
- [ ] **Every module article has a Lab Notes entry**:
      `node scripts/intake-module-article.mjs --all --check` passes, and any
      entry added by this project links back to a module article that resolves.
- [ ] **Published claims carry their tier**: a Lab Notes entry states the
      `evidenceTier` of the strongest claim in its source article and never
      presents a lower tier as a higher one. Simulation is never reported as
      physical validation ([AXIS.md](../AXIS.md#guardrails)).
- [ ] **Attribution survives the change**: every article touched records its
      `sources` with publisher and, where known, license; original text is
      summarized and linked, never republished; the content license is declared.
- [ ] **The product surface was looked at**: a screenshot of the affected page
      from a local production build (`make preview`) is committed with the
      evidence. The corpus is the product here, and a schema-valid article that
      renders badly is still a defect.

## Compact regression (per-PR scale)

Deliberately compact - the corpus at its real size, which is small enough that
the full build *is* the regression:

1. `make verify` from `atlas/`: rebuild the index, type/schema check, full
   static build.
2. Compare against the **previous accepted baseline** in
   [docs/evidence/](docs/evidence/README.md): page count, indexed document
   count, and zero check errors. A change that moves page or document count
   states why; the new count becomes the baseline.
3. Commit the transcript to [docs/evidence/](docs/evidence/README.md).

The build is deterministic given the corpus, so "unchanged" means exactly equal
unless the change is intended to add or remove pages.

## Deployed verification

The site deploys on Vercel from this directory (project Root Directory `atlas`).
The deployed check is that the production build command Vercel runs is the one
verified locally:

```bash
cd atlas
npm ci && npm run index && npm run build   # exactly what Vercel runs
npm run preview                            # serve dist/ and walk the surface
```

Walking the surface is part of the gate, not a formality: open the changed
section index, open one article inside it, and confirm the "Edit this page" and
repository links resolve to this repository rather than to wherever the module
came from. Broken outbound links are the one defect class the build cannot see.

## Two-tier verification (module CI/CD DAG)

Per the [generic process template](../sdlc/LIFECYCLE.md#stages), change detection
decides depth on every PR and merge:

- **This module modified** -> full extensive verification: install, index
  freshness, collection registration, `astro check`, full build, the
  module-article intake guard, `scripts/check-policy.sh` (stale repository
  references, centralized repository URLs, no committed build output, no home
  paths, attribution on every article), and the pipeline's static checks.
- **Module untouched** -> only the less extensive top-API-level regression that
  runs across all modules on every merge. Note the asymmetry this module
  introduces: a **module article added anywhere else in the repository** makes
  the atlas intake guard fail, which is deliberate - the publication debt
  belongs to the project that created it.

## Promotion

Beyond the merge, this module follows [sdlc/PROMOTION.md](../sdlc/PROMOTION.md).
Its instances of the generic gates:

| Generic gate | This module's instance |
|--------------|------------------------|
| Self-gating product artifact | The corpus: the site build fails on any invalid article, so the product validates itself |
| Module regression baseline | Page count and indexed document count in `docs/evidence/` |
| Contract compatibility | `src/content.config.ts` - a schema change that invalidates existing articles is a breaking change and fixes them in the same PR |
| Observability gate | The deployed build log and the walked surface; there is no runtime to instrument, so the gate is the build and the page |
| Canary-always change class | Content schema changes, the ingestion pipeline's drafting path, and anything touching attribution or license rendering |

Evidence tiers apply ([AXIS.md](../AXIS.md#guardrails)): this module publishes
**other modules' evidence**, and its own work produces **process** evidence. A
lab note repeats the tier of the claim it summarizes and never upgrades it -
restating a simulation result as a validated one is the specific failure this
line exists to prevent.
