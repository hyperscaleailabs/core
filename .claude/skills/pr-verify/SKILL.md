---
name: pr-verify
description: Verify a PR meets SDLC discipline before handing it to the Architect - template sections, evidence-backed checkboxes, green CI, policy scan. Use before every review handoff and before merging.
---

# PR verification

Run every check below against the PR (default: the current branch's open PR).
Report a pass/fail table in chat; anything failed must be fixed before handoff.

## Checks

1. **Body structure**: `gh pr view --json body` contains all five template
   sections: Purpose, Tasks, Acceptance criteria, Evidence, Lessons learned.
   No placeholder `- [ ] ...` left.
2. **Criteria vs evidence**: every checked `- [x]` criterion has a concrete
   matching item in Evidence (link, transcript, or committed artifact path).
   Checked boxes without evidence are a hard fail: uncheck or add evidence.
   Documentation criteria ("X states Y") are evidenced by artifact path plus a
   line anchor or quoted line - a file appearing in the diff proves existence,
   not content.
3. **CI green**: `gh pr checks` - all checks pass, including required
   `pii-and-secrets` and `pr-discipline`.
4. **Policy scan locally**: `bash tools/policy/check_pii.sh tree` on the branch.
5. **Scope**: `gh pr diff --stat` - the diff matches the stated Tasks; flag
   unrelated changes.
6. **Evidence artifacts**: files referenced under module docs/evidence/ directories exist in the
   diff and contain no PII (they pass check 4 automatically, but eyeball
   screenshots for paths and names - the scanner cannot read images).
7. **Merge PRs only** (sdlc/<project> into main): the control surfaces table is
   filled - every surface has a link (or the documented manual equivalent) and
   the required LGTM gate comments are present on the PR thread.

## Output

Post the table, then one line: `READY FOR ARCHITECT` or `NOT READY: <reasons>`.
