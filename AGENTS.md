# Agent instructions for hsailabs core

Canonical agent contract for this repository, vendor-neutral.
`CLAUDE.md` points here; do not maintain a second copy.

## Read first, in order

1. **[AXIS.md](AXIS.md)** - direction and effort weighting. Every unit of work
   declares a horizon (short 80% / mid 15% / long 5%). Ambiguous work defaults to
   short. Mid-horizon work without its short-horizon foundation is deferred, not
   started.
2. **[sdlc/LIFECYCLE.md](sdlc/LIFECYCLE.md)** - how ALL work here is organized.
   Current mode: one PR at a time. It is the project level of the four-level
   SDLC (strategic / tactical / daily / project, [sdlc/README.md](sdlc/README.md)).

Use the skills: `pr-flow` to run the cycle, `pr-verify` before every handoff,
`lessons` after every merge or review round.

## Where things live

| File or directory | Answers |
|-------------------|---------|
| [AXIS.md](AXIS.md) | Strategic and tactical direction, compressed |
| [MISSION.md](MISSION.md), [docs/strategic/](docs/strategic/) | Why, and the research behind the direction |
| `AGENTS.md` (this file), `CLAUDE.md` | How agents behave |
| [.claude/skills/](.claude/skills/) | What agents can do, as executable procedures |
| [sdlc/](sdlc/) | The four-level SDLC; [LIFECYCLE.md](sdlc/LIFECYCLE.md) is the project level with release gates |
| [sdlc/GRAPH.md](sdlc/GRAPH.md) | The repository graph: how to traverse it and pull per-stage context, placement rules, compaction |
| [executive/](executive/) | Standing CEO and CTO validation agents and repo monitoring |
| [docs/](docs/), subproject `README.md` files | What we are doing: PRDs, ADRs, designs, state |
| [apps/](apps/) | Long-term value stream; evolves with core, aligned to the axis |

## Hard rules

- This repo is public. **Never commit PII**: no personal names, usernames, emails,
  home paths, credentials, or co-author trailers - in files, commit messages, or
  branch names. People are referred to by role (Architect, Implementer).
  Machine-generated artifacts embed usernames in paths; never commit them.
  Run `bash tools/policy/check_pii.sh tree` before pushing.
- Never push directly to `main`; all changes go through a PR with the template
  fully filled (CI enforces it). Squash merge only.
- Check an acceptance criterion only when Evidence proves it. Evidence or it
  didn't happen; fabrication is a hard failure.
- No simulated result is ever reported as physical validation. Evidence tier on
  every record.
- Learned policies and language models propose; deterministic supervisors dispose.
- Nothing deployment-specific, environment-specific, or commercial belongs here;
  that goes to the private companion repo (see [sdlc/notes.md](sdlc/notes.md)).
- Every mechanical review finding becomes a CI guard in the same PR.
- Core never imports app code.

## Writing

- Plain dash, never an em dash.
- No agent name as commit co-author.
- Never hand-edit `CHANGELOG.md` or any file marked auto-generated.
- Prefer quality, simplicity, robustness, and long-term maintainability over
  development cost.
