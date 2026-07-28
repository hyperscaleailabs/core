# Implementation Package Contents and Handoff Instructions

## 1. Purpose of this package

This archive is intended to be handed directly to implementation agents or an engineering team. It supplies enough product intent, UI behavior, architecture context, fixtures, test cases, and runnable reference behavior to begin structured implementation without reverse-engineering the conversation that produced it.

## 2. Package structure

```text
agent-simulation-control-plane-handoff-v0.1.0/
├── README.md
├── VERSION
├── Makefile
├── NOTICE.md
├── app/
│   └── agent_simulation_control_plane_mvp.html
├── assets/
│   ├── architecture.png
│   └── previews/
│       ├── preview_overview.png
│       ├── preview_wizard.png
│       ├── preview_run.png
│       └── preview_results.png
├── docs/
│   ├── 00_ORIGINAL_MVP_README.md
│   ├── 01_PRODUCT_REQUIREMENTS.md
│   ├── 02_OPERATOR_UI_SPEC.md
│   ├── 03_PRODUCT_MANUAL_TUTORIAL.md
│   ├── 04_IMPLEMENTATION_HANDOFF.md
│   ├── 05_QA_VERIFICATION_PLAN.md
│   ├── 06_CICD_AND_DELIVERY_GUIDE.md
│   ├── 07_ARCHITECTURE_CONTEXT.md
│   ├── 08_GOLDEN_WORKFLOW_TEST_CASES.md
│   └── 09_DECISIONS_AND_OPEN_QUESTIONS.md
├── examples/
│   ├── purchase_ambiguity_experiment.json
│   ├── transaction_safety_harness.json
│   ├── transaction_release_gates.json
│   ├── failed_purchase_trajectory.json
│   └── recovered_purchase_trajectory.json
├── qa/
│   └── acceptance_matrix.md
├── scripts/
│   ├── serve_mock.sh
│   ├── verify_package.py
│   └── extract_inline_js.py
├── .github/workflows/
│   └── package-quality.yml
└── manifest/
    ├── PACKAGE_MANIFEST.json
    └── SHA256SUMS
```

## 3. What each item is for

### Runnable HTML

`app/agent_simulation_control_plane_mvp.html` is the canonical interaction reference. It demonstrates the operator flow with deterministic browser-side data. It is not the target production codebase.

### Product requirements

`docs/01_PRODUCT_REQUIREMENTS.md` defines what the product must do and the honest boundary between MVP and future production-informed capabilities.

### UI specification

`docs/02_OPERATOR_UI_SPEC.md` defines navigation, pages, components, forms, states, state transitions, and interaction behavior.

### Product manual

`docs/03_PRODUCT_MANUAL_TUTORIAL.md` explains users, concepts, metrics, release decisions, and the main operator workflows.

### Golden workflow tests

`docs/08_GOLDEN_WORKFLOW_TEST_CASES.md` turns product behavior into deterministic Given/When/Then scenarios for implementation and QA agents.

### Examples

The JSON files are seed contracts. They should be moved into typed schemas and fixtures in the implementation repository.

### CI/CD guide and workflow

The workflow is deliberately technology-light. It validates this package today and establishes the expected quality-gate sequence for a production repository.

## 4. Source-of-truth hierarchy

1. Product requirements.
2. UI specification.
3. Golden workflow test cases.
4. Architecture context.
5. Implementation guidance.
6. Clickable MVP as interaction/visual reference.

When the HTML and written requirements differ, implementation agents should follow the written requirements and document the discrepancy.

## 5. Recommended implementation sequence

### Milestone 0 — Repository and contracts

Deliver:

- Monorepo or clearly separated frontend/backend repositories.
- Typed domain schemas for Experiment, Run, Iteration, Trajectory, Gate, Harness, Failure Profile, Tool, Agent, and Persona.
- API contract generation and validation.
- Static fixture import from `examples/`.
- CI with lint, typecheck, unit tests, security checks, and artifact build.

Exit criterion: the UI can read canonical fixtures through an application API rather than embedded constants.

### Milestone 1 — Golden workflow in mock-service architecture

Implement the Purchase Ambiguity golden workflow with a real frontend and backend, while keeping model and tool execution deterministic.

Deliver:

- Experiment builder.
- Run API and background execution.
- Deterministic seeded simulation.
- Live event transport using SSE or WebSocket.
- Results and trajectory storage.
- Gate evaluation service.
- Before/after transaction-safety comparison.

Exit criterion: the first blocked run and corrected passing run are reproducible in CI.

### Milestone 2 — Real agent and MCP adapters

Replace deterministic agent execution selectively with a model gateway and MCP-compatible tool adapters. Keep the simulator/proxy available for controlled failure injection.

Exit criterion: one linear and one transactional workflow can execute through real adapters while still being replayable at the dependency layer.

### Milestone 3 — Production-shaped telemetry

Add OpenTelemetry tracing, durable event storage, queue adapter, analytical aggregation, and operator correlations.

Exit criterion: each iteration can be traced end-to-end by experiment/run/iteration/trajectory/trace IDs.

### Milestone 4 — Kubernetes and scale

Deploy API, orchestrator, workers, simulator proxy, storage, and telemetry components to local k3s or development Kubernetes. Add autoscaling and isolation.

Exit criterion: at least 100 concurrent or rapidly batched iterations execute within configured resource and cost bounds.

### Milestone 5 — CI/CD release integration

Expose machine-readable decisions and integrate with deployment checks. Keep promotion and rollback manual until governance and evidence justify automation.

### Milestone 6 — Production evidence learning

Ingest sanitized production trajectories and failure outcomes, version learned distributions, compare them with assumed profiles, and require explicit operator approval before simulation use.

## 6. Recommended repository architecture

```text
/apps/operator-web
/apps/control-api
/apps/simulation-orchestrator
/apps/simulation-worker
/apps/mcp-simulator-proxy
/apps/aggregation-worker
/packages/domain
/packages/api-contracts
/packages/gate-engine
/packages/simulation-kernel
/packages/telemetry
/packages/ui-components
/infra/k8s
/infra/observability
/tests/e2e
/tests/fixtures
/docs
```

A smaller initial repository can combine services, but domain boundaries should remain visible in code.

## 7. Critical contracts to stabilize first

### Experiment configuration
Versioned and immutable after a run. Includes workflow, agents, tools, failure profiles, harness, execution settings, gates, and baseline.

### Iteration event envelope
Must include experiment/run/iteration/trajectory/trace identifiers, event type, timestamp, component, sanitized payload, latency, tokens, cost, failure classification, and recovery action.

### Gate result
Must contain metric definition, scope, actual value, threshold, severity, sample size, result, and related trajectory IDs.

### Release decision
Must contain status, explanations, blocking gates, warnings, version identifiers, and reproducibility metadata.

## 8. Implementation-agent assignments

A coordinated multi-agent implementation can use these roles:

- **Product contract agent:** translates requirements into epics, stories, and acceptance criteria.
- **Architecture agent:** writes the system design, ADRs, API contracts, data model, and sequence diagrams.
- **Frontend agent:** implements application shell, builder, live run, results, and trajectory inspector.
- **Simulation agent:** implements deterministic simulation, failure sampling, seeded replay, and cost/latency calculation.
- **Control-plane agent:** implements registries, versioning, policy, gates, and decisions.
- **Telemetry agent:** implements event schemas, OTel, queue adapters, aggregation, and correlations.
- **QA agent:** implements golden workflow, calculation, state-transition, accessibility, and regression tests.
- **DevOps agent:** implements containerization, Kubernetes, environment promotion, evidence collection, and rollback procedures.
- **Security agent:** reviews tool authorization, redaction, secrets, retention, audit, and multi-tenant boundaries.

Each agent should commit evidence and update the relevant specification or ADR when assumptions change.

## 9. Required implementation evidence

Every pull request or milestone should produce:

- Build artifact.
- Test reports.
- Coverage summary.
- Lint/typecheck result.
- API/schema compatibility result.
- Security/dependency scan.
- Screenshots or video for changed operator flows.
- Golden workflow result JSON.
- Trace/log evidence for one success, one recovery, and one failure.
- Performance and cost-bound result where execution behavior changes.

## 10. Handoff steps for the receiving team

1. Unzip the package.
2. Run `make verify`.
3. Run `make serve` and complete the primary demo.
4. Read the documents in the source-of-truth order.
5. Create an implementation repository and copy `docs/`, `examples/`, `.github/`, and `qa/` into it.
6. Convert product requirements into tracked epics while preserving requirement identifiers or adding them.
7. Create architecture ADRs for orchestration, durable execution, queue, analytical store, model gateway, and identity.
8. Implement the Purchase Ambiguity golden workflow first.
9. Add CI evidence before integrating real models or tools.
10. Record unresolved decisions in `docs/09_DECISIONS_AND_OPEN_QUESTIONS.md` rather than silently assuming them.

## 11. Definition of handoff acceptance

The receiving implementation lead should confirm:

- The HTML MVP runs locally.
- Package verification passes.
- The primary golden workflow is understood.
- MVP versus future scope is understood.
- Source-of-truth order is accepted.
- Initial architecture decisions have owners.
- CI/CD and QA evidence requirements are incorporated into the implementation plan.
