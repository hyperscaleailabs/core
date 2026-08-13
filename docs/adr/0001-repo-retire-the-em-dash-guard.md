# 0001 - repo: retire the em dash rule and its guard

- **Status**: accepted
- **Date**: 2026-08-12
- **Scope**: repo

## Context

`AGENTS.md` carried "Plain dash, never an em dash" from the repository's first
commits. It went unenforced for months, and 766 em dashes accumulated across
roughly 114 files, arriving mostly with the atlas corpus and the prod module.

PR #21 closed that gap the right way: it cleaned the tree and landed
`tools/policy/check_writing.py` in the same change, on the principle that a
guard introduced already-red is a guard people learn to bypass. The guard was
careful work. It masked fenced blocks and inline code so the rule could be
documented without tripping itself, excluded two frozen artifacts with a
recorded reason each, and included a second check asserting those exclusions
still pointed at real paths.

Nothing about the implementation was the problem.

## Decision

Retire the rule and delete the guard.

- Remove the rule from the `AGENTS.md` Writing section.
- Delete `tools/policy/check_writing.py`.
- Remove the `writing` target from the root `Makefile` and drop it from the
  `policy` aggregate.
- Remove the writing step from the `docs-links` job in
  `.github/workflows/policy.yml`.

Em dashes become ordinary punctuation everywhere in this repository.

## Rationale

The guard cost almost nothing to run: stdlib only, no `setup-python` step, and
about 0.09 seconds across the whole tree. Compute was never the argument.

The cost was rework. The rule gates prose, and prose changes in nearly every
PR, so the failure mode is a red pipeline over punctuation followed by a manual
pass to reword. A line-leading em dash cannot be replaced in place either,
because `- ` at the start of a Markdown line is a list item, so some fixes
require reflowing a paragraph. That is a real edit to real sentences in service
of a convention with no functional consequence.

Weighed against that, the benefit is a house style preference. The character
carries no correctness, security, portability, or accessibility meaning. Set
against `check_pii.sh`, `check_links.sh`, and `check_ci_hygiene.py`, each of
which prevents a concrete failure, this guard was the only one enforcing taste.

This decision is a genuine exception to the `AGENTS.md` rule that every
mechanical review finding becomes a CI guard. That rule is sound where the
finding maps to a defect. It is being read here as: guard what breaks, not what
merely differs.

## What is kept

The 2026-07-30 em dash article, lesson, and evidence documents under
`sdlc/docs/` stay exactly where they are, each marked as superseded by this
ADR. They record a real project with real reasoning, and deleting them would
leave the reversal looking like drift.

The lesson in particular argues that a stated-but-unenforced rule is worthless,
and it is right. That is precisely why the rule is being removed rather than
softened into unenforced guidance, which would recreate the 766-violation
condition the lesson describes.

## Alternatives considered

**Keep the rule in `AGENTS.md`, drop only the CI gate.** Rejected. This
reproduces the exact state that PR #21 existed to fix. A rule nobody enforces
is a rule that quietly stops being true.

**Narrow enforcement to the published corpus under `atlas/`.** A defensible
middle: the corpus ships to a public site, and uniform punctuation there has
more claim to mattering than in a Makefile comment. Rejected as still paying
the rework cost on the files most likely to be edited by hand, in exchange for
a benefit no reader has asked for.

## Consequences

- Contributors and agents are no longer blocked on punctuation.
- Punctuation style in prose will drift, including within a single document.
  That is accepted.
- `make policy` now runs three guards instead of four.
- Reinstating this would mean cleaning the tree and landing the guard in one
  change again, per the principle in PR #21. Read this ADR first, and expect to
  argue against the rework cost recorded above.
