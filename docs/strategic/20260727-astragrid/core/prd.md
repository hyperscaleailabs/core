---
document: Product Requirements Document
project: HSAILabs/core
version: 0.1.0
status: Draft
date: 2026-07-27
---

# HSAILabs/core - Product Requirements Document

## 1. Product definition

HSAILabs/core is an open scientific application platform for building,
operating, evaluating, and improving autonomous scientific and physical
systems.

It is not an application and is not tied to a single scientific domain.
Applications such as AstraGrid use selected platform capabilities through
versioned contracts.

## 2. Mission

> Enable practical applications to become reproducible scientific and
> engineering laboratories by providing shared infrastructure for models,
> agents, simulation, evaluation, human supervision, and continuous
> improvement.

## 3. Problem statement

Teams building embodied AI, scientific agents, digital twins, and autonomous
systems repeatedly reconstruct the same infrastructure:

- Dataset and model metadata.
- Simulation adapters.
- Policy execution.
- Distributed rollouts.
- Experiment tracking.
- Fault injection.
- Replay.
- Human approvals.
- Model serving.
- Telemetry.
- Release qualification.

These systems are often tightly coupled to one framework or application,
making results difficult to reproduce and capabilities difficult to reuse.

HSAILabs/core addresses this by defining a stable application platform with
replaceable implementations.

## 4. Target users

### Application builders

Create applications such as AstraGrid without implementing every platform
service.

### ML and scientific engineers

Train, evaluate, and serve PyTorch or JAX models with complete lineage.

### Simulation and robotics engineers

Connect MuJoCo, MJX, Isaac Lab, Gazebo, or custom environments to a common
evaluation lifecycle.

### Agent builders

Compose planners, supervisors, tools, and human approvals without embedding
application logic in the platform.

### Researchers and contributors

Run reproducible experiments, compare approaches, and preserve evidence.

### Platform operators

Deploy locally or on clusters and observe infrastructure, model, and policy
behavior.

## 5. Goals

### G1. Application independence

Applications consume core capabilities through public contracts.

### G2. Reproducible experimentation

Runs can be reconstructed from manifests, versions, seeds, parameters, and
artifacts.

### G3. Framework portability

PyTorch, JAX, Ray, MuJoCo, LiveKit, vLLM, Kafka, and ClickHouse are adapters,
not platform semantics.

### G4. Distributed evaluation

Large episode matrices can be evaluated across workers with retry and
aggregation.

### G5. Human-supervised autonomy

Operators can approve, pause, modify, or abort execution through auditable
events.

### G6. Reliability and governance

Policies and agents are evaluated under faults, compared against baselines,
and promoted through release gates.

### G7. Scientific progression

The platform can evolve toward scientific-agent runtime and autonomous
laboratory orchestration.

## 6. Non-goals for v0.1

- A general-purpose workflow engine.
- A replacement for Kubernetes, Ray, MLflow, or LiveKit.
- A universal robotics middleware.
- A validated safety-certification system.
- A full laboratory information-management system.
- A full digital-twin authoring suite.
- Automatic physical deployment without human review.
- Domain-specific scientific conclusions.

## 7. Product principles

1. **Application-led, platform-decoupled.**
2. **Local reference semantics before scale-out.**
3. **Contracts before frameworks.**
4. **Evidence before claims.**
5. **Safety constraints outside learned policy authority.**
6. **Every run is an inspectable artifact.**
7. **Failures are data.**
8. **Human intervention is part of the system, not an exception.**
9. **Research outputs are versioned alongside code.**
10. **Generalization is earned through repeated application needs.**

## 8. Functional requirements

## FR-1: Application registration

The platform shall load an application manifest containing:

- Application name and version.
- Required and optional capabilities.
- Scenario packages.
- Policy and environment adapters.
- Data and artifact locations.
- Operator surfaces.
- Compatibility constraints.

## FR-2: Environment lifecycle

The platform shall support:

- Reset.
- Step.
- Render.
- Snapshot.
- Restore.
- Parameterization.
- Fault injection.
- Termination.
- Environment metadata.

## FR-3: Policy lifecycle

The platform shall support:

- Policy initialization.
- Reset by episode.
- Action generation.
- Policy metadata.
- Checkpoint references.
- Inference timing.
- Optional confidence and explanation.
- Safety-wrapper composition.

## FR-4: Experiment execution

The platform shall execute:

- One episode locally.
- A matrix of episodes.
- Identical episode manifests across policy versions.
- Partial failure recovery.
- Local or distributed execution.

## FR-5: Artifact management

The platform shall store:

- Trajectories.
- Videos.
- Logs.
- Model and policy metadata.
- Dataset cards.
- Evaluation reports.
- Operator interventions.
- Release decisions.

## FR-6: Evaluation

The platform shall support:

- Application metrics.
- Generic infrastructure metrics.
- Baseline comparison.
- Robustness dimensions.
- Failure categorization.
- Aggregate and per-episode reporting.

## FR-7: Replay

The platform shall permit:

- Timeline inspection.
- Observation and action review.
- Operator intervention review.
- Video synchronization.
- Re-evaluation without rerunning the simulator.

## FR-8: Distributed execution

The platform shall provide a Ray adapter for:

- Episode distribution.
- Resource declarations.
- Worker retries.
- Result aggregation.
- Progress reporting.
- Cancellation.

## FR-9: Model lifecycle

The platform shall support:

- Dataset manifests.
- Model manifests.
- Training-run manifests.
- Checkpoints.
- PyTorch and JAX adapters.
- Policy packaging.
- Serving endpoints.

## FR-10: Serving

The platform shall expose:

- Policy-serving interface.
- Language or multimodal planner interface.
- vLLM adapter.
- Version and health metadata.
- Request and response tracing.

## FR-11: Human supervision

The platform shall represent:

- Proposed action.
- Approval.
- Rejection.
- Modification.
- Pause.
- Resume.
- Abort.
- Escalation.
- Operator identity and timestamp.

## FR-12: Research records

The platform shall publish:

- Architecture decisions.
- Experiment summaries.
- Dataset and model cards.
- Assumption registers.
- Known limitations.
- Next research actions.

## 9. Non-functional requirements

### NFR-1: Reproducibility

A stored experiment manifest must contain enough information to recreate the
execution environment or explicitly state what cannot be reproduced.

### NFR-2: Compatibility

Minor contract versions must remain backward compatible.

### NFR-3: Observability

Every run must expose application, model, simulator, infrastructure, and
operator events.

### NFR-4: Security

Secrets must not appear in artifacts. Operators and agents receive scoped
capabilities.

### NFR-5: Reliability

Completed episode results must not be lost because another worker fails.

### NFR-6: Performance

The local runtime should add minimal overhead relative to direct environment
execution. Distributed overhead must be measured.

### NFR-7: Portability

The reference stack shall run on Linux locally. Cluster profiles may target
Kubernetes and common GPU environments.

### NFR-8: Testability

Contracts, adapters, and release rules require automated tests.

## 10. Core contracts

### ApplicationManifest

Declares what an application is and what it requires.

### DatasetManifest

Records source, license, version, transformation, split, and limitations.

### ModelManifest

Records architecture, framework, weights, precision, inputs, outputs, and
license.

### Environment

Defines state transitions and rendering without exposing simulator-native
objects.

### Policy

Maps standardized observations to standardized actions.

### Trajectory

Records timestamped observations, actions, rewards, events, and terminations.

### ExperimentRecord

Identifies the complete execution context.

### EvaluationResult

Contains metric definitions, values, aggregates, and evidence references.

### FaultEvent

Represents injected or naturally occurring failures.

### OperatorIntervention

Represents human control over execution.

### ReleaseDecision

Documents whether and why a policy or configuration is promoted.

## 11. Initial reference technology choices

| Capability | Initial choice | Status |
|---|---|---|
| Contracts | Python typing/Pydantic + JSON Schema | Required |
| Local runtime | Python synchronous runner | Required |
| Distributed evaluation | Ray | Required after local |
| Model framework | PyTorch | Required |
| Scientific/RL lane | JAX/MJX | Required as adapter |
| Simulation | MuJoCo/MJX | First adapter |
| Planner serving | vLLM-compatible endpoint | Initial adapter |
| Operator interaction | LiveKit Meet | Initial adapter |
| Artifacts | Local filesystem | Reference |
| Telemetry | Structured JSON/events | Reference |
| Production telemetry | Kafka/ClickHouse/Grafana | Planned |
| Cluster deployment | Kubernetes | Planned |

## 12. User journeys

### Application builder

1. Creates an application manifest.
2. Implements environment and policy adapters.
3. Runs a local episode.
4. Registers metrics.
5. Launches distributed evaluation.
6. Publishes a replay and report.

### Researcher

1. Registers a dataset and model.
2. Runs a training or fine-tuning experiment.
3. Packages a policy checkpoint.
4. Compares it against baselines.
5. Reviews failures.
6. Creates a next experiment.

### Operator

1. Opens a Meet room.
2. Reviews a proposed mission.
3. Approves execution.
4. Watches telemetry.
5. Intervenes if necessary.
6. Reviews the final report and replay.

## 13. Acceptance criteria for v0.1

- AstraGrid completes one full episode through public contracts.
- A second minimal application also executes.
- Local and Ray runners produce the same result schema.
- A replay can be opened from a run ID.
- A policy comparison report is generated.
- Operator abort is represented and persisted.
- Core imports no application package.
- Contracts and examples are documented.
- Simulation claims are labeled correctly.

## 14. Future product expansion

- Scientific instrument adapters.
- Experiment-planning agents.
- Automated laboratory queues.
- Multi-robot coordination.
- Hardware-in-the-loop.
- Fleet trajectory ingestion.
- Scientific provenance graphs.
- Energy-aware cluster scheduling.
- Cross-simulator benchmark qualification.
- Physical-world evidence tiers.

## 15. Next proposed action

Approve the v0.1 goals, non-goals, and twelve core contracts. Then implement a
thin end-to-end slice using an in-memory environment before integrating the
AstraGrid MuJoCo scenario.
