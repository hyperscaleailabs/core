---
document: Plan
project: HSAILabs/core
filename: pland.md
version: 0.1.0
status: Draft execution plan
date: 2026-07-27
---

# HSAILabs/core - Platform Plan

## 1. Planning objective

Establish a stable, reusable platform that supports AstraGrid while remaining
suitable for future applications in scientific automation, robotics, energy,
aerospace, and autonomous laboratories.

The plan intentionally separates:

- Stable contracts.
- Reference local implementations.
- Optional distributed implementations.
- Application-specific behavior.
- Experimental research lanes.

## 2. North star

Within twelve months, HSAILabs/core should provide an open, reproducible
infrastructure layer for:

- Multimodal model and policy training.
- JAX- and PyTorch-based execution.
- Distributed simulation and evaluation.
- Digital-twin adapters.
- Model and policy serving.
- Human-supervised agent operation.
- Experiment provenance and replay.
- Fault injection and release qualification.
- Scientific-agent and laboratory orchestration experiments.

## 3. Success measures

### Platform adoption measures

- Number of applications using only public contracts.
- Time required to create a new application adapter.
- Percentage of core capabilities exercised by more than one application.
- Number of reproducible public experiments.

### Reliability measures

- Reproducible seeded-run rate.
- Replay completeness.
- Distributed worker recovery rate.
- Percentage of failures assigned to a clear category.
- Contract compatibility across minor releases.

### Scientific and engineering measures

- Number of benchmarked policies and environments.
- Number of documented dataset and model cards.
- Number of simulation assumptions explicitly tracked.
- Number of application requirements generalized into reusable capabilities.

## 4. Workstreams

## Workstream A - Contracts and application SDK

Deliver:

- Application manifest.
- Environment and policy interfaces.
- Experiment and trajectory schemas.
- Capability discovery.
- Adapter registration.
- Compatibility tests.

Outcome:

Applications can depend on core without importing internal implementations.

## Workstream B - Model lifecycle

Deliver:

- Dataset and model manifests.
- PyTorch training adapter.
- JAX experiment adapter.
- Checkpoint and artifact references.
- Policy-serving interface.
- vLLM serving adapter for language and multimodal planners.

Outcome:

Applications can train or consume models through consistent metadata and
artifact boundaries.

## Workstream C - Simulation and digital twins

Deliver:

- Environment lifecycle.
- Snapshot and restore.
- Rendering.
- Domain-randomization contracts.
- Fault-injection interface.
- MuJoCo/MJX adapter.
- Later Isaac Lab, Gazebo, or domain simulators.

Outcome:

Simulation engines are replaceable while experiment semantics remain stable.

## Workstream D - Distributed execution

Deliver:

- Local episode runner.
- Ray evaluation adapter.
- Parallel benchmark manifests.
- Retry and idempotency behavior.
- GPU and worker resource profiles.

Outcome:

The same evaluation moves from a laptop or workstation to a cluster.

## Workstream E - Evaluation, replay, and governance

Deliver:

- Evaluator plugins.
- Failure taxonomy.
- Replay API.
- Release gates.
- Evidence labels.
- Model and policy comparison reports.
- Human intervention records.

Outcome:

A policy is promoted based on reproducible evidence, not a demonstration alone.

## Workstream F - Human and agent collaboration

Deliver:

- Generic operator-event contract.
- LiveKit Meet adapter.
- Agent tool contract.
- Approval, pause, abort, and escalation.
- Structured mission and report artifacts.

Outcome:

Humans and agents collaborate through auditable events.

## Workstream G - Research accumulation

Deliver:

- Atlas research ingestion.
- Dataset and technology landscape records.
- Architecture decision index.
- Experiment summaries.
- Reusable lessons from applications.

Outcome:

The project accumulates knowledge rather than repeatedly rediscovering it.

## 5. First two weeks

### Days 1–2

- Establish package and dependency rules.
- Add `apps/` as a first-class boundary.
- Approve contract names and versioning.
- Create architecture lint preventing core imports from apps.

### Days 3–5

- Implement `ApplicationManifest`, `Environment`, `Policy`, `Trajectory`, and
  `ExperimentRecord`.
- Add schema examples.
- Add validation and compatibility tests.
- Create a minimal in-memory environment.

### Days 6–7

- Implement the synchronous local runner.
- Persist a complete seeded episode.
- Add partial-run recovery.
- Produce a CLI for run and inspect.

### Days 8–10

- Add evaluator plugins and a comparison report.
- Implement replay from stored trajectory.
- Integrate a minimal AstraGrid environment adapter.
- Record architecture decisions.

### Days 11–14

- Add Ray evaluation adapter.
- Run local-versus-Ray semantic equivalence tests.
- Add operator intervention event.
- Produce Core Contract Pack v0.1 release candidate.

## 6. Six-week plan

### Weeks 1–2: Contract Pack and local runtime

Primary output:

- Stable v0.1 contracts.
- Local runner.
- File-backed artifacts.
- AstraGrid vertical slice.

### Week 3: Distributed evaluation

Primary output:

- Ray workers.
- Episode matrix execution.
- Retry behavior.
- Evaluation aggregation.

### Week 4: Model and serving adapters

Primary output:

- PyTorch policy adapter.
- JAX/MJX experiment adapter.
- vLLM planner-serving adapter.
- Model and checkpoint manifests.

### Week 5: Meet and operator controls

Primary output:

- Generic LiveKit operator channel.
- Approval and abort.
- Operator event storage.
- Application UI composition guidance.

### Week 6: Governance and second-application test

Primary output:

- Release gates.
- Failure taxonomy.
- Replay review.
- Minimal second application.
- v0.1 platform report.

## 7. Six-month roadmap

### Month 1–2: Reliable baseline

- Publish v0.1 contracts.
- Support AstraGrid baseline.
- Establish CI, examples, and developer documentation.
- Add benchmark and artifact dashboards.

### Month 3–4: Scaling and portability

- Kubernetes/Ray execution profile.
- Object-storage backend.
- Kafka and ClickHouse adapters.
- Multiple simulator adapters.
- GPU scheduling and cost telemetry.
- Cross-platform CPU/GPU validation.

### Month 5–6: Scientific application platform

- Scientific dataset adapters.
- Experiment-planner contract.
- Instrument or laboratory device simulator.
- Provenance graph.
- Multi-stage agent workflow.
- Human review and approval.
- Initial autonomous-laboratory reference application or scenario.

## 8. Twelve-month roadmap

- Cross-embodiment policy evaluation.
- Offline and online trajectory ingestion.
- Sim-to-real comparison records.
- Hardware-in-the-loop adapters.
- Fleet-learning dataset format.
- Multi-agent and multi-robot orchestration.
- Energy-aware workload scheduling.
- Scientific-agent runtime.
- Instrument and robot coordination.
- Formal experiment lineage and reproducibility reports.
- Community application templates.

## 9. Prioritization model

Each proposed core capability receives a score:

```text
priority =
    application_need
  + cross_application_reuse
  + reliability_value
  + scientific_reproducibility_value
  + operational_value
  - implementation_complexity
  - domain_specificity
```

High application urgency does not automatically justify a core abstraction.
AstraGrid may temporarily own adapters until patterns stabilize.

## 10. Dependency sequence

```text
contracts
  → local runtime
    → artifact persistence
      → evaluation and replay
        → AstraGrid vertical slice
          → distributed execution
            → serving and Meet adapters
              → governance
                → second-application validation
```

## 11. Release cadence

- Patch releases: implementation fixes and documentation.
- Minor releases: backward-compatible contracts and capabilities.
- Major releases: incompatible contract changes.
- Weekly experiment reports.
- Six-week platform review.
- Quarterly mission and roadmap review.

## 12. Next proposed action

Create the first fourteen GitHub issues from the two-week plan, link their
dependencies, and designate `ApplicationManifest`, `Environment`, `Policy`,
`Trajectory`, and `ExperimentRecord` as the first contract-review gate.
