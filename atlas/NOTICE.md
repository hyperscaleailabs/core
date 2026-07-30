# NOTICE

Atlas (the Agentic Atlas site and its corpus)
Copyright 2026 hsailabs contributors.

Developed as the standalone public repository
`github.com/hyperscaleailabs/agentic-atlas` (Apache-2.0 code, CC BY 4.0 content)
and integrated into this monorepo as the `atlas/` module. This file is the
provenance record; see also [README.md](README.md#provenance).

This is the one file in the repository permitted to name the origin repository,
so that a license audit can find it. Everywhere else - the site, the docs, the
pipeline - repository links come from `src/lib/repo.ts` and point here, because
a link into a repository that no longer moves is a dead end for the reader. The
atlas CI workflow enforces both halves of that rule.

## Dual licensing

- **Source code** - the site, its components and layouts, the build scripts, and
  the ingestion pipeline - is licensed under the Apache License, Version 2.0,
  the repository default. See [LICENSE](../LICENSE).
- **Written content** - articles, comparisons, glossary, lab notes, and other
  original prose under `src/content/` - is licensed under the Creative Commons
  Attribution 4.0 International License (CC BY 4.0), unless an individual
  article's frontmatter declares a different `license`. See
  [LICENSE-CONTENT](LICENSE-CONTENT).

Both are compatible with public Apache-2.0 distribution of this repository, per
the [licensing rules](../README.md#licensing) for subprojects that deviate from
the default.

## Third-party material

Atlas is a technical reference. Articles summarize, analyze, and link to primary
sources; they do not republish third-party text or code. All referenced material
- vendor documentation, engineering blog posts, papers, and open-source projects
- remains the property of its respective authors and is subject to its own
license and copyright. Each article's "Sources and attribution" section, and the
`sources` field in its frontmatter, record the referenced works with their
publisher and, where known, their license.

Product and company names referenced throughout (including but not limited to
LangChain, LangGraph, Anthropic, Claude, AWS, Google, Hugging Face, and the
Model Context Protocol) are trademarks of their respective owners. Their mention
is nominative and does not imply endorsement.

If an attribution is incorrect, or material should be removed, open an issue on
this repository and it will be addressed.
