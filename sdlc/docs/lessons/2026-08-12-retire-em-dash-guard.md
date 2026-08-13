# Lessons: retiring the em dash guard

Source: [PR #28](https://github.com/hyperscaleailabs/core/pull/28), which
removed the em dash rule and `tools/policy/check_writing.py`, recorded as
[ADR 0001](../../../docs/adr/0001-repo-retire-the-em-dash-guard.md).
Role: Implementer, reviewed by the Architect.

## L1. A guard that only exists as workflow YAML is first exercised after the push

**The correction:** PR #28's first push failed `pii-and-secrets` with
`author identity must use a noreply email`. Nothing runnable before pushing
covered it. `check_pii.sh` scans the working tree, not commit metadata, and
`make policy` had no equivalent target, so the rule was undiscoverable until a
hosted runner rejected the commit.

This is lesson L6 of the 2026-07-28 atlas integration arriving a second time, in
a place that had not been swept: that lesson produced `infra/scripts/check-hsai.sh`
for the module gates, and `check_ci_hygiene.py` guards the pattern, but only for
jobs whose id ends `-policy-guards`. The `pii-and-secrets` job does not match
that suffix, so it was exempt from the rule and kept its logic inline. The
exemption was invisible: the guard against inline guards reported ok.

Worth stating plainly, because the first write-up of this finding got it wrong:
the inline block was **not** a violation of `check_policy_jobs_are_scripts`. The
gap was local runnability, not rule compliance. A guard can be fully compliant
and still be discoverable only from CI.

**The lesson:** when a rule is codified as a scoped guard, the scope is itself a
policy decision, and everything outside it silently keeps the old behaviour.
Ask what the guard does *not* cover before treating a class of defect as retired.

**Codified:** `tools/policy/check_commit_identity.sh`, called by the workflow
step and by `make commit-identity`, and included in the `policy` aggregate so
`make policy` catches it before a push.

## L2. Deleting a guard is not a one-file change

**The correction:** `check_writing.py` was linked twice from the lesson that
documented it. Deleting the file would have turned `check_links.sh` red. It did
not, because the links were found by reading the diff before the gate ran, but
the exposure was real and the gate would have caught it either way.

**The lesson:** a guard that has been written up in the SDLC corpus accumulates
inbound references, so removal is noisier than addition. The write-up is what
makes it so. Before deleting anything the corpus documents, grep the corpus for
it.

**Codified:** `tools/policy/check_links.sh`, already in the `policy` aggregate.
No new tooling; the existing guard covers this class.

## L3. Reversing a documented lesson needs a marker, not a deletion

**The correction:** the retained 2026-07-30 lesson argues that a
stated-but-unenforced rule is worthless, and cites 766 em dashes across roughly
114 files as the evidence. That argument is correct. It is also the reason PR #28
removed the rule outright instead of softening it into unenforced guidance,
which would have recreated exactly the condition the lesson describes.

Left alone, the document would read as current policy and the next reader would
reasonably re-add the guard.

**The lesson:** when a decision reverses a recorded one, the record stays and
gains a pointer. Deleting it hides the reasoning; leaving it unmarked
contradicts the new state. Neither is a journal.

**Codified:** [ADR 0001](../../../docs/adr/0001-repo-retire-the-em-dash-guard.md),
plus superseded banners on the 2026-07-30 article, lesson, and evidence.

## L4. A self-exemption is attached to a path, not to a purpose

**The correction:** extracting the commit scan into
`tools/policy/check_commit_identity.sh` made `check_pii.sh` fail on the new
file:

```
POLICY VIOLATION [coauthor-trailer] in tools/policy/check_commit_identity.sh
```

The pattern it flagged is the one the script exists to detect. Detecting a
pattern means naming it. The inline version never tripped this, because
`check_pii.sh` exempts three literal paths, one of which is
`.github/workflows/policy.yml`. Moving code out of an exempted file drops the
exemption with it, silently, and the failure looks like a real violation rather
than a relocation artefact.

**The lesson:** a guard's self-exemption list is coupled to file layout. Any
refactor that moves detection logic across a file boundary has to move the
exemption too. Check the exemption list before moving a guard, not after CI
rejects it.

A second instance surfaced immediately: the evidence file for this change also
tripped the guard, because it quoted the trailer it was documenting.
`check_pii.sh` has no code-fence exemption, unlike the writing guard that PR #28
retired, so patterns must be described rather than reproduced in prose. The
choice is deliberate on the PII guard's part: a fence exemption would be a hole
in exactly the guard that must not have one.

There are **two** exemption lists, not one, and they are independent:
`SELF_PATHS` in `check_pii.sh` and `[allowlist] paths` in `.gitleaks.toml`.
Updating only the first left CI red on the gitleaks job. Both list the same
three enforcement files, which makes it easy to believe fixing one is fixing
the class.

**Codified:** `tools/policy/check_pii.sh`, `SELF_PATHS`, with a comment
recording why the list grows when a guard is extracted. The exemption stays
per-file rather than covering `tools/policy/` wholesale, so a trailer committed
into any other policy script is still caught; proven with a decoy in
[the evidence](../evidence/2026-08-12-commit-identity-guard.md).

## L5. `gitleaks protect --staged` verifies nothing once the work is committed

**The correction:** the local pre-push check reported `no leaks found` while CI
failed the same class on the same file. `protect --staged` scans the staged
diff. Running it after `git commit --amend` leaves nothing staged, so it
scanned an empty set and reported success. Meanwhile CI runs `detect` over
history, which found the file.

**The lesson:** a green check that examined nothing reads exactly like a green
check that examined everything. This is the same failure the new
`check_commit_identity.sh` now refuses to commit, by erroring when its selection
matches no commits, and the guard was written before its author made the
equivalent mistake by hand.

The local equivalent of the CI job is `gitleaks detect --source . --config
.gitleaks.toml`, not `protect --staged`. `pr-flow` step 4 names
`pre-commit run --all-files`, whose gitleaks hook stages correctly; the hand
reproduction is what diverged.

**Codified:** the pre-push parity table in
[the evidence](../evidence/2026-08-12-commit-identity-guard.md) now records
`detect` rather than `protect --staged` as the hand-run equivalent, with the
reason.

## For the next PR

The `policy` aggregate now runs four guards. `check_commit_identity.sh` defaults
to `origin/main..HEAD` locally and takes an explicit range in CI, so a local run
scans the branch and CI scans the pushed commits. If a future job needs commit
scanning, call the script rather than reproducing the patterns.
