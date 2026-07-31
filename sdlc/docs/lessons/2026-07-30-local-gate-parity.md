# Lessons: local gate parity

Source: a repository-wide review of what was broken, on a tree where every CI
check was already green. Role: Implementer, reviewed by the Architect.

## L1. A lesson that is codified in one module is not codified

Lesson L6 of the atlas integration
([atlas/docs/lessons/2026-07-28-atlas-integration.md](../../../atlas/docs/lessons/2026-07-28-atlas-integration.md))
established the rule: *a check belongs in a script the author can run, with the
workflow calling it.* It was written after two guards shipped broken because
their first execution was on a hosted runner. It was then codified as
`atlas/scripts/check-policy.sh` - and only there.

Two days later `models` and `prod` still held thirteen checks that existed
nowhere but workflow YAML. The rule had been recorded, accepted, and applied to
exactly the module that discovered it. Nothing carried it across, because
nothing was asked to.

**Lesson:** codifying a lesson in the module that found it is the first half of
the work. The second half is asking which other modules have the same shape,
and either fixing them or writing down why they differ. A lesson with a
single-module blast radius will not generalize on its own.

**Codified:** [`tools/policy/check_ci_hygiene.py`](../../../tools/policy/check_ci_hygiene.py)
rule 2 fails any `*-policy-guards` job whose steps are not a call to a
`check-policy.sh`. The rule is now enforced for every module that exists and
every module that will.

## L2. The repository's most-used shell sets `-e` but not `pipefail`

`atlas.yml` built the site with `npm run build | tee build.txt`. GitHub's
default `run:` shell is `bash -e {0}`; `pipefail` is not in it. The step
therefore carried `tee`'s exit status, and **a failing Astro build passed the
gate**. The build gate had been decorative since it was written.

Two other piped steps in the tree (`atlas-ingest.yml`, `models.yml`) set
`set -o pipefail` in the body and were correct. So the knowledge existed in the
repository; it just was not uniform, and nothing checked for uniformity.

This is the most valuable kind of finding: not a check that fails, but a check
that cannot fail. Nothing in a green CI run distinguishes the two.

**Lesson:** when a step captures output with `| tee` in order to publish it, the
capture must not swallow the status. Either declare `shell: bash` - which is how
GitHub opts a step into `-eo pipefail` - or set `pipefail` in the body. And when
the same construct appears in several workflows with only some of them correct,
the inconsistency itself is the bug to guard.

**Codified:** [`tools/policy/check_ci_hygiene.py`](../../../tools/policy/check_ci_hygiene.py)
rule 1 fails any step that pipes into `tee` without `shell: bash` or an explicit
`pipefail`. Verified by reverting the fix and watching the guard fire.

## L3. Report a defensive measure as defensive, not as proven

Both new `check-policy.sh` scripts exclude their own path, copying the atlas
script, whose self-exclusion was written after its grep matched its own source
line. The obvious claim to write in the evidence was that self-exclusion is
load-bearing here too.

Testing it showed otherwise. These patterns are escaped regexes - the source
holds `ghcr\.io/`, and the backslash means the line does not match the pattern
it contains. Removing the exclusion changed nothing.

**Lesson:** a measure copied from a place where it was necessary is not thereby
necessary here. Test the claim before writing it into evidence, and when the
measure is worth keeping anyway, record it as insurance rather than as a
verified behaviour. "Evidence or it didn't happen" cuts both ways: it also
forbids upgrading a precaution into a finding.

**Codified:** the evidence file states the exclusion is defensive and untriggered,
with the negative result that shows it. No guard - this is a writing discipline,
and the place it is enforced is review.

## L4. `verify` is a contract, and it has to mean the same thing everywhere

`prod/Makefile` had `verify` meaning "check the v0.1.0 handoff package" while
`atlas/Makefile` had `verify` meaning "everything CI runs". A contributor moving
between modules would read the same word two ways, and the prod reading is the
one that silently does less.

The prod target was also drifting on its own: `make lint` linted four paths
where CI linted six, and skipped the format gate entirely. Someone running the
documented pre-push command got a green result from a strictly weaker check.

**Lesson:** when a target name is a cross-module convention, treat a divergent
meaning as a defect rather than a local choice. Renaming the odd one out
(`verify` -> `verify-package`) costs one line of documentation; leaving it costs
a contributor a false green.

**Codified:** [`tools/policy/check_ci_hygiene.py`](../../../tools/policy/check_ci_hygiene.py)
rule 3 requires every module `Makefile` to define `verify`. The root
[`Makefile`](../../../Makefile) composes them, so `make verify` at the top means
the same thing as `make verify` in any module: run this scope's gates.

## L5. Extracting a check is a chance to make it fail better

The inline YAML versions of the models YAML and golden-schema checks raised an
unhandled Python traceback on the first bad file. The extracted
`check-static.sh` reports `::error file=...` per offending file and keeps going,
so one malformed document no longer hides every other one behind a stack trace.

**Lesson:** the move from YAML to a script is not a pure lift. A check that was
written to be read by whoever wrote it gets read next by whoever broke the
build, and the error message is the whole interface. Improve it while it is
already open.

**Codified:** both extracted scripts collect failures and report per file;
exercised with planted decoys in both directions, recorded in
[the evidence](../evidence/2026-07-30-local-gate-parity.md).

## Deferred, with reasons

- **Em dashes.** [AGENTS.md](../../../AGENTS.md) requires a plain dash. About a
  hundred tracked files contain one, almost all of them inherited with the
  `atlas` corpus and the `prod` module at integration. Folding a hundred-file
  text rewrite into a CI-parity change would bury it, and rewriting published
  article prose deserves its own review. Not guarded here either: a guard added
  today would fail on the first run, and a guard that has to be introduced
  already-red teaches people to bypass guards. It needs a cleanup PR first, then
  the guard in the same PR that makes the tree clean.
- **`ACCEPTANCE.md` coverage.** [sdlc/LIFECYCLE.md](../../LIFECYCLE.md#project-shape)
  says every top-level directory carries one; three of twelve do. The other nine
  are placeholder directories holding a single README, so writing acceptance
  criteria for them now would be documentation ahead of substance. Worth a guard
  once a directory has real content, not before.
- **No project issue template.** LIFECYCLE says the project issue is opened
  "from the project template", and `.github/ISSUE_TEMPLATE/` holds only
  `surface-feedback.md`. Issues have been following a consistent shape by hand.
  Small, separate, and genuinely SDLC-owned.
