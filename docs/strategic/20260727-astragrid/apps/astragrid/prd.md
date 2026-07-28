---
document: Product Requirements Document
project: AstraGrid
version: 0.1.0
status: Draft
date: 2026-07-27
---

# AstraGrid - Product Requirements Document

## 1. Product definition

AstraGrid is an open scientific application built on HSAILabs/core.

It demonstrates how humans, agents, learned policies, simulation, and
evaluation can collaborate on remote infrastructure maintenance.

Its first application is a simulated lunar rover mission involving power and
thermal infrastructure.

## 2. Mission

> Create a practical application laboratory in which contributors can train,
> evaluate, supervise, and improve autonomous systems while progressively
> developing capabilities relevant to energy, scientific materials automation,
> aerospace, robotics, and space exploration.

## 3. Golden Use Case

A human joins a LiveKit Meet room and gives a rover a mission:

> Inspect Thermal Node B, determine why it is overheating, restore normal
> operation, and return with at least 25% battery.

The system proposes a structured plan, requests approval, executes the mission
in MuJoCo, handles an injected fault, returns or escalates, and produces a
replayable evidence report.

## 4. Durable problem

Critical infrastructure increasingly exists in environments where human
intervention may be:

- Delayed.
- Expensive.
- Dangerous.
- Operationally disruptive.
- Physically unavailable.

AstraGrid explores the infrastructure needed to train and qualify autonomous
systems for inspection, diagnosis, recovery, and resource-aware operation.

The lunar setting is a visible and directional demonstration. The underlying
capabilities are applicable to remote energy assets, industrial facilities,
data centers, scientific sites, aerospace systems, and planetary operations.

## 5. Target participants

### Contributors

Use the project as a practical lab for models, simulation, RL, distributed
evaluation, serving, and human supervision.

### Researchers

Test policies, perturbations, planning methods, and resource tradeoffs.

### Application builders

Learn how an application consumes HSAILabs/core capabilities.

### Reviewers and collaborators

Inspect demos, replays, evidence, and technical decisions.

### Operators

Give missions, approve plans, observe execution, and intervene.

## 6. Goals

### G1. One clear mission

The application must be explainable in one sentence and demonstrable in five
minutes.

### G2. Complete learning lifecycle

The application must connect data or trajectories, training, serving,
simulation, distributed evaluation, replay, and improvement.

### G3. Human supervision

The operator must retain approval and abort authority.

### G4. Reproducible evidence

Results must be reproducible and replayable.

### G5. Broad technical foundation

The project should exercise PyTorch, JAX/MJX, Ray, MuJoCo, vLLM-compatible
serving, RL, and optional preference learning through meaningful roles.

### G6. Directional scientific growth

The application should admit future energy, thermal, materials, scientific
automation, aerospace, and space layers without requiring them in v0.1.

## 7. Non-goals for v0.1

- Real lunar mission planning.
- Validated space thermal physics.
- Flight or space qualification.
- Full VLA foundation-model training.
- Low-level learned motor control.
- Production materials discovery.
- Physical robot deployment.
- Multi-robot coordination.
- Autonomous action without deterministic safety constraints.

## 8. User experience

## 8.1 Join

The operator opens an AstraGrid room in Meet.

Visible:

- Main simulation stream.
- Rover camera.
- Synthetic thermal view.
- Battery reserve.
- Node status.
- Mission timeline.

## 8.2 Request

The operator speaks or types a mission.

## 8.3 Plan

The planner returns a structured plan including:

- Objective.
- Constraints.
- Expected route.
- Inspection steps.
- Recovery options.
- Abort conditions.

## 8.4 Approve

The operator approves, modifies, or rejects the plan.

## 8.5 Execute

The rover performs the mission. Faults may be injected.

## 8.6 Intervene

The operator may pause, abort, or request a review.

## 8.7 Review

The system presents:

- Outcome.
- Remaining energy.
- Diagnosis.
- Recovery result.
- Interventions.
- Safety events.
- Policy comparison.
- Replay.

## 9. Functional requirements

## FR-A1: Mission input

Support text input in v0.1 and voice input when stable.

## FR-A2: Structured planning

Planner output must validate against the mission-plan schema.

## FR-A3: Operator approval

Execution cannot begin without approval unless an explicit development-mode
configuration is enabled.

## FR-A4: Simulated environment

The environment shall include:

- Rover.
- Return base.
- At least three nodes.
- Terrain costs or obstacles.
- Battery state.
- Asset power and thermal state.
- Synthetic visual and thermal observations.

## FR-A5: Mission execution

The rover shall:

- Navigate.
- Inspect.
- Select a bounded recovery action.
- Verify recovery.
- Return or escalate.

## FR-A6: Fault injection

Support at least:

- Dust degradation.
- Sensor noise.
- Increased movement cost.
- Communication delay.
- Incomplete recovery.

## FR-A7: Policies

Support:

- Random baseline.
- Shortest-path baseline.
- Rule-based energy policy.
- RL policy.
- Optional multimodal skill-selection policy.

## FR-A8: Distributed evaluation

Use Ray to run policy, seed, terrain, battery, and fault matrices.

## FR-A9: Model serving

Use a vLLM-compatible service for planning or reporting when supported.

## FR-A10: PyTorch experiment

Train or fine-tune at least one model associated with diagnosis, perception, or
high-level skill selection.

## FR-A11: JAX/MJX experiment

Train and evaluate the navigation or resource policy in vectorized simulation.

## FR-A12: Preference experiment

Optional for v0.1; create chosen/rejected high-level mission plans and test DPO
without granting low-level control.

## FR-A13: Replay

Every mission shall create synchronized events, telemetry, and video references.

## FR-A14: Evidence report

Generate an outcome report grounded in recorded metrics.

## 10. Non-functional requirements

### NFR-A1: Demoability

A complete demonstration should fit within five minutes.

### NFR-A2: Local execution

The baseline mission runs on a development workstation.

### NFR-A3: Determinism

Seeded baseline episodes are repeatable.

### NFR-A4: Safety

Reserve, collision, and abort rules remain deterministic.

### NFR-A5: Transparency

Simulation assumptions and evidence levels are visible.

### NFR-A6: Modularity

AstraGrid uses public core contracts.

### NFR-A7: Degradation

The scripted mission works without vLLM, Ray, or Meet.

### NFR-A8: Measurability

Every learned policy is compared with non-learned baselines.

## 11. Initial data strategy

### Generated trajectories

The primary dataset is generated from the simulated mission.

Records include:

- Observations.
- Actions.
- Mission state.
- Faults.
- Operator interventions.
- Outcomes.

### Open datasets

Potential later adapters:

- Public rover or navigation datasets.
- NASA prognostics data for degradation experiments.
- Materials Project and Matbench for parameter studies.
- Public energy and thermal datasets.

Open data enriches specific experiments but is not required for the first
deterministic mission.

## 12. Metrics

### Mission metrics

- Mission success.
- Diagnosis correctness.
- Recovery effectiveness.
- Safe return.
- Remaining battery.
- Completion time.
- Inspection coverage.

### Reliability metrics

- Fault recovery.
- Abort correctness.
- Replay completeness.
- Worker failure recovery.
- Safety violations.

### Model metrics

- Diagnosis accuracy.
- Skill-selection accuracy.
- Policy reward.
- Generalization.
- Inference latency.
- Robustness.

### Human collaboration metrics

- Approval latency.
- Number of interventions.
- Successful escalations.
- Operator-plan modifications.

## 13. Evidence tiers

Every result shall be labeled:

- `SIMULATION_DEMO`
- `SIMULATION_BENCHMARK`
- `DISTRIBUTED_SIMULATION_BENCHMARK`
- `HARDWARE_IN_THE_LOOP`
- `PHYSICAL_EXPERIMENT`

v0.1 is limited to simulation tiers.

## 14. Dependencies on HSAILabs/core

AstraGrid requires:

- Application manifest.
- Environment and policy contracts.
- Experiment runtime.
- Artifact storage.
- Evaluation.
- Replay.

AstraGrid benefits from:

- Ray runtime.
- Meet operator adapter.
- vLLM serving adapter.
- Model manifests.
- Release gates.
- Atlas publishing workflows.

## 15. Acceptance criteria for v0.1

- The Golden Mission executes end to end.
- At least three policies are compared.
- At least three fault types are evaluated.
- A human can approve and abort.
- A replay is produced.
- A JAX/MJX RL run is documented.
- A PyTorch model run is documented.
- A Ray evaluation suite is documented.
- Planner output is structured and constrained.
- Claims remain within the simulation evidence tier.

## 16. Future expansion

### Energy

- More realistic storage, generation, and thermal models.
- Remote terrestrial microgrid scenario.
- Data-center power and cooling scenario.

### Scientific materials

- Material property profiles.
- Thermal and surface parameter studies.
- Sample-handling and autonomous-lab scenarios.

### Aerospace

- Communication delay.
- Mission windows.
- Onboard inference.
- Fault-tolerant operations.
- Hardware-in-the-loop.

### Robotics

- Physical rover.
- Real-to-sim calibration.
- Multi-sensor fusion.
- Fleet learning.
- Multi-robot missions.

## 17. Next proposed action

Freeze the Golden Mission, environment state, action vocabulary, safety
constraints, and metrics. Then implement the scripted policy as the reference
behavior before introducing learned models.
