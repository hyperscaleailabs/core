---
document: Suggested Reference Architecture
project: HSAILabs/core
version: 0.1.0
status: Draft architecture proposal
date: 2026-07-27
---

# HSAILabs/core - Suggested Reference Architecture

## 1. Architecture objective

Provide a modular platform in which applications can compose model, simulation,
evaluation, agent, operator, and infrastructure capabilities without depending
on internal implementations.

## 2. Context view

```text
                           ┌──────────────────────┐
                           │ Human contributors   │
                           │ operators/reviewers  │
                           └──────────┬───────────┘
                                      │
                           LiveKit / Web / CLI
                                      │
┌──────────────────┐       ┌─────────▼───────────┐
│ Applications     │──────▶│ Core application SDK│
│ AstraGrid, others│       │ manifests/contracts │
└──────────────────┘       └─────────┬───────────┘
                                      │
               ┌──────────────────────┼───────────────────────┐
               │                      │                       │
      ┌────────▼────────┐   ┌────────▼────────┐    ┌────────▼────────┐
      │ Models/Serving  │   │ Digital Twins   │    │ Agents/Meet     │
      │ PyTorch/JAX     │   │ MuJoCo/MJX      │    │ planners/HITL   │
      │ vLLM/policies   │   │ other adapters  │    │ LiveKit         │
      └────────┬────────┘   └────────┬────────┘    └────────┬────────┘
               │                      │                       │
               └──────────────────────┼───────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │ Experiment runtime │
                           │ local / Ray         │
                           └──────────┬──────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
                    │                 │                  │
          ┌─────────▼────────┐ ┌──────▼───────┐ ┌──────▼────────┐
          │ Artifacts/replay │ │ Evaluation   │ │ Telemetry      │
          │ FS/object store  │ │ release gates│ │ Kafka/ClickH.  │
          └──────────────────┘ └──────────────┘ └───────────────┘
```

## 3. Architectural layers

## Layer 1: Application layer

Location:

```text
apps/<application>/
```

Owns:

- Product and mission semantics.
- Scenario definitions.
- Domain rewards and metrics.
- UI composition.
- Application prompts.
- Application-specific adapters.
- Acceptance criteria.

Depends only on public core contracts and capability providers.

## Layer 2: Contract and SDK layer

Owns:

- Schemas.
- Protocols.
- Capability discovery.
- Adapter registration.
- Compatibility.
- Client libraries.

This is the most stable platform layer.

Suggested packages:

```text
core/contracts/
core/sdk/
core/registry/
```

## Layer 3: Capability providers

Mapped to existing projects:

```text
models/   model lifecycle and serving
dtwins/   simulation and digital twins
agents/   planners, supervisors, and tools
meet/     human interaction
prod/     evaluation, telemetry, and replay
infra/    runtime and deployment
sdlc/     lifecycle automation and release
atlas/    research and knowledge artifacts
```

Each provider registers a capability identifier, version, and implementation.

Example:

```yaml
capability: dtwins.environment
version: 0.1
provider: mujoco
implementation: hsailabs.dtwins.mujoco:MujocoEnvironmentProvider
```

## Layer 4: Experiment runtime

The runtime coordinates:

- Application manifest resolution.
- Environment creation.
- Policy creation.
- Episode lifecycle.
- Event emission.
- Artifact persistence.
- Evaluation.
- Cancellation.
- Recovery.

Two implementations:

### LocalRuntime

Canonical reference semantics.

### RayRuntime

Scale-out implementation preserving the same episode and result contracts.

## Layer 5: Evidence plane

Stores:

- Manifests.
- Trajectories.
- Videos.
- Events.
- Metrics.
- Reports.
- Release decisions.

Initial:

- Local filesystem.
- SQLite index.

Production direction:

- Object storage.
- Kafka event stream.
- ClickHouse analytics.
- Grafana/Superset presentation.

## 4. Core runtime flow

```text
1. Load ApplicationManifest
2. Resolve required capabilities
3. Validate Dataset/Model/Environment manifests
4. Build episode matrix
5. Create policy and environment
6. Start ExperimentRecord
7. Execute observation/action loop
8. Process safety and operator events
9. Persist trajectory and artifacts
10. Run evaluators
11. Aggregate results
12. Apply release gates
13. Publish report and replay
```

## 5. Contract sketches

### Environment

```python
class Environment(Protocol):
    def metadata(self) -> EnvironmentMetadata: ...
    def reset(self, seed: int, parameters: dict) -> Observation: ...
    def step(self, action: Action) -> Transition: ...
    def render(self, mode: str) -> ArtifactReference | None: ...
    def snapshot(self) -> Snapshot: ...
    def restore(self, snapshot: Snapshot) -> None: ...
    def inject_fault(self, fault: FaultEvent) -> None: ...
    def close(self) -> None: ...
```

### Policy

```python
class Policy(Protocol):
    def metadata(self) -> PolicyMetadata: ...
    def reset(self, context: EpisodeContext) -> None: ...
    def act(self, observation: Observation) -> PolicyDecision: ...
    def close(self) -> None: ...
```

### PolicyDecision

```text
action
confidence
latency
model_version
explanation_reference
proposed_constraints
```

The safety wrapper evaluates the proposed action after the policy returns it.

### ExperimentRecord

```text
experiment_id
application
scenario
contract_versions
dataset_versions
model_versions
policy_versions
environment_version
seed
parameters
infrastructure_profile
operator_events
artifact_references
status
start_time
end_time
```

## 6. Event model

Use CloudEvents-inspired envelopes:

```json
{
  "id": "event-id",
  "type": "hsailabs.policy.decision",
  "source": "models/policy-service",
  "subject": "experiment/episode",
  "time": "ISO-8601",
  "contract_version": "0.1",
  "data": {}
}
```

Initial event types:

- `experiment.started`
- `environment.observation`
- `policy.decision`
- `safety.rejected`
- `fault.injected`
- `operator.intervened`
- `episode.completed`
- `evaluation.completed`
- `release.decided`

## 7. Model and serving architecture

```text
DatasetManifest
      ↓
training adapter
(PyTorch/JAX)
      ↓
ModelManifest + checkpoint
      ↓
policy adapter or serving adapter
      ↓
Policy contract
```

### vLLM

Use for language or multimodal planning and reporting where the chosen model is
supported.

Do not require vLLM for low-level policies.

### PyTorch

Primary model training and policy implementation framework.

### JAX/MJX

Accelerated simulation, scientific optimization, and RL research adapter.

## 8. Simulation architecture

```text
Application Scenario
       ↓
Environment Factory
       ↓
Simulator Adapter
(MuJoCo/MJX/Isaac/Gazebo/custom)
       ↓
Normalized observations/actions/events
```

Simulator-native state may be stored as an artifact but does not cross generic
application boundaries.

## 9. Human-supervision architecture

LiveKit Meet provides:

- Audio/video.
- Simulation stream.
- Operator commands.
- Approvals.
- Abort and pause.
- Agent responses.

The Meet adapter emits normalized operator events. AstraGrid interprets those
events in mission context.

## 10. Safety architecture

```text
policy proposal
      ↓
schema validation
      ↓
application constraints
      ↓
deterministic safety supervisor
      ↓
operator approval when required
      ↓
environment action
```

A language model cannot directly bypass the safety supervisor.

## 11. Deployment profiles

### Local developer

- Python.
- Local MuJoCo.
- Local artifact store.
- Optional single GPU.
- Local LiveKit or web UI.

### Workstation distributed

- Ray local cluster.
- Multiple GPUs.
- Parallel evaluation.
- Local ClickHouse/Grafana optional.

### Kubernetes

- Ray cluster.
- GPU scheduling.
- Object storage.
- Kafka.
- ClickHouse.
- Grafana/Superset.
- LiveKit services.
- vLLM services.

## 12. Repository dependency rules

Allowed:

```text
apps → core public SDK
models/dtwins/prod/... → core contracts
sdlc → all projects through declared automation interfaces
atlas → read-only project artifacts plus publishing interfaces
infra → deployment descriptors from all projects
```

Forbidden:

```text
core → apps
models → AstraGrid domain packages
dtwins → AstraGrid mission packages
prod → application-specific metric names in generic schemas
```

## 13. Architecture fitness functions

Automated checks should verify:

- Core does not import applications.
- Contracts remain serializable.
- Local and Ray result schemas match.
- Every run has a seed and version metadata.
- Safety rejections are persisted.
- Simulation evidence labels are present.
- Application-specific fields live under extension namespaces.
- Adapters pass conformance tests.

## 14. Evolution path

### v0.1

Contracts, local runtime, file artifacts, MuJoCo adapter, AstraGrid slice.

### v0.2

Ray evaluation, vLLM and LiveKit adapters, ClickHouse telemetry.

### v0.3

Multiple applications, object storage, Kubernetes deployment, scientific data
adapters.

### v1.0 candidate

Stable SDK, compatibility guarantees, hardware-in-the-loop evidence, and
scientific-agent orchestration interfaces.

## 15. Next proposed action

Create an architecture spike implementing the exact runtime flow with a
`ToyInspectionEnvironment` and `RulePolicy`. Validate the contracts and event
model before connecting AstraGrid, MuJoCo, Ray, or LiveKit.
