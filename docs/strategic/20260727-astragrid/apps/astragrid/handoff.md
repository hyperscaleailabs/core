---
document: Handoff
project: AstraGrid
version: 0.1.0
status: Draft implementation handoff
date: 2026-07-27
---

# AstraGrid - Implementation Handoff

## 1. Application definition

AstraGrid is the first flagship application built on HSAILabs/core.

Its Golden Use Case is:

> Through a LiveKit Meet room, a human directs a simulated rover to inspect and
> restore a degraded lunar power or thermal node, verify recovery, and return
> while preserving a safe energy reserve.

The lunar setting provides a clear and memorable application. The underlying
problem is broadly relevant:

> Autonomous maintenance of critical energy and thermal infrastructure where
> human intervention is delayed, expensive, dangerous, or unavailable.

## 2. Role within HSAILabs

AstraGrid is:

- A demonstrable application.
- A source of concrete platform requirements.
- A benchmark environment.
- A learning and collaboration surface.
- A path toward energy, robotics, scientific automation, aerospace, and space
  operations.

AstraGrid is not:

- The HSAILabs platform itself.
- A claim of validated lunar autonomy.
- A high-fidelity space thermal simulator.
- A materials-discovery system in its first release.
- A replacement for robotics or aerospace certification.

## 3. Initial mission

Mission name:

**Restore Thermal Node B**

Operator command:

> Inspect Thermal Node B, determine why it is overheating, restore normal
> operation, and return with at least 25% battery.

The rover must:

1. Parse the voice mission.
2. Produce a structured plan.
3. Request approval.
4. Navigate to the asset.
5. Inspect RGB, synthetic thermal, and telemetry observations.
6. Select a bounded recovery action.
7. Verify whether conditions improve.
8. Replan or request help if needed.
9. Return before violating the reserve.
10. Publish a report and replay.

## 4. Initial environment

Use:

- MuJoCo for reference physics and rendering.
- MJX for vectorized JAX rollouts.
- A simple differential-drive rover.
- A compact lunar-styled surface.
- Three power/thermal nodes.
- A charging or return base.
- Obstacles and terrain-cost zones.
- Battery and movement-cost model.
- Synthetic asset temperature and power telemetry.

Initial failures:

- Dust-degraded node.
- Noisy thermal sensor.
- Increased rover energy use.
- Communication delay or dropout.
- Recovery action with incomplete effect.

## 5. Initial action vocabulary

```text
NAVIGATE_TO
INSPECT_ASSET
ACTIVATE_DUST_MITIGATION
RESET_THERMAL_CONTROLLER
WAIT_AND_RECHECK
RETURN_TO_BASE
REQUEST_HUMAN_REVIEW
ABORT_MISSION
```

Low-level motor safety remains deterministic.

## 6. Initial model lanes

### Lane A: Planner and explanation

- LLM or multimodal model served through a vLLM-compatible endpoint.
- Produces structured mission plans.
- Produces evidence-grounded summaries.
- Cannot directly command unsafe low-level actions.

### Lane B: Rover navigation and resource policy

- JAX/MJX RL environment.
- PPO or another established baseline.
- Optimizes mission completion and safe energy return.
- Compared with random, shortest-path, and rule-based policies.

### Lane C: PyTorch perception or skill selection

One small, measurable model:

- Thermal anomaly classification.
- Visual node-condition classification.
- High-level action selection.
- Optional LoRA fine-tuning of a compact multimodal model.

### Lane D: Preference alignment

- DPO or preference optimization over high-level mission plans.
- Preferences prioritize safety, successful return, correct recovery, energy
  preservation, and then speed.
- Not used for low-level control.

## 7. Core capabilities consumed

Required:

```text
models.policy-training
models.policy-serving
dtwins.environment
prod.experiment-runtime
prod.evaluation
prod.replay
infra.local-runtime
```

Optional for the first release:

```text
infra.ray-runtime
meet.operator-room
agents.mission-planner
prod.telemetry-streaming
models.preference-training
dtwins.domain-randomization
```

AstraGrid must not implement a duplicate general experiment runtime.

## 8. First six-week deliverable

A five-minute interactive demonstration:

1. Operator enters Meet.
2. Simulation stream and telemetry appear.
3. Operator gives the Golden Mission.
4. Planner returns a structured plan.
5. Operator approves.
6. Rover performs the mission.
7. One fault is injected.
8. Rover recovers or requests assistance.
9. Rover returns.
10. Dashboard displays success, reserve, interventions, and policy comparison.
11. Replay and evidence-grounded summary are available.

## 9. First two-week implementation packages

### WP-ASTRA-01: Scenario package

Create:

- Mission manifest.
- Asset definitions.
- Action vocabulary.
- Reward and safety constraints.
- Failure profiles.
- Acceptance tests.

### WP-ASTRA-02: MuJoCo environment

Create:

- Rover model.
- Lunar-styled terrain.
- Three nodes.
- Battery model.
- RGB and synthetic thermal rendering.
- Reset, step, render, snapshot, and fault injection.

### WP-ASTRA-03: Rule-based baseline

Create:

- Deterministic mission script.
- Shortest-path route.
- Reserve calculation.
- Recovery verification.
- Return-to-base behavior.

### WP-ASTRA-04: Core integration

Connect:

- Application manifest.
- Environment adapter.
- Policy adapter.
- Experiment record.
- Evaluation metrics.
- Replay artifacts.

### WP-ASTRA-05: Meet display

Initially:

- Simulation video.
- Mission text input.
- Approve.
- Pause.
- Abort.
- Telemetry status.

Voice may be enabled after text behavior is stable.

### WP-ASTRA-06: First RL benchmark

- MJX vectorized environment.
- Random and rule-based baselines.
- PPO training.
- Multi-seed evaluation.
- Safe-action wrapper.

## 10. Acceptance criteria

### Baseline mission

- Reaches the intended node.
- Executes inspection.
- Applies the correct scripted mitigation.
- Verifies improvement.
- Returns with reported reserve.
- Produces a replay.

### Learned policy

- Evaluated on identical seeds as baselines.
- Exceeds random-policy performance.
- Does not bypass reserve or collision constraints.
- Records training and checkpoint metadata.

### Meet

- Operator can start and abort.
- Operator events appear in replay.
- Simulation remains usable without Meet.

### Claims

- Simulation assumptions are documented.
- No result is described as physical validation.
- Materials data, when introduced, is described as parameterization or
  hypothesis support.

## 11. Required outputs from the receiving team

- Runnable local scenario.
- Application manifest.
- Scenario and task definitions.
- Environment adapter.
- Baseline policies.
- Metrics.
- Videos and trajectories.
- Installation guide.
- Architecture decisions.
- Benchmark report.
- Known limitations.
- Next experiment proposal.

## 12. Next proposed action

Implement the deterministic `Restore Thermal Node B` mission through the
HSAILabs/core local runtime. Do not start model training until the complete
scripted mission, telemetry, evaluation, and replay path works.
