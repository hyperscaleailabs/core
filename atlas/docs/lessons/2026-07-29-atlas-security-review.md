# Atlas acceptance review: dependency security is a build input

Project: [issue #14](https://github.com/hyperscaleailabs/core/issues/14).
Review round: acceptance review of
[PR #15](https://github.com/hyperscaleailabs/core/pull/15), 2026-07-29.

## Correction

The review installed the exact lockfile and ran a production dependency audit.
It found five high-severity advisories in the shipped dependency graph,
including Astro XSS and SSRF issues and vulnerable Sharp, PostCSS, SVGO, and
XML parsing packages. Every existing CI job was green because none queried the
advisory database.

The correction upgraded Astro from 5.18.2 to 7.1.6 and updated compatible
integrations. Astro 7 required a complete migration from the legacy content
collection API:

- all nine collections now use explicit glob loaders in `src/content.config.ts`;
- route generation and links use entry IDs instead of legacy slugs;
- pages use the standalone content rendering API;
- Node 22.12 is the declared runtime floor in local, CI, and ingestion paths.

The production build still renders 48 pages and indexes 35 documents. Browser
checks of the home page, Lab Notes index, and project article passed at desktop
and mobile widths without console errors, overlays, or horizontal overflow.

## Lesson

A deterministic build proves compatibility with the installed dependency
graph. It does not prove that graph is safe. Dependency advisories are an input
to acceptance and must be checked at the same entrypoints as schema validation,
static generation, and module policy.

Because this is mechanical, a one-time correction is incomplete. The failure
class needs a guard that contributors can run before pushing and that CI cannot
skip.

## Codified

- `make audit` runs `npm audit --omit=dev --audit-level=high`.
- `make verify` depends on `audit`, so the documented local gate includes it.
- The Atlas site and ingestion CI paths run the same audit after `npm ci`.
- The guard was exercised against an isolated Astro 5.6.1 lockfile and exited
  nonzero with two high-severity findings.
- The final secure lockfile reports zero vulnerabilities.

Evidence:
[the acceptance review correction](../evidence/2026-07-28-atlas-integration-evidence.md#acceptance-review-correction-2026-07-29).
