# Agent Simulation Control Plane — Interactive MVP

A self-contained, clickable operator-console mock for configuring and evaluating production-like multi-agent simulations.

## Start

### Simplest

Double-click `agent_simulation_control_plane_mvp.html` and open it in a modern desktop browser.

### Local web server

From this directory:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/agent_simulation_control_plane_mvp.html`.

No package installation, build step, backend, model API, or internet access is required.

## Recommended demo path

1. Open **Overview** and select **Open demo**.
2. Run **Purchase Agent Reliability** with the intentionally unsafe Basic Retry harness.
3. Watch live iterations, Kafka-shaped telemetry events, provisional release gates, costs, and worker state.
4. Review the blocked result and open the failed trajectory.
5. Select **Apply recommended fix**.
6. Review the Transaction Safety harness, continue to **Review**, and run again.
7. Observe the candidate pass blocking gates with a retry-rate warning.

## Included workflows

- Linear Chat
- Hierarchical Research with depth-one sub-agents
- Department Routing with depth-two delegation
- Transactional MCP with ambiguous completion and recovery

## Included operator surfaces

- Overview dashboard
- Experiment registry and detail
- Eight-step experiment builder
- Persona and assistant-agent configuration
- Tools, resources, skills, and access-policy selection
- Failure and latency distribution configuration
- Validation and recovery harness selection
- Evaluation-gate configuration
- Live run monitor with pause, resume, stop, workers, and streaming events
- Candidate-versus-baseline results and cost projections
- Gate scorecard and anomaly discovery
- Trajectory list and event-level inspector
- Same-seed and new-seed replay interactions
- Workflow, agent, persona, MCP, harness, and gate registries
- Embedded architecture view and production-evidence preview
- JSON export actions

## Implementation note

This is an interactive UI MVP. LLM execution, MCP calls, Kafka/Flink/Druid/OTel integrations, production distribution learning, CI/CD gating, and rollback execution are represented by deterministic browser-side simulation and realistic interface boundaries.
