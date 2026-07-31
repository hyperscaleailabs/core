# 766 em dashes and the rule nobody could see breaking

Audience: Architect, PM. Project trail:
[issue #20](https://github.com/hyperscaleailabs/core/issues/20) ->
[PR #21](https://github.com/hyperscaleailabs/core/pull/21).
Produced by the RESEARCHER/PUBLISHER stage of the
[project lifecycle](../../../LIFECYCLE.md#stages).

## Goal

`AGENTS.md` has said *plain dash, never an em dash* since the repository's first
commits. When someone finally counted, the tree held **766 em dashes across
about 114 files**.

Nobody had ignored the rule. It simply had no way to be noticed.

## Where they came from

Almost none were typed by someone who had read the rule and disagreed. They
arrived in bulk, when the `atlas` corpus and the `prod` module were integrated -
content written under a different house style, moved in wholesale.

That is worth naming as a pattern. An integration is the moment a repository's
writing rules are most likely to be violated and least likely to be checked,
because review attention that week is on structure, licensing, module boundaries,
and CI. Prose conventions are exactly the thing that slips through a review whose
checklist is about architecture.

So the count is not a measure of carelessness. It is a measure of how long an
unguarded rule had been quietly accumulating exceptions.

## Why this was not a find-and-replace

Three hazards, and each one would have shipped silently.

**A line-leading em dash is a list item.** Three occurrences were wrapped
sentence continuations:

```markdown
This is the mechanism behind the entire [agent loop](/foundations/what-is-an-agent)
— the atlas covers its design tradeoffs in depth under [tool use](/patterns/tool-use).
```

Replace that `—` in place and Markdown renders a **bullet** where there was a
sentence. The build stays green, the content schema still validates, and only a
reader notices. The transformer was written to refuse line-leading dashes and
report them instead, which turned a silent rendering bug into three lines of
manual reflow.

**Sometimes the character is data, not punctuation.** The shipped v0.1.0 MVP
uses `'—'` as a table value meaning *not applicable*, rendered to an operator.
And `atlas/docs/content-guide.md` documented `license: "—"` as the marker for an
unknown source license - which a blind replace turned into `license: " - "`, a
string that is not a value at all but still parses.

**A fallback rule leaves artifacts.** One template held `>— {v}<`, which came out
as `> -  {v}` with a doubled space. HTML collapses it, so nothing looked wrong;
the source was just sloppy. Found by diffing added lines for doubled spaces
around a dash, which returned exactly one hit across 660 replacements.

## What was built

- **667 replacements across 104 files**, leaving zero em dashes in scope and zero
  in the rendered site - verified across all 49 built pages, not just the source.
- **Two documented exclusions** for frozen artifacts: the shipped MVP HTML and
  the archived `prod/docs/v0.1.0/` handoff package, whose text is supposed to
  match what shipped.
- **`tools/policy/check_writing.py`**, in the `policy` workflow and `make policy`,
  scanning tracked *and* non-ignored untracked files - so a brand-new document
  fails in the terminal rather than in CI. It carries a second check that fails
  when an excluded path stops existing, because an exclusion pointing at a moved
  path is a rule nobody can see is dead.

`atlas/public/search-index.json` was going to be excluded as generated output. It
turned out to go clean by itself once the corpus did, so the exclusion was
dropped - which makes the guard stronger, since an em dash reappearing there now
means the committed index has drifted from the content.

## What the gates could not tell us

Every gate passed on the first run: `astro check` clean, 50 pages built, corpus
schema valid, 61 tests green, golden release decisions reproducing their
baseline.

None of that would have caught a stray bullet, a doubled space, or a placeholder
turned into `" - "`. A build proves the page compiles. It does not prove it
reads.

All three real defects in this change were found by reading output: two by
inspecting the reflowed sentences on the running site, one by diffing the change
against the artifacts the transformer itself could have introduced. For a change
whose entire surface is prose, the passing build is the weakest evidence
available.

## Axis alignment

**Horizon: short.** [AXIS.md](../../../../AXIS.md) weights short-horizon work at
80% and describes it as *grounded, immediate, unglamorous*. Retiring a
punctuation mark is the far end of unglamorous, and it is the kind of work that
only ever gets done when it is scheduled deliberately.

It serves one guardrail directly: **evidence or it didn't happen**. A repository
whose stated rules and actual contents disagree teaches its readers - human and
agent - that the stated rules are decorative. Every such gap makes the next
stated rule cheaper to ignore. This project closes one gap and, more importantly,
makes it impossible to reopen quietly.

No capability was added, nothing mid-horizon was anticipated, and the evidence
tier is **process** throughout. The strategic weighting held.

The deliberate omission is recorded rather than left to be rediscovered: **103 en
dashes across 36 files remain**, untouched and unguarded. `AGENTS.md` names the
em dash specifically, and most of these are numeric ranges (`5-15 min`) where the
en dash is correct typography. Widening the writing rule is a decision for the
Architect, not something a cleanup PR should decide on its own. If it is widened,
the same ordering applies.

## Lessons

Full text in
[sdlc/docs/lessons/2026-07-30-em-dash.md](../../lessons/2026-07-30-em-dash.md).

1. **A stated rule with no guard is a rule that is drifting.** Measure before
   assuming the cleanup is small; integrations are where writing rules break.
2. **Land the guard in the PR that makes the tree clean.** A guard introduced
   already-red teaches people to bypass guards; a cleanup without a guard decays
   from the moment it merges.
3. **Not every occurrence of a character is an instance of the rule.** Separate
   character-as-punctuation from character-as-data before a bulk rewrite.
4. **A mechanical rewrite must model the format, not just the character** - and
   the cheapest way is to make it decline what it cannot reason about.
5. **Verify a prose change by reading the prose.** The passing build is the
   weakest evidence available.
6. **A rule about prose must distinguish using a character from naming it.** The
   guard's first version made it impossible to document the rule it enforced.

## A postscript the guard wrote itself

The first version of the guard was one grep over whole files. It went green on
the cleaned tree - and then failed on this article, its lesson, its evidence
file, and its Lab Notes entry: eleven violations, every one of them the em dash
being *quoted* inside code to show a reader the hazard.

A guard that forbids a character cannot coexist with the document explaining why
the character is forbidden. Rewritten to mask fenced blocks and inline code spans
while preserving line numbers, it now checks prose rather than bytes - and the
seven decoy cases include a prose dash placed *after* a closed fence, to prove
the masking does not swallow the rest of the file.
