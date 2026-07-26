---
name: pr-flow
description: Drive the one-PR-at-a-time SDLC cycle end to end - branch, PRD/ADR discussion, acceptance criteria, worktree, CI, architect review, squash merge. Use when starting any new unit of work in this repo.
---

# One-PR-at-a-time flow

Follow sdlc/LIFECYCLE.md (current mode). One PR in flight at any time; do not start
a second one before the first merges.

## Steps

1. **Frame the work with the Architect.** State in chat: goal, PRD delta (what the
   product should do after this PR), ADR delta (decisions and trade-offs, if any),
   and draft acceptance criteria as concrete checkboxes. Wait for confirmation
   before writing code. Substantial PRD/ADR content goes into the PR body; only
   repo-shaping decisions get an ADR file in docs/adr/.
2. **Create a worktree** so main stays clean:
   `git worktree add ../core-wt/<slug> -b pr/<slug> main`
   Work inside `../core-wt/<slug>`.
3. **Implement.** Keep the diff scoped to the agreed criteria.
4. **Verify locally before pushing**: run `pre-commit run --all-files` and
   `bash tools/policy/check_pii.sh tree`; run any tests the change touches.
5. **Open the PR**: push the branch, then create the PR with a body following
   .github/PULL_REQUEST_TEMPLATE.md - all five sections filled, criteria as
   checkboxes, evidence linked (artifacts committed under docs/evidence/).
6. **Get CI green**: both required checks (`pii-and-secrets`, `pr-discipline`)
   plus any others. Fix and push until green; never hand a red PR to the Architect.
7. **Hand off to the Architect**: post a short review request summarizing which
   criteria are met and where each piece of evidence is. Use the pr-verify skill
   first; fix anything it flags.
8. **On LGTM**: squash merge, confirm the policy run on main is green, remove the
   worktree (`git worktree remove ../core-wt/<slug>`), and capture lessons with the
   lessons skill.

## Rules

- Never push directly to main; never force-push a shared branch.
- Check an acceptance box only when the Evidence section proves it.
- If a review finding is mechanical, add a CI guard for it in the same PR.
