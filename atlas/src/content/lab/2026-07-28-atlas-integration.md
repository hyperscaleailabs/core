---
title: "The stage that named an artifact and never checked for it"
description: "Our lifecycle said every project ends in a published article. Nothing checked that it did, and two finished projects were sitting unpublished. Closing that gap, plus three defects no green build could see."
level: "advanced"
updated: 2026-07-28
created: 2026-07-28
tags: [lab-notes, atlas, ci, process, migration, publishing]
module: "atlas"
project: "atlas-integration"
articlePath: "atlas/docs/articles/2026-07-28-atlas-integration/article.md"
issue: 14
pr: 15
evidenceTier: "process"
draft: false
aiGenerated: false
license: "CC-BY-4.0"
sources:
  - title: "The stage that named an artifact and never checked for it (module article)"
    url: "https://github.com/hyperscaleailabs/core/blob/main/atlas/docs/articles/2026-07-28-atlas-integration/article.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
  - title: "Lessons from the atlas integration project"
    url: "https://github.com/hyperscaleailabs/core/blob/main/atlas/docs/lessons/2026-07-28-atlas-integration.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
---

> Field notes from the `atlas` module - this site. Full article, evidence, and
> review trail in
> [the module article](https://github.com/hyperscaleailabs/core/blob/main/atlas/docs/articles/2026-07-28-atlas-integration/article.md).
> This entry is the first thing the mechanism it describes produced about
> itself.

Our development lifecycle has a stage saying every project ends in a published
article. It had been true as prose for two projects. Nothing anywhere checked
that the publication happened, and by the time this project started, two
finished projects had articles written, reviewed, and merged - and never
published.

That is the ordinary shape of process debt. The stage existed, the destination
existed, everyone involved agreed with it, and the edge between them was carried
entirely by memory.

## What "landed" had to mean

Moving the site into the monorepo was the easy half. The half worth writing
about is the mechanism:

- A script reads a module's project article and drafts the corresponding
  published entry - title, description, and provenance: which module, which
  issue, which pull request, and the repository path back to the source.
- The same script has a `--check` mode that fails when a module article has no
  published entry, or when an entry's path back to its source stops resolving.
- CI runs it on **every** pull request that touches any module's article
  directory. That path filter is the load-bearing part: the check fires on the
  PR that creates the publication debt, not on some later change to the site,
  where it would be somebody else's problem.
- The script drafts; a person writes. The entry lands marked as a draft with a
  heading skeleton, and re-running it on an existing entry refreshes only the
  frontmatter and keeps the prose.

The last point matters more than it looks. A generator that overwrites what a
writer improved gets run once and then avoided, and an avoided tool is a
disabled check.

## Three defects a green build could not see

**Every outbound link in the migrated site pointed at the repository it had just
left.** "View on GitHub", "Edit this page", the license link. The build was
green, every page rendered, the type and schema checker reported nothing. A
reader clicking "Edit this page" would have landed in a repository that no
longer moves; a license audit would have followed the same dead link. Our
existing migration checklist covered old filenames and old command examples -
*text*. These were live URLs inside components, and the only place they are
visible is the rendered page.

**A new content section registered in three of four places reported the wrong
number.** Adding a section needs its schema, its display metadata, the
cross-section article list, and the home page grid. The third was missed. Every
page rendered, every link worked, the section had its own index - and the home
page said 32 articles for a site that had 34. Nothing looked broken, which is
strictly worse than a missing page, because there is no symptom to chase.

**The new CI guards had nowhere to run before CI.** They shipped as inline steps
in the workflow file. Everything runnable locally was run before pushing, and
the pull request still came back red on its first run, because the guards
themselves had never executed anywhere at all. Two defects, both found by their
own first execution: one grep matched its own source line, and one over-matched
the article corpus, where absolute source URLs are exactly what attribution
*is*.

## What we changed

- The repository URLs got one home, and two guards keep them there.
- The duplicated collection list is **gone** rather than guarded - it is now
  derived from the display metadata - and a small script guards the single
  coupling that remains, in both directions.
- All the module guards moved into a script the author runs with one command,
  which CI then calls in one line. A check you cannot run locally is a check
  that debugs itself in front of your reviewer.

Each of those was a mechanical finding, and the standing rule here is that a
mechanical finding becomes a guard in the same change that found it. Otherwise
the finding is a story, and the next person gets to rediscover it.

## The part that has to survive contact with a public page

A published entry repeats the **evidence tier** of the claim it summarizes, and
never upgrades it. The entry for our simulation control plane says
`simulation-demo`, because a release decision it emits is a statement about a
simulated population under declared failure distributions - not about anything
physical.

That distinction is easy to hold in an internal document and easy to lose on a
public one, where the incentive runs entirely one way. Encoding it in the
content schema means rounding up has to be done deliberately, by editing a typed
field, rather than by writing a slightly warmer sentence.
