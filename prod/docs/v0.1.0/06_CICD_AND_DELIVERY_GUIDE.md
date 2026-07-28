# CI/CD and Delivery Guide

## 1. Objective

The delivery system should make implementation evidence reproducible and prevent unsafe application or agent changes from being promoted without verified product, simulation, and release-gate behavior.

## 2. Branch and change model

Recommended:

- Trunk-based development or short-lived branches.
- Protected `main`.
- Required pull-request reviews for domain contracts, gate engine, security policy, and infrastructure.
- Versioned database migrations and API schemas.
- Changes to golden fixtures require explicit review and explanation.

## 3. Pull-request pipeline

Suggested sequence:

1. Repository/package structure validation.
2. Formatting and lint.
3. Typecheck.
4. Unit tests.
5. Domain and API schema compatibility.
6. Deterministic simulation and gate-engine tests.
7. Service integration tests.
8. Frontend component tests.
9. Browser golden workflow tests.
10. Accessibility checks.
11. Dependency, secret, and static security scans.
12. Container build and scan.
13. Build artifact and evidence bundle upload.

Fail fast on formatting, type, schema, or security issues; run browser and container tests after core checks.

## 4. Main-branch pipeline

In addition to PR checks:

- Publish versioned images and frontend artifact.
- Generate SBOM and provenance.
- Deploy to development.
- Run smoke and golden workflows.
- Publish OpenTelemetry and log evidence.
- Update environment status only after tests pass.

## 5. Promotion pipeline

### Development to staging

Require:

- Golden workflow pass.
- Migration dry run.
- Configuration compatibility.
- Security scan pass.
- No critical observability gaps.

### Staging to production

Initially require manual approval and a release evidence packet containing:

- Candidate commit/image digest.
- API/schema versions.
- Test summary.
- Golden workflow comparisons.
- Performance/cost evidence.
- Security results.
- Deployment plan.
- Rollback plan.

The simulation platform's release decision can become one required check, but should not be the sole authorization.

## 6. Deployment strategy

Recommended for the control plane:

- Rolling or blue/green deployment for stateless API/frontend.
- Backward-compatible event and database migrations.
- Worker version pinning per run so an experiment is not split across incompatible runtime versions.
- Canary deployment for model gateway, simulator proxy, and gate-engine changes.

## 7. Rollback

Rollback should distinguish:

- Application code rollback.
- Agent/configuration rollback.
- Database migration recovery.
- Event schema compatibility.
- Release-decision override/revocation.

Automated rollback is a later capability. Initial production behavior should produce a recommendation and require operator confirmation.

## 8. Required pipeline artifacts

- Frontend build.
- Service/container images.
- Image digests.
- SBOM.
- Test/coverage reports.
- Browser traces and screenshots.
- Schema diff.
- Security scan.
- Golden experiment configs and result JSON.
- Deployment manifests.
- Release notes and rollback instructions.

## 9. Environment configuration

Do not embed secrets or environment-specific endpoints in experiment configurations. Use references resolved by the control plane. Keep model price catalogs, tool registries, and policy sets versioned.

## 10. Observability gates for deployment

Before promotion verify:

- Health and readiness probes.
- Structured logs with correlation IDs.
- Trace sampling and propagation.
- Queue lag and failure metrics.
- Worker throughput/error metrics.
- Database migration and storage capacity.
- Alerts for stuck runs, lost telemetry, gate-engine errors, and policy violations.

## 11. Example workflow included in this package

`.github/workflows/package-quality.yml` validates the handoff archive. A production repository should extend it with project-specific lint, typecheck, unit, integration, browser, security, container, and deployment jobs.
