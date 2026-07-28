---
document: Suggested Reference Architecture
project: AstraGrid
version: 0.1.0
status: Draft architecture proposal
date: 2026-07-27
---

# AstraGrid - Suggested Reference Architecture

## 1. Architecture objective

Build a thin flagship application that composes HSAILabs/core capabilities
without reimplementing the platform.

## 2. Application context

```text
                 ┌──────────────────────┐
                 │ Human operator       │
                 │ voice/text/approval  │
                 └──────────┬───────────┘
                            │ LiveKit Meet
                 ┌──────────▼───────────┐
                 │ AstraGrid UI         │
                 │ mission + telemetry  │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │ Mission application  │
                 │ domain orchestration │
                 └─────┬──────────┬─────┘
                       │          │
          ┌────────────▼───┐  ┌──▼────────────────┐
          │ Planner/agent  │  │ Safety supervisor │
          │ vLLM-compatible│  │ deterministic     │
          └────────────┬───┘  └──┬────────────────┘
                       │           │
                       └─────┬─────┘
                             │ bounded actions
                    ┌────────▼────────┐
                    │ Rover policy    │
                    │ rule/RL/PyTorch │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ MuJoCo/MJX      │
                    │ lunar scenario  │
                    └────────┬────────┘
                             │
              ┌──────────────┼────────────────┐
              │              │                │
      ┌───────▼──────┐ ┌─────▼───────┐ ┌────▼─────────┐
      │ Core runtime │ │ Evaluation  │ │ Replay/       │
      │ local / Ray  │ │ and gates   │ │ telemetry     │
      └──────────────┘ └─────────────┘ └──────────────┘
```

## 3. Application packages

```text
apps/astragrid/
├── app.yaml
├── README.md
├── scenarios/
│   └── lunar-thermal-maintenance/
│       ├── scenario.yaml
│       ├── assets.yaml
│       ├── faults.yaml
│       ├── safety.yaml
│       └── acceptance.yaml
├── domain/
│   ├── mission.py
│   ├── rewards.py
│   ├── metrics.py
│   └── reports.py
├── environments/
│   ├── mujoco_adapter.py
│   └── mjx_adapter.py
├── policies/
│   ├── random.py
│   ├── shortest_path.py
│   ├── energy_rule.py
│   ├── rl_policy.py
│   └── skill_policy.py
├── agents/
│   ├── mission_planner.py
│   └── report_agent.py
├── meet/
│   ├── room.py
│   └── components/
├── experiments/
│   ├── baseline.yaml
│   ├── rl-training.yaml
│   └── robustness.yaml
└── docs/
```

## 4. Application manifest

Example:

```yaml
apiVersion: hsailabs.ai/v1alpha1
kind: Application
metadata:
  name: astragrid
  version: 0.1.0
spec:
  requiredCapabilities:
    - prod.experiment-runtime@0.1
    - prod.evaluation@0.1
    - prod.replay@0.1
    - dtwins.environment@0.1
    - models.policy@0.1
    - infra.local-runtime@0.1
  optionalCapabilities:
    - infra.ray-runtime@0.1
    - meet.operator-room@0.1
    - agents.mission-planner@0.1
    - models.vllm-serving@0.1
    - models.preference-training@0.1
  scenarios:
    - lunar-thermal-maintenance
```

## 5. Mission architecture

The application mission state machine:

```text
CREATED
  → PLAN_PROPOSED
    → WAITING_APPROVAL
      → APPROVED
        → NAVIGATING
          → INSPECTING
            → DIAGNOSING
              → RECOVERING
                → VERIFYING
                  → RETURNING
                    → COMPLETED
```

Alternative terminal or suspended states:

```text
REJECTED
PAUSED
ESCALATED
ABORTED
FAILED
```

State transitions are application-specific and stored as experiment events.

## 6. Planner boundary

Planner input:

- Operator request.
- Current asset summary.
- Rover state.
- Safety constraints.
- Available actions.

Planner output:

```yaml
objective: string
constraints: []
steps:
  - action: bounded_action
    target: optional_asset
    conditions: []
abortConditions: []
explanation: string
```

The planner cannot introduce unregistered actions.

## 7. Safety supervisor

The supervisor validates:

- Battery reserve.
- Return-cost estimate.
- Collision and terrain constraints.
- Allowed asset actions.
- Thermal exposure.
- Operator approval.
- Communication policy.

Decision:

```text
ALLOW
MODIFY
REQUIRE_APPROVAL
PAUSE
ABORT
```

Safety decisions become first-class events.

## 8. Environment model

### State

- Rover pose and velocity.
- Rover battery.
- Node temperature.
- Node power output.
- Dust/degradation state.
- Sensor status.
- Communication status.
- Mission phase.
- Terrain cost.

### Observation

- RGB frame reference.
- Synthetic thermal frame reference.
- Rover state vector.
- Asset telemetry.
- Mission state.
- Safety status.

### Action

High-level bounded action plus parameters.

### Reward

Used only for RL training and evaluation:

```text
+ mission completion
+ correct recovery
+ successful return
+ preserved reserve
- unnecessary travel
- wrong action
- safety violation
- collision
- failed return
```

Safety constraints are not represented only as reward penalties.

## 9. Policy composition

```text
high-level planner
        ↓
bounded mission action
        ↓
resource/navigation policy
        ↓
deterministic safety wrapper
        ↓
environment
```

Initial implementations:

- `RandomPolicy`
- `ShortestPathPolicy`
- `EnergyRulePolicy`
- `MJXPPOPolicy`
- Optional `PyTorchSkillPolicy`

## 10. Model architecture

### PyTorch lane

Potential first model:

- Inputs: RGB/thermal crop plus node telemetry.
- Output: one of `DUST`, `CONTROLLER_FAULT`, `NO_FAULT`, `UNCERTAIN`.
- Small CNN or compact multimodal encoder.
- Packaged as a policy-support model, not the mission controller.

### JAX/MJX lane

- Vectorized environment.
- PPO navigation/resource policy.
- Domain randomization.
- Checkpoint exported behind the core Policy contract.

### vLLM lane

- Mission-plan generation.
- Structured output.
- Report generation grounded in run metrics.

### DPO lane

- Chosen/rejected plan pairs.
- High-level preference alignment.
- Experimental and optional.

## 11. Distributed evaluation architecture

Ray evaluates a matrix:

```text
policy
× terrain
× battery profile
× fault
× sensor profile
× random seed
```

Each worker:

1. Loads immutable episode manifest.
2. Creates environment and policy.
3. Runs one episode.
4. Persists artifacts.
5. Returns normalized evaluation input.

The aggregator produces:

- Per-policy metrics.
- Confidence intervals.
- Failure categories.
- Worst-case episodes.
- Replay links.

## 12. Meet architecture

Meet tracks:

- Simulation stream.
- Rover camera.
- Thermal view.
- Operator voice.
- Agent audio or text.
- Approval and intervention controls.
- Telemetry data channel.

The Meet application uses generic core operator events but renders
AstraGrid-specific mission terminology.

## 13. Replay architecture

Replay aligns:

- Simulation video.
- RGB and thermal frames.
- State telemetry.
- Planner output.
- Policy actions.
- Safety decisions.
- Faults.
- Operator interventions.
- Final metrics.

A replay should remain viewable if the original planner or policy service is
offline.

## 14. Scientific-extension architecture

The initial extension point is a parameter-profile service:

```text
public dataset
    → documented feature extraction
      → parameter profile
        → scenario configuration
          → distributed evaluation
            → comparison report
```

Potential profiles:

- Battery degradation.
- Surface dust sensitivity.
- Thermal emission.
- Component mass.
- Energy efficiency.

These parameters remain explicitly separated from validated engineering design.

## 15. Deployment profiles

### Minimal local

- MuJoCo.
- Scripted policy.
- Local core runtime.
- File artifacts.
- Simple web or CLI replay.

### Interactive local

- LiveKit.
- vLLM-compatible planner or mock planner.
- Local Grafana optional.
- Single GPU.

### Distributed workstation/cluster

- Ray.
- MJX GPU rollouts.
- PyTorch training worker.
- Object storage.
- ClickHouse/Grafana.

## 16. Architecture fitness tests

- AstraGrid imports only public core SDK packages.
- Planner actions validate against the bounded vocabulary.
- Safety supervisor can reject every policy type.
- Every episode has a replay.
- Baselines and learned policies use identical episode manifests.
- Simulation evidence labels are present.
- Meet is optional for batch evaluation.
- vLLM is optional for scripted baseline.
- Ray is optional for one local episode.

## 17. Next proposed action

Implement the minimal local architecture profile with a scripted planner,
`EnergyRulePolicy`, MuJoCo environment, core experiment runtime, and replay.
Introduce voice, vLLM, JAX RL, and Ray only after this reference path passes all
fitness tests.
