---
document: Handoff
project: HSAILabs/core
version: 0.1.0
status: Draft implementation handoff
date: 2026-07-27
---

# HSAILabs/core - Implementation Handoff

## 1. Purpose

This document transfers the initial HSAILabs/core platform definition to an
implementation team or coding-agent harness.

HSAILabs/core is an open scientific application platform. It supports practical
applications that progressively develop capabilities in multimodal agents,
distributed ML, robot learning, digital twins, scientific automation, energy
systems, aerospace, and space exploration.

The platform is driven by applications but remains independent from any one
application. AstraGrid is the first flagship consumer and proving ground.

## 2. Mission

> Build reusable infrastructure for training, serving, simulating, evaluating,
> supervising, and improving autonomous scientific and physical systems.

The platform should make it possible for contributors to begin with practical
experiments, preserve what is learned, compare results, and progressively apply
the accumulated capabilities to more difficult scientific and physical-world
problems.

## 3. Existing project topology

```text
hsailabs-core/
├── apps/      # Independent applications, including AstraGrid
├── sdlc/      # Agentic engineering and release workflows
├── models/    # Training, benchmarking, optimization, and serving
├── prod/      # Evaluation, replay, observability, and data plane
├── meet/      # LiveKit-based collaboration and operator interaction
├── agents/    # Agent APIs and LiveKit agent services
├── dtwins/    # Simulation and digital-twin abstractions
├── atlas/     # Research synthesis and knowledge artifacts
└── infra/     # Local, cluster, cloud, and accelerator deployment
```

## 4. Platform/application relationship

AstraGrid depends on core contracts. Core does not depend on AstraGrid.

```text
AstraGrid requirements
        ↓
core contract proposal
        ↓
contract review and versioning
        ↓
generic implementation
        ↓
AstraGrid integration
        ↓
evaluation and lessons learned
        ↓
contract refinement
```

A capability should move into core when at least one of these conditions holds:

- It is reusable by more than one application.
- It represents a durable systems boundary.
- It is needed for reproducibility, reliability, security, or governance.
- It is required to compare models, environments, or policies consistently.
- It is infrastructure rather than domain-specific behavior.

A capability should remain in the application when it contains:

- Domain-specific reward definitions.
- Mission vocabulary.
- Scenario assets.
- Application-specific prompts.
- Domain assumptions.
- Product-specific UI composition.
- Domain-specific benchmark acceptance thresholds.

## 5. Initial deliverable

The first platform increment is **Core Contract Pack v0.1**.

It must include:

1. `ApplicationManifest`
2. `DatasetManifest`
3. `ModelManifest`
4. `Policy`
5. `Environment`
6. `Trajectory`
7. `ExperimentRecord`
8. `EvaluationResult`
9. `FaultEvent`
10. `OperatorIntervention`
11. `ArtifactReference`
12. `ReleaseDecision`

Reference implementations may initially be Python protocols plus JSON Schema or
Pydantic models.

## 6. Required first vertical slice

A minimal AstraGrid run must be possible through core interfaces:

```text
application manifest
    → environment reset
    → policy reset
    → repeated observation/action steps
    → optional fault injection
    → operator intervention
    → trajectory persistence
    → evaluation
    → replay
    → release decision
```

The first implementation does not require all production systems. A local
SQLite or file-backed artifact store is acceptable if the contracts allow later
Kafka, ClickHouse, object-storage, and Ray implementations.

## 7. Implementation principles

### 7.1 Local-first

Every capability must have a local development mode. A contributor with one
machine and one GPU should be able to run a complete experiment.

### 7.2 Scale-out without semantic changes

Ray, Kubernetes, Kafka, ClickHouse, and object storage may change execution and
capacity, but they must not change the meaning of an experiment.

### 7.3 Contract-first

Schemas and interfaces are reviewed before adapters. Avoid leaking MuJoCo,
Ray, PyTorch, JAX, LiveKit, or vLLM objects across public core boundaries.

### 7.4 Evidence before claims

All reports distinguish:

- Simulated result.
- Benchmark result.
- Hardware-in-the-loop result.
- Physical result.
- Inference or projection.

### 7.5 Deterministic safety ownership

Language models and learned policies may propose actions. Deterministic safety
rules can reject, modify, pause, or terminate them.

### 7.6 Reproducibility

Every run records:

- Application and scenario version.
- Dataset and model versions.
- Policy checkpoint.
- Simulator and adapter versions.
- Random seed.
- Environment parameters.
- Infrastructure profile.
- Operator interventions.
- Metrics and outcome.
- Produced artifacts.

## 8. First implementation work packages

### WP-CORE-01: Contracts

Create the versioned Python and JSON contracts.

Acceptance:

- Schema validation tests pass.
- Backward-incompatible changes require a new contract version.
- Example AstraGrid records validate.

### WP-CORE-02: Local experiment runtime

Create a synchronous experiment runner.

Acceptance:

- One environment and one policy can complete a seeded episode.
- The runner records actions, observations, timing, and outcome.
- A failed run preserves partial evidence.

### WP-CORE-03: Artifact and replay store

Create a local file-backed store with stable artifact identifiers.

Acceptance:

- Videos, trajectories, model metadata, and reports can be retrieved by run ID.
- Replay does not require retraining.
- The store can later be replaced by object storage.

### WP-CORE-04: Evaluation interface

Create metric and evaluator plugins.

Acceptance:

- Evaluations can be recomputed from stored trajectories.
- Multiple policies can be compared over identical episode manifests.
- Infrastructure failures are separated from policy failures.

### WP-CORE-05: Application capability resolution

Read an application manifest and resolve available providers.

Acceptance:

- Missing required capabilities fail early.
- Missing optional capabilities degrade explicitly.
- The application can choose local or distributed execution profiles.

### WP-CORE-06: Ray adapter

Add distributed evaluation after the local runner is stable.

Acceptance:

- The same episode manifest produces semantically equivalent local and Ray runs.
- Worker retries do not duplicate completed results.
- Run IDs remain stable.

### WP-CORE-07: Meet operator adapter

Expose generic start, approve, pause, abort, and intervention events.

Acceptance:

- The adapter does not know AstraGrid mission vocabulary.
- Operator actions appear in the experiment record.
- Application-specific UI remains under `apps/`.

## 9. Definition of done for v0.1

Core v0.1 is complete when:

- AstraGrid can run one scenario through public core interfaces.
- Core tests contain no import from `apps/astragrid`.
- A local episode can be evaluated and replayed.
- A Ray-backed evaluation produces the same metric schema.
- An operator intervention is recorded.
- Contracts and examples are documented.
- A second sample application can implement a trivial environment without
  modifying the contracts.

The second sample may be deliberately small, such as a grid-world inspection
task. Its purpose is to test generality, not create another flagship.

## 10. Risks

### Risk: premature platform abstraction

Mitigation: only generalize requirements demonstrated by AstraGrid or the
minimal second application.

### Risk: framework leakage

Mitigation: adapters translate framework-native objects into core contracts.

### Risk: distributed complexity before value

Mitigation: local synchronous execution is the reference semantics.

### Risk: unclear ownership between projects

Mitigation: maintain an ownership table and architecture decision records.

### Risk: application-specific logic entering core

Mitigation: enforce import and dependency tests in CI.

## 11. Required outputs for the receiving team

The implementation team should return:

- Contract source and generated schemas.
- Example manifests.
- Unit and compatibility tests.
- Local runner.
- File-backed artifact store.
- Evaluation and replay CLI.
- AstraGrid adapter integration.
- One architecture decision record per major boundary.
- A status report listing accepted, deferred, and rejected requirements.

## 12. Next proposed action

Implement `WP-CORE-01` and `WP-CORE-02` first. Use a minimal in-memory test
environment before connecting MuJoCo. Submit the initial contract pack and one
recorded AstraGrid-shaped example episode for architecture review.
