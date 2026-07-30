---
title: "A missing link is invisible to a broken-link checker"
description: "The repository link check was green while the root deployment table named four modules without linking to their documentation. Every declared edge worked. Four required edges did not exist."
level: "advanced"
updated: 2026-07-30
created: 2026-07-29
tags: [lab-notes, sdlc, doc-navigation]
module: "sdlc"
project: "doc-navigation"
articlePath: "sdlc/docs/articles/2026-07-29-doc-navigation/article.md"
issue: 16
pr: 17
evidenceTier: "process"
draft: false
aiGenerated: false
license: "CC-BY-4.0"
sources:
  - title: "A missing link is invisible to a broken-link checker (module article)"
    url: "https://github.com/hyperscaleailabs/core/blob/main/sdlc/docs/articles/2026-07-29-doc-navigation/article.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
---

> Field notes from the `sdlc` module. Full article, evidence, and
> review trail in [the module article](https://github.com/hyperscaleailabs/core/blob/main/sdlc/docs/articles/2026-07-29-doc-navigation/article.md).

The repository link check was green while the root deployment table named four
modules without linking to their documentation. Every declared edge worked.
Four required edges did not exist.

## Why green was not complete

A broken-link checker starts with the links it can see. It can prove that a
declared target exists and that an anchor resolves, but it cannot infer that a
table cell should have contained a link in the first place.

That distinction mattered in the deployment table. Meet, Agents, Models, and
D-twins were named as backing modules in inline code. Readers could find them
elsewhere in the repository, but the table that mapped product surfaces to
components did not provide the path.

## The contract behind the table

The `Backed by` column is a navigation interface. Each data row must link to at
least one component document. The policy now checks that structural promise,
then passes every declared target to the ordinary link validator.

The new assertion was run against the original table before the links were
added. It reported all three bad cells and exited nonzero. After the four module
references became links, the same command passed.

## A second blind spot

The project article exposed a related problem. Its first draft contained a
broken relative link, yet the local checker reported success because it scanned
only files already tracked by Git.

The scanner now includes tracked and non-ignored untracked Markdown. New
documentation is checked before staging, while ignored dependency trees remain
outside the scan.

## Evidence

The final review checked repository Markdown targets and anchors, traversed the
documentation graph from the root, built all 49 Atlas pages, and crawled 1,625
local routes and fragments without a failure.

The evidence tier is process. These results describe deterministic
documentation and build checks, not a simulated or physical system.

## The reusable lesson

Navigation completeness and target validity need separate assertions. One asks
whether a required edge exists. The other asks whether that edge resolves.
Documentation infrastructure needs both.
