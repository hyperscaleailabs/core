---
document: Plan
project: AstraGrid
filename: pland.md
version: 0.1.0
status: Draft execution plan
date: 2026-07-27
---

# AstraGrid - Application Plan

## 1. Planning objective

Deliver one simple, communicable, reproducible mission that demonstrates a
complete embodied-AI lifecycle while creating a credible path toward scientific
automation, energy systems, aerospace, and space robotics.

## 2. Golden mission

> Inspect and restore a degraded lunar power or thermal node, verify the
> recovery, and return with a safe energy reserve under human supervision.

## 3. Product progression

```text
scripted mission
    → reproducible simulation
      → learned navigation/resource policy
        → multimodal planning and diagnosis
          → distributed robustness evaluation
            → human preference alignment
              → materials and thermal parameter studies
                → hardware and remote-operations experiments
```

## 4. Six-week outcomes

By the end of six weeks, AstraGrid should provide:

- One reliable MuJoCo mission.
- One JAX/MJX RL policy.
- One PyTorch model experiment.
- Ray-distributed evaluation.
- vLLM-compatible mission planner.
- Meet operator interaction.
- Fault injection.
- Replay and evaluation report.
- A small materials/thermal parameter study.
- Public documentation and demonstration.

## 5. Week-by-week plan

## Week 1 - Deterministic world and mission

Deliver:

- Application manifest.
- MuJoCo rover and lunar scene.
- Three energy/thermal nodes.
- Battery and route-cost model.
- Scripted policy.
- One dust-related failure.
- Core experiment record.
- Video and replay.

Exit criteria:

- One command runs the mission.
- Same seed produces the same outcome.
- All steps are recorded.
- The rover returns or fails for an explicit reason.

## Week 2 - Operator surface and initial evaluation

Deliver:

- LiveKit Meet application room.
- Simulation stream.
- Mission proposal.
- Approve, pause, and abort.
- Mission metrics.
- Rule, random, and shortest-path baselines.
- Evaluation report.

Exit criteria:

- Operator abort appears in replay.
- Policies use identical episode manifests.
- Application remains runnable without Meet.

## Week 3 - JAX/MJX reinforcement learning

Deliver:

- Vectorized MJX environment.
- PPO training.
- Domain parameter randomization.
- Safe-action wrapper.
- Baseline comparison.

Exit criteria:

- RL exceeds random policy.
- Rule baseline remains visible.
- Training manifest and checkpoint are stored.
- Safety violations are measured separately from reward.

## Week 4 - Ray distributed qualification

Deliver:

- Ray episode workers.
- Terrain, battery, sensor, and fault matrix.
- At least 500 episode runs.
- Failure taxonomy.
- Robustness dashboard.
- Retry and worker-failure evidence.

Exit criteria:

- Completed results survive worker failure.
- Policy and infrastructure failures are distinguished.
- Every aggregate links to individual episodes.

## Week 5 - Multimodal planning and PyTorch model

Deliver:

- vLLM-compatible planner endpoint.
- Structured mission-plan schema.
- PyTorch anomaly or skill-selection model.
- Model and dataset cards.
- Planner grounding to simulation telemetry.
- No direct low-level actuator authority.

Exit criteria:

- Invalid plans fail schema validation.
- Summaries cite experiment evidence.
- Model metrics are reported separately from mission metrics.

## Week 6 - Preference and scientific extension

Deliver:

- Chosen/rejected high-level plan pairs.
- Small DPO experiment.
- Three thermal/material parameter profiles.
- Comparison of mission outcomes.
- Public video, report, and tutorial.
- Next six-month backlog.

Exit criteria:

- Preference learning cannot override safety.
- Materials profiles are explicitly hypothetical or data-derived.
- No material is claimed as space-qualified.
- Final demonstration runs from documented instructions.

## 6. Detailed first two weeks

### Day 1

- Approve application and scenario manifests.
- Freeze action vocabulary.
- Freeze first failure: dust-related thermal/power degradation.
- Select initial rover model.

### Day 2

- Create MuJoCo scene.
- Add node positions and return base.
- Add deterministic rover movement and energy accounting.

### Day 3

- Implement synthetic node telemetry.
- Implement inspection radius and observation.
- Implement dust mitigation and verification.

### Day 4

- Integrate HSAILabs Environment and Policy contracts.
- Produce first structured trajectory.
- Add mission metrics.

### Day 5

- Add replay video and timeline.
- Write installation and run instructions.
- Record first architecture decision.

### Day 6

- Implement random, shortest-path, and scripted policies.
- Generate identical evaluation episode manifests.
- Compare results.

### Day 7

- Stabilize and tag baseline scenario.
- Produce a one-minute noninteractive video.

### Day 8

- Create Meet room.
- Stream simulation.
- Add mission text entry.

### Day 9

- Add proposal, approval, pause, and abort.
- Record operator events.

### Day 10

- Add telemetry tiles and final report.
- Validate replay synchronization.

### Days 11–12

- Add voice input.
- Convert transcription into structured mission request.
- Maintain text fallback.

### Days 13–14

- Run a 50-episode baseline suite.
- Publish initial benchmark and failure list.
- Freeze interfaces needed for RL work.

## 7. Six-month roadmap

### Months 1–2

- Stable Golden Mission.
- Ray robustness evaluation.
- PyTorch and JAX training lanes.
- vLLM planner.
- Meet operation.
- Public benchmark.

### Months 3–4

- Additional mission nodes and failures.
- Better terrain and energy models.
- Offline trajectory learning.
- Human correction collection.
- Hardware-compatible rover interface.
- Materials and thermal dataset adapters.

### Months 5–6

- Physical low-cost rover experiment.
- Sim-to-real comparison report.
- Remote industrial scenario pack.
- Scientific sample-handling scenario.
- Energy-aware AI workload experiment.
- Hardware-in-the-loop or communication-delay study.

## 8. Twelve-month direction

- Multi-rover missions.
- Fleet trajectory ingestion.
- Real-to-sim parameter estimation.
- Scientific instrument simulations.
- Autonomous laboratory scenario.
- Higher-fidelity thermal and power models.
- Aerospace mission and communication constraints.
- Planetary outpost scenario benchmark.
- Cross-simulator policy evaluation.

## 9. Metrics

### Mission

- Completion rate.
- Correct diagnosis.
- Recovery effectiveness.
- Return success.
- Remaining energy.
- Mission duration.
- Human interventions.

### Policy

- Reward.
- Collision and safety violations.
- Generalization across seeds.
- Robustness under faults.
- Inference latency.
- Checkpoint size.

### Infrastructure

- Episodes per hour.
- Worker success.
- Retry count.
- GPU utilization.
- Artifact completeness.
- Replay availability.

### Scientific integrity

- Assumptions documented.
- Data provenance.
- Evidence tier.
- Reproducibility.
- Known limitations.

## 10. Next proposed action

Create the application manifest and deterministic scenario package, then run a
single complete scripted episode through the core runtime before beginning Meet,
RL, or model-serving work.
