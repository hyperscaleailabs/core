# Agent instructions for hsailabs core

**[AGENTS.md](AGENTS.md) is the canonical agent contract. Read it first, in full.**
It is vendor-neutral and kept in one place so instructions cannot drift between
harnesses. Nothing Claude-specific overrides it.

Two things it will send you to, before any work starts:

1. **[AXIS.md](AXIS.md)** - direction and effort weighting. Every unit of work
   declares a horizon: short 80%, mid 15%, long 5%. Ambiguous work defaults to
   short.
2. **[sdlc/LIFECYCLE.md](sdlc/LIFECYCLE.md)** - one PR at a time. Use the skills
   `pr-flow`, `pr-verify`, and `lessons`.

Hardest rules, repeated here because the cost of missing them is highest: this
repo is public, so **never commit PII** (`bash tools/policy/check_pii.sh tree`
before pushing); never push directly to `main`; and check an acceptance criterion
only when Evidence proves it.
