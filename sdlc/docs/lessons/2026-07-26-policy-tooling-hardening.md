# Lessons from standing up the policy tooling

Source: the initial repo setup and the first two merges. Each lesson states
the correction and where it is now codified.

## L1. Gitleaks reports capture group 1 as the secret

A PII rule written as `(/Users|/home)/[A-Za-z0-9._-]+` made gitleaks match
rule allowlists against just `/Users`, silently bypassing the allowlist for
documented placeholder paths.

**Lesson:** in gitleaks rules, use non-capturing groups `(?:...)` unless the
capture is deliberate; always negative-test the allowlist (a file that must
fail and a file that must pass).

**Codified:** .gitleaks.toml pii-home-path-unix rule comment; both test cases
exercised before every policy change.

## L2. Server-side squash merges rewrite authorship

GitHub authors the squash commit as the merging account's profile identity
and appends a noreply co-author trailer whenever branch commits are authored
differently. This first leaked a personal email (fixed by enabling the
account's private-email setting and recreating history), then injected a
trailer that tripped the strict commit-message check.

**Lesson:** commit hygiene on a protected branch is decided by the merge
platform, not by local git config. Align three identities: local repo
`user.name`/`user.email`, the account's noreply identity, and what CI
accepts. Guards must tolerate exactly what the platform injects (noreply
identities) and nothing more.

**Codified:** repo-local git identity set to the account noreply identity;
policy workflow accepts only noreply co-author trailers; CONTRIBUTING.md
commit conventions.

## L3. Structure checks cannot verify truth

The pr-discipline CI job proves a PR body has the required sections and
checkboxes; it cannot prove a checked box is evidence-backed. That judgment
belongs to pr-verify and the Architect review.

**Lesson:** separate cheap structural gates (CI) from judgment gates (review);
name the gap explicitly so it is not assumed covered.

**Codified:** pr-verify skill check 2 (criteria vs evidence cross-check).
