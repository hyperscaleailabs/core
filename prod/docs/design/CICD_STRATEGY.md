# CI/CD strategy - prod module

**Version:** 0.3.0 · **Extends:** [06_CICD_AND_DELIVERY_GUIDE.md](../v0.1.0/06_CICD_AND_DELIVERY_GUIDE.md)

The delivery system makes implementation evidence reproducible and prevents unsafe
application or agent changes from being promoted without verified product,
simulation, and release-gate behavior.

> **What moved up.** The promotion ladder, the release evidence packet, deployment
> strategies, rollback classes, and the observability gates were not specific to
> this module and now live in [sdlc/PROMOTION.md](../../../sdlc/PROMOTION.md), where
> every module inherits them. This document keeps only what is specific to `prod`:
> its CI/CD DAG and the checks that encode this product's semantics. The module's
> instances of the generic gates are tabulated in
> [ACCEPTANCE.md](../../ACCEPTANCE.md).

The novel property this module contributes: **the product is part of its own CI**.
The golden Purchase Ambiguity workflow runs on every PR and emits a machine-readable
release decision. That is the module's instance of the
[self-gating principle](../../../sdlc/PROMOTION.md).

## Branch and change model

Repository-wide rules (protected `main`, squash merge, module-bounded PRs, PR
template discipline) come from the root [README](../../../README.md) and
[sdlc/LIFECYCLE.md](../../../sdlc/LIFECYCLE.md). On top of those, this module
requires explicit review for:

- `packages/domain` - the four core contracts; a breaking change needs a version bump.
- `packages/gate-engine` - release-decision semantics.
- `deploy/` and `infra/` - anything that changes how the stack is assembled.
- `examples/` - the golden fixtures. A fixture change alters the definition of done,
  so the PR explains it.

## The module CI/CD DAG

One workflow, `.github/workflows/prod.yml`, path-scoped to `prod/**`. Cheap checks
run fail-fast; the rest fan out afterwards.

| Job | What it does | Depth |
|-----|--------------|-------|
| `static-checks` | Ruff format and lint, Python syntax, shell syntax, YAML validity | Always |
| `contracts` | Regenerate JSON schemas from `packages/domain` and diff against the checked-in `schemas/`; fail on an incompatible change without a version bump | Always |
| `unit-tests` | `pytest` across `packages`, `services`, and `stream` with coverage | Always |
| `golden-workflow` | The in-process Purchase Ambiguity e2e; asserts Blocked then Passed, uploads the release decisions and writes them to the run summary | Always - the self-gate |
| `prod-policy-guards` | No hardcoded registries, no committed artifacts or kubeconfigs, no absolute home paths, no real credentials in manifests | Always |
| `terraform-validate` | `terraform fmt -check` and `validate` on `infra/terraform/gcp/`; never `apply` | On `infra/` changes |
| `deployed-evidence` | The stack on an ephemeral k3d cluster, then `deploy/scripts/collect-evidence.sh` | Nightly and manual |

Container image build, SBOM, and provenance run on merge to `main`, not on PRs;
image scanning is part of the release evidence packet in
[sdlc/PROMOTION.md](../../../sdlc/PROMOTION.md).

### Why the deployed job is not on every PR

The full data and observability stack is heavy for hosted runners, and running it
per-PR would trade a large amount of compute for a signal that changes rarely. It
runs nightly, on demand, and locally during development - the local path is
`deploy/scripts/collect-evidence.sh` against a running cluster, which is how the
committed evidence in [../evidence/README.md](../evidence/README.md) is produced.

This is also a known structural limit: a path-filtered workflow cannot be a blanket
required check in branch protection, so until a ruleset scoped to `prod/**` exists,
the module gate is review discipline plus the always-on jobs above.

## Runner strategy

PR, merge, and terraform-validate jobs run on hosted runners. The deployed job runs
k3d inside the runner for the nightly build; heavier deployed tests belong on a
self-hosted runner once a cluster above local exists.
