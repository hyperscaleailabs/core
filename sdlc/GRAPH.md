# The repository graph

The repository is a **graph**, and the root [README.md](../README.md) is its
**entrance node**. Every artifact is reachable from it by following links, and
every artifact links back toward its anchors. Agents do not scan the tree;
they **traverse the graph** and pull only the context the current project
phase requires.

## Nodes and edges

```text
root README.md  (entrance)
  -> AXIS.md / MISSION.md / docs/strategic/   (direction)
  -> sdlc/                                    (method: levels, stages, this file)
  -> executive/                               (CEO / CTO standing validation)
  -> <module>/README.md                       (one per top-level directory)
       -> <module>/ACCEPTANCE.md              (acceptance criteria template)
       -> <module>/docs/                      (module docs, evidence, lessons)
  -> projects: GitHub issues                  (one issue per project)
       <-> PRs (Issue: #N)                    (implementation + review trail)
       -> evidence (SHA-pinned links)
       -> article                             (published to Atlas)
docs/lessons/  (repo-wide lessons; module lessons live in the module)
```

Edges are ordinary markdown links and the `Issue: #N` field on PRs. Both are
guarded: `tools/policy/check_links.sh` (files and anchors) and
`sdlc / pr-discipline` (issue linkage).

## Placement rules

- **Module-specific artifacts live in the module.** Evidence about a module's
  behavior (a training run, a benchmark, a module CI run) goes to
  `<module>/docs/evidence/`; module lessons to `<module>/docs/lessons/`.
- **Repo-level artifacts live at the top.** Evidence about the process or
  spanning modules (policy runs, PR discipline, cross-module integration)
  goes to `docs/evidence/`; process lessons to `docs/lessons/`.
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
| 6 RESEARCHER/PUBLISHER | merged PR | issue trail, evidence, lessons |
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
