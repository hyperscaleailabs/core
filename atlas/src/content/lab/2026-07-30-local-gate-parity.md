---
title: "The build gate that could not fail"
description: "A repository where every CI check was green, and a build gate that had never been capable of failing. What a pipe does to an exit status, and why a lesson codified in one module is not codified."
level: "advanced"
updated: 2026-07-30
created: 2026-07-30
tags: [lab-notes, sdlc, ci, process, testing]
module: "sdlc"
project: "local-gate-parity"
articlePath: "sdlc/docs/articles/2026-07-30-local-gate-parity/article.md"
issue: 18
pr: 19
evidenceTier: "process"
draft: false
aiGenerated: false
license: "CC-BY-4.0"
sources:
  - title: "The build gate that could not fail (module article)"
    url: "https://github.com/hyperscaleailabs/core/blob/main/sdlc/docs/articles/2026-07-30-local-gate-parity/article.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
  - title: "Lessons from the local gate parity project"
    url: "https://github.com/hyperscaleailabs/core/blob/main/sdlc/docs/lessons/2026-07-30-local-gate-parity.md"
    publisher: "hsailabs"
    license: "Apache-2.0"
  - title: "Defaults for the run keyword (GitHub Actions workflow syntax)"
    url: "https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_iddefaultsrun"
    publisher: "GitHub"
---

> Field notes from the `sdlc` module. Full article, evidence, and review trail in
> [the module article](https://github.com/hyperscaleailabs/core/blob/main/sdlc/docs/articles/2026-07-30-local-gate-parity/article.md).

We went looking for what was broken in a repository where every CI check was
green. We found a build gate that had never been capable of failing.

## The gate that could not fail

The step looked ordinary, and the pipe was there for a good reason - the job
summary publishes the tail of the build log, so failures are visible without
opening the run:

```yaml
- name: Build the site (validates every article's frontmatter)
  run: npm run build | tee build.txt
```

The problem is what a pipe does to an exit status. GitHub's default shell for a
`run:` step is `bash -e {0}`, and `pipefail` is not part of it. The step's
status is the last command's, which is `tee`, which succeeds:

```console
$ bash -e -c 'false | tee out.txt'; echo "step exit=$?"
step exit=0
```

Every article's frontmatter was, on paper, validated on every pull request. In
practice the validation could report anything and the check stayed green.

Nothing distinguishes this from a working check by looking at CI. The runs are
green either way. That is what makes it the most expensive class of defect a
delivery pipeline can carry: it degrades silently, and the moment you find out
is the moment you needed it.

Two other workflows in the same repository piped into `tee` and both set
`set -o pipefail` explicitly. The knowledge was present and non-uniform, and
nothing checked for uniformity. The fix is one line - `shell: bash`, which is
how GitHub opts a step into `-eo pipefail` - and the durable part is the guard
that now fails any piped step lacking it.

## The rule that was codified once

Two days earlier we had recorded a lesson: a check belongs in a script the
author can run, with the workflow calling it. It was written after two guards
shipped broken, because guards that live only in workflow YAML get their first
execution on a hosted runner, after the handoff - the one place where finding a
defect costs the most.

We codified that lesson in exactly the module that discovered it. Two other
modules still held thirteen checks that existed nowhere but workflow YAML.

That is the more general finding. Applying a lesson to the module that found it
is half the work. The other half is asking which modules have the same shape,
and either fixing them or writing down why they differ. A lesson with a
single-module blast radius does not generalize on its own, and the interval
between recording it and noticing that was two days.

## What changed

- Every gate is a script the author can run; one command reproduces the whole
  set, and each module's `verify` is its CI job list in CI's order.
- Piped steps declare `shell: bash`.
- A guard fails the build on any of three shapes: a pipe into `tee` without
  pipefail, a policy check inlined into YAML instead of calling a script, or a
  module without a `verify` target.

Thirteen checks were runnable only in CI. Now none are.

## The claim that did not survive testing

We assumed the new guard scripts needed to exclude their own source from their
own greps - the earlier one did, after its pattern matched its own source line.

Testing showed they don't. These patterns are escaped regexes: the source holds
`ghcr\.io/`, and the backslash means the line does not match the pattern it
contains. Removing the exclusion changed nothing. We kept it as insurance and
wrote it up as untriggered, with the negative result attached.

"Evidence or it didn't happen" is usually read as a floor - do not claim what
you cannot show. It is also a ceiling. A precaution copied from a place where it
was necessary does not become a finding here, and the document whose entire
value is that it contains no fabrication is the last place to round up.
