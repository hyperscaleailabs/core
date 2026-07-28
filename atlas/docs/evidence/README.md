# Evidence

Committed proof for this module's acceptance criteria. Evidence or it didn't
happen; fabrication is a hard failure. Every record states its **evidence tier**.

This module's own work produces **process** evidence: a build, a validated
corpus, a working intake, and a walked surface. Atlas also *publishes* other
modules' evidence, and a lab note repeats the tier of the claim it summarizes -
it never upgrades one.

| File | What it proves | Collected |
|------|----------------|-----------|
| [2026-07-28-atlas-integration-evidence.md](2026-07-28-atlas-integration-evidence.md) | The integration: build baseline, both guards exercised in the failing direction, and the walked surfaces with their outbound links read from the DOM | 2026-07-28 |
| `2026-07-28-atlas-*.png` | Product screenshots referenced from the record above | 2026-07-28 |

## Generating evidence

```bash
cd atlas
make verify        # index, collection registration, astro check, build
make intake-check  # every module article has a published Lab Notes entry
make preview       # serve dist/ and walk the pages the change touched
```

Screenshots are captured from the local production build with a headless browser
on a throwaway profile: logged out, no browser chrome, no identity in the frame.
Transcripts pass through `sed "s|$PWD|<repo>|g"` before they leave the machine.
Both are surfaces the policy scanner cannot read, so both are handled by hand
and eyeballed before commit.

## Reading a record

A record that says the site "works" without the counts is narration. Each record
carries the page count, the indexed document count, and the check result, so the
next run can reproduce or refute it - and a guard is only recorded as working
once it has been seen to **fail** on a planted defect.
