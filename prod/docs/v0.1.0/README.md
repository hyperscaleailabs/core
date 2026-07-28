# Agent Simulation Control Plane — Implementation Handoff Package

**Package version:** 0.1.0  
**Product stage:** Interactive MVP mock + implementation specifications  
**Primary artifact:** `app/agent_simulation_control_plane_mvp.html`

This package is a self-contained handoff for implementation, architecture, design, QA, DevOps, and CI/CD agents. It contains the clickable browser MVP, the product and UI specifications that define expected behavior, operator tutorials, golden workflow test cases, implementation guidance, verification criteria, sample domain data, and reusable package-validation scripts.

## Run the clickable MVP

### Fastest path

Open this file in a modern desktop browser:

```text
app/agent_simulation_control_plane_mvp.html
```

No installation, backend, model API, or internet connection is required.

### Local server

From the package root:

```bash
make serve
```

Then open:

```text
http://localhost:8000/app/agent_simulation_control_plane_mvp.html
```

## Recommended five-minute demo

1. Open **Overview** and select **Open demo**.
2. Run **Purchase Agent Reliability** using the intentionally unsafe retry configuration.
3. Observe live iteration progress, streaming events, provisional gates, worker status, and cost.
4. Open the blocked result and inspect the duplicate-transaction-risk trajectory.
5. Select **Apply recommended fix**, which adds idempotency and transaction-status verification.
6. Rerun the candidate and observe the changed release decision.

## Start here by role

| Role | First document |
|---|---|
| Product or program lead | `docs/01_PRODUCT_REQUIREMENTS.md` |
| Product designer or frontend agent | `docs/02_OPERATOR_UI_SPEC.md` |
| Operator or demo facilitator | `docs/03_PRODUCT_MANUAL_TUTORIAL.md` |
| Backend or platform implementation agent | `docs/04_IMPLEMENTATION_HANDOFF.md` |
| QA or verification agent | `docs/05_QA_VERIFICATION_PLAN.md` |
| DevOps or release agent | `docs/06_CICD_AND_DELIVERY_GUIDE.md` |
| Architect | `docs/07_ARCHITECTURE_CONTEXT.md` |
| Test automation agent | `docs/08_GOLDEN_WORKFLOW_TEST_CASES.md` |
| Technical lead resolving scope | `docs/09_DECISIONS_AND_OPEN_QUESTIONS.md` |

## Source-of-truth order

When documents appear to conflict, use this priority:

1. `docs/01_PRODUCT_REQUIREMENTS.md` — product intent and functional acceptance.
2. `docs/02_OPERATOR_UI_SPEC.md` — operator behavior, page states, and interactions.
3. `docs/08_GOLDEN_WORKFLOW_TEST_CASES.md` — required end-to-end behavior.
4. `docs/04_IMPLEMENTATION_HANDOFF.md` — recommended implementation sequencing and boundaries.
5. The HTML MVP — visual and interaction reference, not a production implementation contract.

## Package verification

Run:

```bash
make verify
```

The verification script checks required files, validates the standalone HTML structure, checks for unexpected external runtime dependencies, confirms the expected product surfaces are present, and verifies example JSON files.

## Important scope statement

The included application is an interactive UI MVP. LLM execution, MCP calls, Kafka/Flink/Druid/OpenTelemetry integrations, production-distribution learning, CI/CD gating, and rollback execution are represented through deterministic browser-side simulation and realistic interface boundaries. Production implementation agents should preserve these boundaries while replacing mock services incrementally.
