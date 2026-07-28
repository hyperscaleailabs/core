# Google Drive Handoff Instructions

## Canonical release

Use the ZIP in the project `release/` folder as the immutable v0.1.0 handoff artifact. The individually uploaded files are provided for convenient reading and review; the ZIP remains the canonical packaged snapshot.

## Source-of-truth order

1. `01_PRODUCT_REQUIREMENTS.md`
2. `02_OPERATOR_UI_SPEC.md`
3. `08_GOLDEN_WORKFLOW_TEST_CASES.md`
4. `07_ARCHITECTURE_CONTEXT.md`
5. `04_IMPLEMENTATION_HANDOFF.md`
6. Runnable HTML MVP for visual and interaction reference

When a visual detail in the HTML differs from the written requirements, follow the written requirements and record the discrepancy.

## Implementation-agent workflow

1. Create a repository and copy the package contents.
2. Preserve domain contracts for Experiment, Run, Iteration, Trajectory, Failure Profile, Harness, Gate, and Release Decision.
3. Implement the Purchase Ambiguity golden workflow first using deterministic services.
4. Make the blocked run and corrected passing run reproducible in CI.
5. Add real model and MCP adapters only after deterministic replay, gate calculations, and telemetry correlations are stable.
6. Require build, lint, typecheck, tests, security scan, screenshots, result JSON, and trace evidence for every milestone.
7. Record architecture choices as ADRs and unresolved issues in the decisions document.

## QA-agent workflow

1. Run package verification.
2. Exercise all four workflow templates.
3. Verify builder validation, run state transitions, provisional and final gate behavior, trajectory inspection, and same-seed replay.
4. Automate golden workflow tests and calculation checks.
5. Verify completed-run configurations are immutable.
6. Confirm that no hidden chain-of-thought is exposed; only operational summaries, events, tool calls, validation, and recovery actions should appear.

## Release and CI/CD guidance

Promotion must remain evidence-based. A candidate may advance only when required gates pass and the build includes reproducibility metadata. Automated rollback should remain recommendation-only until governance, safety, and operational controls are explicitly approved.
