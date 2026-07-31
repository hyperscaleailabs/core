# The build gate that could not fail

Audience: Architect, PM. Project trail:
[issue #18](https://github.com/hyperscaleailabs/core/issues/18) ->
[PR #19](https://github.com/hyperscaleailabs/core/pull/19).
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../LIFECYCLE.md#stages).

## Goal

The review that started this project found a green tree. Every workflow passed,
every guard was satisfied, the golden release decisions reproduced their
baseline exactly. The question was what remained broken anyway.

Two things did. One was a rule the repository had already written down and
applied to exactly one module. The other was a gate that had never been capable
of failing.

## The gate that could not fail

`atlas.yml` built the site like this:

```yaml
- name: Build the site (validates every article's frontmatter)
  run: npm run build | tee build.txt
```

The pipe is there for a good reason: the job summary publishes the tail of
`build.txt`, so the build output is visible without opening the log. The problem
is what a pipe does to an exit status. GitHub's default shell for a `run:` step
is `bash -e {0}`, and `pipefail` is not part of it. The step's status is the
status of the last command in the pipeline, which is `tee`, which succeeds.

```console
$ bash -e -c 'false | tee out.txt'; echo "step exit=$?"
step exit=0
```

A failing Astro build passed the gate. Every article's frontmatter was, on
paper, validated on every PR; in practice the validation could report anything
at all and the check stayed green.

Nothing distinguishes this from a working check by looking at CI. The runs are
green either way. That is what makes it the most expensive class of defect the
delivery pipeline can carry: it degrades silently, and the moment you find out
is the moment you needed it.

The repository already knew the answer in two other places. `atlas-ingest.yml`
and `models.yml` both pipe into `tee` and both set `set -o pipefail` explicitly.
The knowledge was present and non-uniform, and nothing checked for uniformity.

## The rule that was codified once

Two days earlier, the atlas integration recorded lesson L6: *a check belongs in
a script the author can run, with the workflow calling it.* It was written after
two guards shipped broken, because guards that live only in workflow YAML get
their first execution on a hosted runner, after the handoff, which is the one
place where finding a defect costs the most.

That lesson was codified as `atlas/scripts/check-policy.sh`, and there it
stopped. `models` and `prod` still held thirteen checks - seven policy guards,
four static checks, two inline steps - that existed nowhere else. The rule had
been accepted and applied to the module that discovered it, and nothing carried
it across, because nothing was asked to.

`prod` had drifted a second way on its own. Its `Makefile` documented a pre-push
command that ran `ruff check` over four paths where CI ran it over six, and
skipped the format gate entirely. A contributor following the module README got
a green result from a strictly weaker check than the one that would run against
them. And its `verify` target meant "check the v0.1.0 handoff package" while the
same word in `atlas` meant "everything CI runs" - the same name, two meanings,
and the weaker one silent about it.

## What was built

- **Guards extracted.** `models/scripts/check-policy.sh` and
  `prod/scripts/check-policy.sh` hold the seven module policy guards;
  `models/scripts/check-static.sh`, `prod/scripts/check_yaml.py`, and
  `prod/scripts/check-golden-baseline.sh` hold the rest. Each workflow job is
  now a call to its script.
- **`verify` means one thing.** `models` gained a `Makefile`; `prod`'s was
  repaired target-for-target against its workflow and its old `verify` renamed
  to `verify-package`. A root `Makefile` runs the repository-wide guards and
  delegates to each module, so `make verify` at the top and `make verify` in a
  module both mean "run this scope's gates".
- **The pipefail defect fixed**, by declaring `shell: bash` on the affected
  steps - which is how GitHub opts a step into `-eo pipefail`.
- **The class guarded.** `tools/policy/check_ci_hygiene.py` fails a build when a
  step pipes into `tee` without pipefail, when a `*-policy-guards` job runs an
  inline grep instead of calling a script, or when a module `Makefile` has no
  `verify` target. It runs in the `policy` workflow on every PR.

Thirteen checks were runnable only in CI. Now none are, and one command
reproduces the whole set:

```console
$ make verify
...
all gates OK
$ echo $?
0
```

## What the evidence had to walk back

The obvious claim to write was that self-exclusion in the new guard scripts is
load-bearing - the atlas script excludes its own path precisely because its grep
once matched its own source line, and the new scripts copy that.

Testing it showed the opposite. These patterns are written as escaped regexes:
the source holds `ghcr\.io/`, and the backslash means the line does not match
the pattern it contains. Removing the exclusion changed nothing. The measure is
kept as insurance, and
[the evidence](../../evidence/2026-07-30-local-gate-parity.md) records it as
defensive and untriggered, with the negative result attached.

"Evidence or it didn't happen" is usually read as a floor - do not claim what
you cannot show. It is also a ceiling. A precaution copied from a place where it
was necessary does not become a finding here, and writing it up as one would
have been a small fabrication in a document whose entire value is that it
contains none.

Every other guard was exercised in both directions with planted decoys: seven
policy guards, two static checks, and all three hygiene rules, each reverted in
turn to watch the guard fire. The dashboard credential guard was also exercised
in the passing direction against Superset's export mask, confirming it
distinguishes a masked export from a real credential rather than banning the
field.

## Axis alignment

**Horizon: short**, and [AXIS.md](../../../../AXIS.md) makes the test explicit:
*does this make a seeded run reproducible, evaluable, or replayable?* The golden
release-decision baseline is the repository's reproducibility claim, and until
this project the command that checks it existed only inside a workflow. It is
now `make -C prod golden`, and the same is true of every other gate.

The strategic weighting held. No new capability was added, no mid-horizon
foundation was anticipated, and nothing here is a claim about a physical or
simulated system - the evidence tier is **process** throughout. This is the
unglamorous end of the axis: *grounded, immediate, unglamorous*, and the
guardrail it serves is that **evidence or it didn't happen** requires the
evidence-producing machinery to work in the first place.

The one thing this project deliberately did not do belongs here too. About a
hundred tracked files use an em dash, which
[AGENTS.md](../../../../AGENTS.md) forbids. Almost all arrived with the `atlas`
corpus and the `prod` module at integration. Folding a hundred-file text rewrite
into a delivery-gate change would bury both, and a guard added today would fail
on its first run - which teaches people to bypass guards. It needs a cleanup PR,
with the guard landing in the same PR that makes the tree clean. Recorded in
[the lessons](../../lessons/2026-07-30-local-gate-parity.md#deferred-with-reasons)
rather than left to be rediscovered.

## Lessons

Full text in
[sdlc/docs/lessons/2026-07-30-local-gate-parity.md](../../lessons/2026-07-30-local-gate-parity.md).

1. **A lesson codified in one module is not codified.** Applying it to the
   module that found it is half the work; the other half is asking which modules
   have the same shape.
2. **The default shell sets `-e`, not `pipefail`.** A step that captures output
   with `| tee` must not swallow the status. Where the same construct appears in
   several workflows and only some are correct, the inconsistency is the bug.
3. **Report a defensive measure as defensive.** Test the claim before it becomes
   evidence.
4. **`verify` is a cross-module contract.** A divergent meaning is a defect, not
   a local choice.
5. **Extracting a check is a chance to make it fail better.** The inline
   versions raised a traceback on the first bad file; the extracted ones name
   every offender and continue.
