# Acceptance criteria template: prod

Per the [project lifecycle](../sdlc/LIFECYCLE.md#project-shape), every project that
touches this subproject includes these criteria in its acceptance criteria,
instantiated for the specific change. Cross-project work includes the template of
every subproject it touches.

- [ ] **The golden workflow still holds**: the Purchase Ambiguity experiment
      produces **Blocked** under `basic_retry` and **Passed** under
      `transaction_safety`, with the release decision JSON committed as evidence.
      A change that moves this boundary states why, and the new boundary becomes
      the baseline.
- [ ] **A regression test exists for the change**: the affected golden cases
      (GW-01 through GW-15) are covered by re-runnable tests, and the compact
      regression below runs clean against the previous accepted baseline.
- [ ] **The contracts survive**: the four core contracts in `packages/domain`
      (experiment config, iteration event envelope, gate result, release decision)
      are unchanged, or changed with a version bump and the schema diff attached.
- [ ] **The evidence chain is unbroken end to end**: a run started from the
      operator UI produces simulated data that reaches Kafka, is aggregated by
      Flink, lands in ClickHouse, and is readable in **both** Superset and
      Grafana - with the per-hop transcript committed. Every hop is named because
      every hop has, at least once, failed silently while the hop before it looked
      healthy.

## Compact regression (per-PR scale)

Deliberately compact - the golden workflow at a fixed scale, not a load test:

1. Run the in-process golden workflow at 1000 iterations
   (`python tests/e2e/golden_runner.py --iterations 1000 --out artifacts/golden`).
2. Compare both release decisions against the **previous accepted baseline**
   (first: [artifacts/golden/](artifacts/golden/) - `release-decision-unsafe.json`
   Blocked, `release-decision-safe.json` Passed): identical decision, and gate
   metrics within tolerance.
3. Commit the decision JSON and the transcript to
   [docs/evidence/](docs/evidence/README.md).

The workflow is deterministic given a seed, so "within tolerance" means exactly
equal unless the change is intended to move a metric - in which case the change
states the new value and why.

## Deployed verification

Runs on the local k3d cluster when one is reachable; the evidence states which
path was used and on which architecture, because the OLAP store differs
(ClickHouse on arm64, Druid on x86 - ADR-0004 and its update).

```bash
cd prod
bash deploy/scripts/collect-evidence.sh          # per-hop transcript, sanitized
```

The collector is the deployed-evidence gate: it fails if any hop is broken, and it
prints counters before and after a fresh run so the delta - not just the presence
of data - proves the flow. A hop that is merely *reachable* is not a passing hop;
it must show the new run's data.

## Two-tier verification (module CI/CD DAG)

Per the [generic process template](../sdlc/LIFECYCLE.md#stages), change detection
decides depth on every PR and merge:

- **This module modified** -> full extensive verification: static checks, unit
  tests, schema compatibility, the golden workflow with its release decision, the
  **product screenshot** of the operator console, and the deployed evidence chain
  above when a cluster is reachable.
- **Module untouched** -> only the less extensive top-API-level regression that
  runs across all modules on every merge.

## Promotion

Beyond the merge, this module follows [sdlc/PROMOTION.md](../sdlc/PROMOTION.md).
Its instances of the generic gates:

| Generic gate | This module's instance |
|--------------|------------------------|
| Self-gating product artifact | The golden Purchase Ambiguity workflow and its release decision |
| Module regression baseline | `artifacts/golden/*.json` at 1000 iterations |
| Contract compatibility | `scripts/check_schemas.py` against `packages/domain/schemas/` |
| Observability gate | The per-hop evidence collector, including the degraded-telemetry check |
| Canary-always change class | Gate-engine logic, harness semantics, and the MCP simulator proxy |

Evidence tiers apply ([AXIS.md](../AXIS.md#guardrails)): this module produces
**simulation** evidence. A release decision is a statement about a simulated
population under declared failure distributions, never about physical behavior;
state the tier on every record.
