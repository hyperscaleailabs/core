---
name: lessons
description: Capture lessons learned after a PR merges or a review round completes - write the lesson file, convert mechanical findings into CI guards, keep methodology docs clean. Use after every merge and every architect review.
---

# Lessons capture

Lessons are the handoff mechanism and the raw material for Atlas white papers.

## Steps

1. **Collect**: review comments from the merged PR, deviations from the agreed
   criteria, anything the next PR must know.
2. **Classify each finding**:
   - **Mechanical** (guardable: PII slip, missing section, artifact committed,
     naming violation) - convert into a CI guard or policy-check pattern in the
     next PR (or the same correction PR), so the class of defect is retired.
     Note the guard in the lesson.
   - **Methodological** (process or sizing correction) - update
     sdlc/LIFECYCLE.md or the relevant skill in the same PR as the lesson.
   - **Contextual** (project knowledge) - record it; no tooling change.
3. **Write the file**: `<module>/docs/lessons/YYYY-MM-DD-<slug>.md` (process lessons: `sdlc/docs/lessons/`), one file per review
   round or merge. For each lesson: the correction (quote the review comment if
   short), the lesson, and where it is now codified. Refer to people by role.
4. **Keep reference docs clean**: lessons files and PR bodies are the journal;
   LIFECYCLE.md and skills must read as if they always existed - no narration
   of how the text came to be.

## Rules

- Convert absolute dates ("today") to ISO dates.
- A lesson without a codification target ("where this now lives") is not done.
- No PII: no names, no home paths, no quoted tool output containing either.
