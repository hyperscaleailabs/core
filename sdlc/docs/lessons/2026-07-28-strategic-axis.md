# Lessons from landing the strategic axis

Source: PR #3, which added `AXIS.md`, `AGENTS.md`, `docs/strategic/DIRECTION.md`,
the reindexed strategic packages, and the horizon enforcement. Each lesson states
the correction and where it is now codified.

## L1. Two scanners sharing a regex do not share behavior

`gitleaks` failed on a mailing-list address inside a research citation URL while
`tools/policy/check_pii.sh` passed on the same content. Both tools carry the
*identical* email pattern, so the pattern was not the difference: the address was
URL-encoded (`%40`), and gitleaks decodes its input before matching while a
grep-based check does not.

This mattered beyond one citation. `AGENTS.md` instructs agents to run
`check_pii.sh` before pushing, but `gitleaks` is what gates CI and it catches
strictly more. An agent doing exactly what it was told would still hand over a red
PR, which is the worst shape for a guard to fail in.

**Lesson:** when two tools enforce one policy, compare their *effective* behavior
on adversarial input, not their rule text. Input normalization - decoding,
case-folding, whitespace collapsing - is part of the rule. The documented
pre-push check must be at least as strict as the CI gate, never merely similar.

**Codified:** `email-address-urlencoded` pattern in
[tools/policy/check_pii.sh](../../../tools/policy/check_pii.sh), landed in the same
PR that found it, with a negative test showing it fires on `%40` content.

## L2. Documentation criteria need artifact evidence, not prose

Three acceptance criteria in PR #3 were shaped like "`AXIS.md` states X" and were
checked on the strength of the file existing. `pr-verify` check 2 correctly caught
that the Evidence section named no artifact for them. The criteria were true - the
fix was to cite paths and line anchors, not to uncheck - but "the file is in the
diff" is an assertion until something points at where.

**Lesson:** a documentation criterion is evidenced by artifact path plus a line
anchor or quoted line, the same standard a behavioral criterion meets with a
command transcript. Existence is not evidence of content.

**Codified:** [.claude/skills/pr-verify/SKILL.md](../../../.claude/skills/pr-verify/SKILL.md)
check 2 now names the artifact-plus-anchor form for documentation criteria.

## L3. The flow assumes branch-then-implement

`pr-flow` step 2 creates a worktree from `main` and step 3 implements inside it.
PR #3 arrived with the work already complete and uncommitted in the primary
working tree, because the change grew out of an exploratory review rather than an
agreed unit of work. Creating a worktree from `main` at that point would have
produced an empty branch beside the real changes.

**Lesson:** the worktree step exists to keep `main` clean, and branching in place
serves that purpose equally when the work already exists. The step to never skip
is the Architect framing, not the worktree mechanics.

**Codified:** [.claude/skills/pr-flow/SKILL.md](../../../.claude/skills/pr-flow/SKILL.md)
step 2 now covers adopting pre-existing working-tree changes.

## L4. Mandatory local tooling was absent, and the flow had no fallback

`pre-commit` is documented as mandatory for contributors, and `pr-flow` step 4
requires `pre-commit run --all-files` before pushing. It was not installed. Each
hook was reproduced by hand instead - gitleaks, the staged PII scan, large-file
and merge-conflict checks, end-of-file and trailing whitespace - and the gap was
disclosed in the PR rather than passed over silently.

**Lesson:** a required verification step needs a defined behavior for when its
tool is missing. Silently skipping is a fabricated pass; installing tooling
unasked is a side effect the contributor did not request. Reproducing the hooks
and disclosing which documented check did not run is the honest third option.

**Codified:** [.claude/skills/pr-flow/SKILL.md](../../../.claude/skills/pr-flow/SKILL.md)
step 4 now states the fallback and the disclosure requirement.

## L5. Imported research carries third-party PII

The finding in L1 came from a citation URL in an imported market-research
document. Research imports arrive with hundreds of third-party links, and mailing
lists, profile pages, and archive URLs routinely embed addresses. This is a
recurring class, not a one-off.

**Lesson:** scan imported research with the CI gate, not only the local check, and
expect citation URLs to be the source. Rewriting a citation to its non-address
form preserves the reference without carrying the address.

**Codified:** contextual; L1's pattern is the mechanical guard. Recorded here so
the next research import expects the class.

## L6. Direction is decoration unless something checks it

The 80/15/5 effort weighting would have been a paragraph nobody consults. It
became operative only when a PR had to declare a horizon, the `pr-discipline`
check required the field, and `pr-flow` asked for it while framing work. The
cheapest enforcement point was the PR template, which already carried a
discipline check.

**Lesson:** when adding a policy that shapes what gets built, find the existing
gate it can attach to in the same change. A policy landing without an enforcement
point should be treated as unlanded.

**Codified:** `Horizon:` field in
[.github/PULL_REQUEST_TEMPLATE.md](../../../.github/PULL_REQUEST_TEMPLATE.md), guard
in [.github/workflows/sdlc.yml](../../../.github/workflows/sdlc.yml), standing rule in
[sdlc/LIFECYCLE.md](../../../sdlc/LIFECYCLE.md), framing step in `pr-flow`.
