# Promotion and release

The [project lifecycle](LIFECYCLE.md) ends at a squash merge into `main`. This
document covers what happens after: how a merged change reaches operated
production, and which gates it passes on the way. *The lifecycle ends at operated
production, not at merge* - this is that ending, written out.

It is **generic across modules**. Each module instantiates the gates in its own
`ACCEPTANCE.md`; nothing here names a module, a cloud, or an environment. Concrete
endpoints, credentials, and per-host values never live in this repository (see
[notes.md](notes.md)).

Extracted from the practiced delivery system of the [prod](../prod/README.md)
module during its integration; that module's own instance of these gates lives in
[prod/ACCEPTANCE.md](../prod/ACCEPTANCE.md).

## The ladder

| Boundary | Environment | Gate | Who closes it |
|----------|-------------|------|---------------|
| PR -> `main` | none (CI) | Module CI/CD DAG green, evidence bundle complete, Architect LGTM | [Project lifecycle](LIFECYCLE.md#stages) |
| `main` -> staging | staging | Release evidence packet complete; migration dry-run clean; no critical observability gap | Automatic on packet completeness |
| staging -> canary | canary | Operational evidence from staging: the observability gates below hold under real traffic | Human gate |
| canary -> production | production, ramped | Canary metrics within tolerance for the declared soak window | Human gate |

Each boundary is **one-way**: a change that fails a gate returns to the project
lifecycle as a new unit of work, never as an in-place patch to a promoted artifact.

## The release evidence packet

The same bundle at every boundary, growing as it moves. A boundary is not passable
with a missing item; an item that cannot be produced is a gap to fix, not to waive.

| Item | Proves |
|------|--------|
| Commit and image digests | Exactly what is being promoted |
| API and event-schema versions, with the compatibility diff | No silent contract break |
| Test and coverage report | The change is exercised |
| **Module regression result against the accepted baseline** | No regression, per the module's `ACCEPTANCE.md` |
| **The module's own product artifact, run as a check** | The thing being shipped works - see self-gating below |
| Security scan results (dependency, secret, SAST, image) | No known-critical exposure introduced |
| Deployment manifests and the rollback plan | The change can be undone |
| Performance and cost evidence | The change is affordable at the target scale |

Evidence tiers apply ([AXIS.md](../AXIS.md#guardrails)): state the tier on every
record, and never report a simulated result as physical validation.

## Self-gating

**A module's product runs in its own delivery pipeline as a check.** Where a module
produces something that can evaluate a change, that thing evaluates the change
before the change ships.

This is not a metaphor. In `prod` the release-gating simulator runs its golden
workflow on every PR and emits a machine-readable release decision; in `models` the
golden-slice pipeline runs and publishes its transcript. A module with nothing to
run against itself has a gap in its acceptance template, not an exemption.

The self-gate is **one required check, never the sole authorization**. A green
release decision does not by itself promote anything; a red one blocks.

## Deployment strategies

| Change class | Strategy |
|--------------|----------|
| Stateless services | Rolling, or blue/green where the cutover must be atomic |
| Anything a run's correctness depends on | Version-pinned per run, so a single unit of work is never split across incompatible runtimes |
| Learned components, policy engines, gate logic | Canary, always - these are exactly the changes whose effects are not visible in unit tests |
| Schema and data migrations | Backward-compatible, versioned, dry-run before apply |

## Rollback

Rollback is not one action. Distinguish, and plan each separately:

- **Application code** - redeploy the previous digest.
- **Configuration and policy** - revert the config version; the runtime must not
  require a code deploy for this.
- **Data migration** - recovery procedure, tested, distinct from code rollback.
- **Event schema** - compatibility window, so in-flight consumers survive.
- **A published decision** - override and revocation, with the trail preserved.

Automated rollback is a later capability. Until it exists, the pipeline produces a
**recommendation requiring operator confirmation** - which is the deterministic
supervisor pattern from the axis applied to delivery itself.

## Observability gates

Before any promotion, these must hold; each is a gate, not a dashboard:

- Health and readiness probes reflect real dependency state, not process liveness.
- Structured logs carry correlation IDs that join to traces.
- Traces sample and propagate across every service boundary in the path.
- Queue lag, worker throughput, and error rates are visible and within tolerance.
- **Degraded telemetry is loud.** A component that silently falls back to a no-op
  emitter has failed the gate, because every downstream claim built on that
  telemetry becomes unfalsifiable. Fallbacks must be observable in the surface that
  reports readiness.
- Alerts exist for stuck work, lost telemetry, gate-engine errors, and policy
  violations.

The telemetry gate is stated this strongly because it is the one that was learned
the hard way: see
[prod/docs/lessons/2026-07-28-prod-integration.md](../prod/docs/lessons/2026-07-28-prod-integration.md).

## Status

Active for the boundaries CI can enforce today (PR -> `main`, and the evidence
packet). The staging, canary, and production rungs are **written and not yet
exercised** - no environment above local exists in this repository's scope. They
activate with the first deployed environment; until then they are the specification
that environment must satisfy, and the closest manual equivalent is used where the
tooling does not yet exist.
