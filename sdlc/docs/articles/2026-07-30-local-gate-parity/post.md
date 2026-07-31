# Post variant (LinkedIn format assumed)

Audience: CTO / Architect / PM. Source of truth:
[article.md](article.md); post text below.

<!-- Paste everything below this line -->

---

We went looking for what was broken in a repository where every CI check was
green. We found a build gate that had never been capable of failing.

The step looked ordinary:

npm run build | tee build.txt

The pipe was there so the job summary could show the build output. But GitHub's
default shell for a workflow step is `bash -e`, and `-e` does not include
`pipefail`. The step's exit status was `tee`'s. A failing build passed the gate,
every time, since the day it was written.

Nothing about a green run tells you which of your checks are real. That is what
makes this class of defect expensive: it degrades silently, and you find out at
the exact moment you needed the check to work.

Two other workflows in the same repository piped into `tee` and both set
`pipefail` correctly. The knowledge was there. It just wasn't uniform, and
nothing checked for uniformity.

The second finding was a rule we had written down ourselves two days earlier: a
check belongs in a script you can run, with the workflow calling it - because
guards that live only in CI get their first execution on a hosted runner, after
the handoff. We had codified that rule in exactly the one module that discovered
it. Thirteen checks in two other modules were still CI-only.

What changed:

- Every gate is now a script, and one command runs all of them.
- Piped steps declare `shell: bash`, which is how you opt into `pipefail`.
- A guard now fails the build on any of the three: a pipe without pipefail, a
  policy check inlined into YAML instead of a script, or a module without a
  `verify` target.

The part worth repeating: we tested every guard in the failing direction, and
one claim did not survive. We had assumed the new scripts needed to exclude
their own source from their own greps - the earlier one did. Testing showed they
don't, because the patterns are escaped regexes that can't match the line
holding them. We kept the exclusion as insurance and wrote it up as
untriggered, with the negative result attached.

"Evidence or it didn't happen" is usually a floor: don't claim what you can't
show. It's also a ceiling. A precaution you copied is not a finding, and the
document whose whole value is that it contains no fabrication is the last place
to round up.
