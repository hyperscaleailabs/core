# Evidence

Committed proof for this module's acceptance criteria. Evidence or it didn't happen;
fabrication is a hard failure. Every record states its **evidence tier** - everything
here is **simulation** tier, because this module evaluates simulated populations under
declared failure distributions and never observes physical behavior.

| File | What it proves | Collected |
|------|----------------|-----------|
| [UI_EVIDENCE.md](UI_EVIDENCE.md) | Pre-integration record: operator UI, Swagger, the deployed console, and the first end-to-end data and observability flow on local k3s | 2026-07-25 |
| [2026-07-28-prod-integration-evidence.md](2026-07-28-prod-integration-evidence.md) | The integration project's own run: golden workflow, per-hop data plane, Superset and Grafana, and the local CI/CD phases | 2026-07-28 |
| [2026-07-28-running-surfaces.md](2026-07-28-running-surfaces.md) | Every deployed UI, screenshotted, with an explicit split between what serves data and what is not yet wired to what | 2026-07-28 |
| `*.png` | Product screenshots referenced from the records above | various |

## Generating deployed evidence

```bash
cd prod
bash deploy/scripts/collect-evidence.sh
```

The collector proves each hop by the **delta** a fresh run produces, not by the
presence of data, and writes a sanitized transcript to this directory. Host paths are
stripped before anything is written, and screenshots are captured logged out - both
are PII surfaces the policy scanner cannot read.

## Reading a record

A record that says a hop "works" without a before/after counter is not evidence, it
is narration. Each hop line carries the numbers that changed and the query or command
that produced them, so the next run can reproduce or refute it.
