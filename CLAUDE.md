# Agent instructions for hsailabs core

Read `sdlc/LIFECYCLE.md` first - it defines how ALL work here is organized.
Current mode: one PR at a time. Use the skills: `pr-flow` to run the cycle,
`pr-verify` before every handoff, `lessons` after every merge or review round.

Hard rules:

- This repo is public. **Never commit PII**: no personal names, usernames,
  emails, home paths, credentials, or co-author trailers - in files, commit
  messages, or branch names. People are referred to by role (Architect,
  Implementer). Machine-generated artifacts embed usernames in paths; never
  commit them. Run `bash tools/policy/check_pii.sh tree` before pushing.
- Never push directly to `main`; all changes go through a PR with the template
  fully filled (CI enforces it). Squash merge only.
- Check an acceptance criterion only when Evidence proves it. Evidence or it
  didn't happen; fabrication is a hard failure.
- Nothing deployment-specific, environment-specific, or commercial belongs
  here; that goes to the private companion repo (see sdlc/notes.md).
- Every mechanical review finding becomes a CI guard in the same PR.
