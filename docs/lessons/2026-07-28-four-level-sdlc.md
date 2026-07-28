# Lessons from landing the four-level SDLC

Source: PR #5, which defined the strategic / tactical / daily / project levels
in `sdlc/`, and its four Architect review rounds. Each lesson states the
correction and where it is now codified.

## L1. Architect feedback can sit in pending reviews

The first review round arrived as a pending (unsubmitted) GitHub review.
`gh pr view --comments` and the flat pull-request comments endpoint returned
nothing; the feedback surfaced only by enumerating the PR's reviews and reading
each review's own comments endpoint. A later "have another look" request came
with no new comments at all - the correct reading was an instruction to
self-review strictly, which found real inconsistencies (stale artifact names,
missing digest wiring).

**Lesson:** when collecting review feedback, enumerate all reviews including
unsubmitted ones, and read comments per review, not only from the flat
endpoints. A review request with no new comments is a self-review instruction,
not a no-op.

**Codified:** contextual; recorded here for the next review cycle.

## L2. Dictated intent needs vocabulary normalization, disclosed

Review rounds arrived as voice-dictated intent carrying transcription
artifacts (mangled names for `main`, Atlas, CTO-level, definition of done) and
vendor product names. Committing them verbatim would have put noise and vendor
references into public methodology docs. The working mapping was normalized to
repository vocabulary, vendor mentions were generalized, and the mapping was
disclosed back to the Architect so a wrong guess could be caught.

**Lesson:** transcription normalization is part of intake for dictated intent.
Map to the repository's vocabulary before committing, keep methodology docs
vendor-neutral, and always disclose the mapping - silent interpretation of
ambiguous terms is how intent drifts.

**Codified:** contextual; recorded here.

## L3. Alignment belongs in outputs, not headers

The first project template restated mission and vision in every project
header. The Architect corrected: reference the strategic and tactical context
in the header, and verify alignment in the outputs instead - the project
article checks that axis alignment held during implementation, the daily
whitepaper evaluates horizon balance and names drift, the weekly digest
aggregates with external market updates.

**Lesson:** repeating direction at every initiation point decays into noise;
checking alignment at every aggregation point produces signal. Push
verification up the output chain rather than boilerplate down the intake
chain.

**Codified:** [sdlc/LIFECYCLE.md](../../sdlc/LIFECYCLE.md#project-shape) project
template and article, [sdlc/DAILY.md](../../sdlc/DAILY.md) whitepaper,
[sdlc/TACTICAL.md](../../sdlc/TACTICAL.md) weekly digest (merged in PR #5).

## L4. Vocabulary and anchor drift across a doc set is mechanical

Renaming a heading in one document silently broke `#anchor` links in another;
the north-star section kept pre-pack artifact names after the pack was
introduced; "daily summaries" and "daily publications" coexisted. All were
caught by manual grep during self-review - which means they will recur when
nobody greps.

**Lesson:** when a term or heading changes at one level of a document set,
sweep the whole set for the old term and for anchors derived from the old
heading in the same commit. Broken relative links and anchors are guardable;
guard them.

**Codified:** [tools/policy/check_links.sh](../../tools/policy/check_links.sh)
verifies every relative markdown link target and GitHub-style heading anchor in
the tree; `docs-links` job in
[.github/workflows/policy.yml](../../.github/workflows/policy.yml); pr-verify
check 4 runs it locally.

## L5. Branch-pinned evidence anchors rot with every push

PR #5's Evidence cited line anchors on the branch head. Every review round
moved the lines, silently pointing the evidence at the wrong content until the
body was manually refreshed - the same shape as L2 of the strategic-axis
lessons: existence is not evidence of content, and an anchor is only evidence
while it points where it did when checked.

**Lesson:** line-anchored evidence links must be pinned to a commit SHA, not a
branch, and re-verified after every review round that touches the files they
cite.

**Codified:** [.claude/skills/pr-verify/SKILL.md](../../.claude/skills/pr-verify/SKILL.md)
check 2 now requires SHA-pinned line anchors and post-review refresh.
