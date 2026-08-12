# Post variant (LinkedIn format assumed)

Audience: CTO / Architect / PM. Source of truth:
[article.md](article.md); post text below.

<!-- Paste everything below this line -->

---

Our contributor guide has said "plain dash, never an em dash" since the first
commit. When we finally counted, the repository held 766 em dashes across 114
files.

Nobody had ignored the rule. It just had no way to be noticed.

The more useful finding was where they came from. Almost none were typed by
someone who'd read the rule and disagreed. They arrived in bulk when we
integrated two existing codebases - content written under a different house
style, moved in wholesale. An integration is the moment your writing conventions
are most likely to break and least likely to be checked, because that week's
review attention is on architecture, licensing, and CI.

So the count wasn't a measure of carelessness. It measured how long an unguarded
rule had been quietly accumulating exceptions.

Three reasons this wasn't a find-and-replace:

- **A line-leading em dash is a list item.** Three of them were wrapped sentence
  continuations. Replace in place and Markdown renders a bullet where there was
  a sentence. The build stays green. Only a reader notices.
- **Sometimes the character is data.** Our shipped MVP uses an em dash as a table
  value meaning "not applicable." And a doc used `license: "—"` as the marker for
  an unknown license - which a blind replace turns into `license: " - "`, a
  string that isn't a value but still parses.
- **Fallback rules leave artifacts.** One template came out with a doubled space.
  HTML collapses it, so nothing looked wrong.

Every automated gate passed on the first run: type checks clean, 50 pages built,
schema valid, 61 tests green. None of it would have caught a stray bullet, a
doubled space, or a placeholder turned into punctuation.

All three real defects were found by reading the rendered output.

For a change whose entire surface is prose, a passing build is the weakest
evidence you have. It proves the page compiles. It doesn't prove it reads.

The guard shipped in the same PR that made the tree clean - deliberately. A guard
added while the tree is still red fails on its author's next unrelated PR, and
the lesson people take from that is to bypass guards.
