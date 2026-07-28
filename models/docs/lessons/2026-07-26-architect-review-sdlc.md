# Lessons from the architect review of the SDLC PR

> Historical record from before this subproject's integration into the
> monorepo. "SDLC.md", "CLAUDE.md", and PR numbers refer to the standalone
> repository; its methodology is superseded by this repository's
> [sdlc/](../../../sdlc/README.md). The lessons themselves carried forward.

Source: inline review comments on the SDLC methodology PR (PR #2),
2026-07-26. Aggregated per the lessons-learned mechanism; feeds the white
paper of the first project. Each lesson states the correction and where it
is now codified.

## L1. PII is a hard boundary, and tooling leaks it silently

**Comment:** hardcoded personal name in SDLC.md; "never commit any changes
with hardcoded user names, passwords etc."

**Lesson:** PII enters the repo through three channels: hand-written docs
(names), machine-generated artifacts (checkpoints/caches embed
home-directory paths, i.e. usernames), and quoted tool output. A rule alone
is insufficient - the same review caught run artifacts and cache files that
ignore rules on a sibling branch silently failed to cover.

**Codified:** SDLC.md PII policy (roles, never names); CLAUDE.md hard rule;
CI guards for run artifacts/checkpoints and for absolute home-directory
paths; repo made private pending history flatten/reimport.

## L2. The methodology document is a reference, not a journal

**Comment:** "don't put dictation notes here. keep SDLC very clean - that is
methodology reference, not the journal."

**Lesson:** Working notes, terminology mappings from dictation, and
session-specific context belong in PR descriptions and lessons files - the
methodology document must read as if it always existed. Same discipline as
code comments: no narration of how the text came to be.

**Codified:** SDLC.md rewritten clean; journaling lives in `docs/lessons/`
and PR bodies.

## L3. PR sizing: minutes for the model, hours for the project

**Comment:** "all of them must fit into 1-2 hour runway, meaning each PR must
be doable under 10 mins by the coding model."

**Lesson:** The earlier "one hour per PR" sizing was calibrated to human
effort. The correct unit is coding-model execution time: ~10 minutes per PR,
1-2 hours for the whole project runway. This forces radically smaller PRs
(5-10 per project) and makes the dependency graph the real planning artifact.

**Codified:** SDLC.md section 2 sizing rule.

## L4. Cadence: whole-project review every 2-4 hours

**Comment:** "Every 2-4 hours review of the whole Project."

**Lesson:** Per-PR review catches local defects; drift from PRD/ADR is only
visible at project altitude. A standing 2-4 hour whole-project checkpoint
bounds how far execution can wander before correction.

**Codified:** SDLC.md section 3 execution rules.

## L5. Acceptance = working product behind explicit control surfaces

**Comment:** the extended acceptance-criteria comment: intermediate PRs get
automated CI acceptance; the merge PR to main is accepted through five
control surfaces - PRODUCT (live walkthrough env with feedback form that
auto-creates PR-linked tickets), API (swagger-style replay dashboard with
regression stats and drill-down), ARCHITECTURE & CODE (live executable
notebook with before/after diagrams), FULL CI/CD + REGRESSION (automatic
gate with screenshot evidence), WHITEPAPER draft - each closed by an
explicit LGTM comment.

**Lesson:** "Evidence" was underspecified as transcripts in a PR body. The
source of truth for acceptance is the *running product and infra*, linked
from the PR, with structured human intake (feedback forms and dashboards
that create tickets) rather than ad-hoc comments. The intake tooling is
itself pluggable backlog - but the LGTM gates apply from day one, with
manual equivalents (live chat interface to the served model, executed
notebook) until each tool exists.

**Codified:** SDLC.md section 5 (control surfaces table + pluggable-tooling
clause); PR template merge-PR block; applies to every served model variant
(text, Ultravox, whisper) - each needs a live reviewable endpoint, not just
training logs.

## L6. Release is part of the SDLC, not an afterthought

**Comment:** "Merge to main triggers CI/CD deployment branch to Production
pipeline... deploying via SSH to Staging... collecting evidences that
service is still operational. Human approval via Github Actions... then
production."

**Lesson:** The lifecycle does not end at merge. main -> staging (SSH-provisioned
box, operational evidence, human gate via Actions environments) -> production
is the tail of every project and needs the same evidence discipline.

**Codified:** SDLC.md section 6.

## L7. Meta-lesson: review the review loop

Three of the defects the architect caught (committed run artifacts, cache
files with absolute paths, sibling-branch ignore gaps) were mechanical and
guard-able. Every review comment of the mechanical kind should convert into
a CI guard in the same correction PR, so the class of defect - not the
instance - is retired.
