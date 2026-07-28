# The repository graph

The repository is a **graph**, and the root [README.md](../README.md) is its
**entrance node**. Every artifact is reachable from it by following links, and
every artifact links back toward its anchors. Agents do not scan the tree;
they **traverse the graph** and pull only the context the current project
phase requires.

**Always start at the root README** - for reading and for writing. Its
[Start here](../README.md#start-here) block fetches the graph, the axis, the
strategic directions, the relevant agents, and the relevant skills, and gives
the SDLC guidance in one paragraph. Any change to documentation begins there
too: before committing, confirm the documents you touched still trace from
the root README and that nothing in it became inconsistent with them.

## Nodes and edges

```text
root README.md  (entrance)
  -> AXIS.md / MISSION.md / docs/strategic/   (direction)
  -> sdlc/                                    (method: levels, stages, this file;
                                               PROMOTION.md past the merge;
                                               process lessons in sdlc/docs/lessons/)
  -> executive/                               (CEO / CTO standing validation)
  -> <module>/README.md                       (one per top-level directory)
       -> <module>/ACCEPTANCE.md              (acceptance criteria template
                                               + module-specific adjustments)
       -> <module>/docs/                      (articles, evidence, lessons)
  -> projects: GitHub issues                  (one issue per project)
       <-> PRs (Issue: #N, module-bounded)    (implementation + review trail)
       -> evidence (SHA-pinned links)
       -> article + post                      (<module>/docs/articles/<date>-<project>/)
            -> atlas/src/content/lab/         (the published entry; the exit node)
docs/  (cross-module only: strategic/, adr/, projects/ whitepapers, weekly/ digests)
```

Edges are ordinary markdown links and the `Issue: #N` field on PRs. Both are
guarded: `tools/policy/check_links.sh` (files and anchors) and
`sdlc / pr-discipline` (issue linkage).

## The exit node

The root README is the entrance; [atlas/](../atlas/README.md) is the **exit**.
Every project's article leaves the graph through it as a published Lab Notes
entry carrying the module, the issue, the PR, the evidence tier, and the path
back to the source article.

That edge is a mechanism, not an intention:
`atlas/scripts/intake-module-article.mjs` creates the entry, and its `--check`
mode - run by the `atlas` workflow on every PR that touches any module's
`docs/articles/` - fails when a module article has no entry, or when an entry's
`articlePath` stops resolving. The procedure is
[atlas/README.md#from-module-article-to-atlas-entry](../atlas/README.md#from-module-article-to-atlas-entry).

A module article without a published entry is an unfinished project, in the same
way a PR without evidence is an unfinished PR.

## Placement rules

- **Module-specific artifacts live in the module.** Evidence about a module's
  behavior or its projects (a training run, a benchmark, a module CI run, the
  project's process evidence) goes to `<module>/docs/evidence/`; module
  lessons to `<module>/docs/lessons/`; project articles to
  `<module>/docs/articles/<date>-<project>/` (`article.md` + `post.md`).
- **Top-level `docs/` holds only cross-module content**: strategy
  (`docs/strategic/`), repo-shaping ADRs (`docs/adr/`), cross-module project
  whitepapers (`docs/projects/`), and weekly publications (`docs/weekly/`).
  Process lessons live with the process in `sdlc/docs/lessons/`.
- **Published prose lives in `atlas/src/content/`, and only there.** The module
  article is the record; the Atlas entry is the publication, rewritten for a
  reader with no repository context. Atlas aggregates and publishes - it never
  becomes the only copy of something, and a module never renders its own site.
  Cross-module publications keep their own homes (`docs/projects/`,
  `docs/weekly/`) and do not pass through the module-article intake.
- A misplaced artifact is a broken edge: it will not be found from the node
  that needs it. Placement is reviewed in the cleanup-and-refinement stage of
  every project.

## How agents pull context

Per [project stage](LIFECYCLE.md#stages), enter at the node closest to the
task and read outward only as needed:

| Stage | Entry node | Pull |
|-------|-----------|------|
| 1 Architect intent | root README | AXIS.md; the touched modules' READMEs |
| 2 MGMT documents | project issue | strategic package, module ACCEPTANCE.md files, prior related issues/PRs |
| 3 BUILDER | handoff pack | module code + docs; module lessons |
| 4 QA | PR | module ACCEPTANCE.md, CI definitions, evidence placement rules |
| 5 Acceptance review | issue + PR trail | evidence tables, prior review comments |
| 6 RESEARCHER/PUBLISHER | merged PR | issue trail, evidence, lessons; [atlas/README.md](../atlas/README.md#from-module-article-to-atlas-entry) for the intake and the corpus it publishes into |
| 7 MGMT final review | issue | everything above, aggregated |

Pulling the whole tree into context is a graph failure, not thoroughness.

## Compaction and refinement

The graph accretes; without maintenance it drifts. Two mechanisms:

- **Per project**: the cleanup-and-refinement stage
  ([LIFECYCLE.md](LIFECYCLE.md#stages)) removes complexity the project added,
  relocates misplaced artifacts, and repairs vocabulary drift before
  acceptance.
- **Periodic**: the monthly architecture review
  ([TACTICAL.md](TACTICAL.md#monthly---architecture-lifecycle)) runs a graph
  compaction pass - merge duplicated docs, retire dead nodes, tighten links,
  verify the entrance paths from the root README still reach every active
  node. The process itself is iterated here until it is flawless.
