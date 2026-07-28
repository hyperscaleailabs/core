<!-- SDLC PR discipline: all five sections are required; CI verifies them.
     See sdlc/LIFECYCLE.md. Do not delete headings. -->

## Purpose

<!-- Why this PR exists; which discussion or plan item it implements.
     State the horizon this work serves: short / mid / long (see AXIS.md).
     Ambiguous work is short. Every PR belongs to a project and references
     the project's GitHub issue. -->

Horizon: <!-- short | mid | long -->
Issue: <!-- #<number> of the project issue -->

## Tasks

<!-- What was done, as a short list. -->

## Acceptance criteria

<!-- Defined up front with the Architect, before implementation.
     Check a box only when the Evidence section proves it. -->

- [ ] ...

## Evidence

<!-- Proof for each criterion: CI run links, command transcripts, screenshots.
     Committed artifacts go under the touched module's docs/evidence/. Evidence or it didn't happen. -->

## Lessons learned

<!-- What was discovered; what the next PR must know. If a review finding is
     mechanical, add the CI guard in this same PR and note it here.
     Substantial lessons get a file in docs/lessons/. Write "None." if none. -->

<details>
<summary>Merge PRs only: acceptance control surfaces</summary>

<!-- Required only when this PR merges a project (sdlc/<project>) into main.
     Each surface links the specific evidence; the Architect closes each gate
     with the listed comment. Until a surface's tooling exists, link the
     closest manual equivalent (live endpoint, recorded walkthrough,
     executed notebook). -->

| Surface | Link | Gate comment |
|---------|------|--------------|
| PRODUCT | | `LGTM on product` |
| API | | `LGTM on API` |
| ARCHITECTURE & CODE | | `LGTM Architecture` |
| FULL CI/CD + REGRESSION | | automatic |
| WHITE PAPER | | `LGTM on WP` |

</details>
