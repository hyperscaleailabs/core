# AI Multi-Agent Simulation, Evaluation & Observability

**Project folder:** `ai-multi-agent-simulation-eval-observability`  
**Documentation version:** `v0.1.0`  
**Current stage:** Interactive MVP mock and implementation handoff

## Purpose

This project defines and demonstrates a pre-production control plane for testing non-deterministic AI agents and multi-agent workflows under production-like failure conditions. Operators configure personas, agents, tools, probabilistic failures, validation and recovery harnesses, and release gates; run repeated simulations; inspect telemetry and trajectories; and receive an explainable release decision.

## Start here

1. Download the release ZIP from the `release/` folder.
2. Unzip it locally.
3. Run `make verify` from the extracted package root.
4. Open `app/agent_simulation_control_plane_mvp.html` directly, or run `make serve` and open the local URL printed by the command.
5. Follow the Purchase Ambiguity golden workflow in `docs/03_PRODUCT_MANUAL_TUTORIAL.md`.
6. Read implementation materials in this order:
   - Product requirements
   - Operator UI specification
   - Golden workflow test cases
   - Architecture context
   - Implementation handoff
   - QA verification plan
   - CI/CD and delivery guide

## Golden demonstration workflow

- Run the intentionally unsafe Purchase Agent configuration.
- Observe the blocked decision and duplicate-transaction-risk trajectory.
- Apply the recommended transaction-safety harness using idempotency and transaction-status verification.
- Rerun the same scenario.
- Verify the release result changes to Passed with warnings or Passed, depending on the selected thresholds.

## Scope boundary

The browser MVP uses deterministic mock execution. LLM calls, MCP services, Kafka, Flink, Druid, OpenTelemetry, CI/CD promotion, production distribution learning, and rollback are represented through realistic contracts and integration boundaries but are not yet live production services.

## Folder layout in Drive

- `release/` — packaged implementation handoff ZIP.
- `app/` — standalone runnable HTML MVP.
- `docs/v0.1.0/` — individually accessible product, implementation, QA, and architecture documents.
- Project root — start-here README and handoff guidance.

## Receiving-team acceptance

The implementation lead should confirm that:

- The ZIP extracts and package verification passes.
- The standalone MVP opens and the primary workflow is clickable.
- The product and UI requirements are understood.
- MVP and future-production scope are distinguished.
- Golden workflow tests are incorporated into CI.
- Architecture decisions and unresolved questions have owners.
