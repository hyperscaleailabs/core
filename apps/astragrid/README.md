
# HSAILabs Golden Use Case

AstraGrid is the first flagship application of [HSAILabs core](../../README.md);
see [MISSION.md](../../MISSION.md) for the lab direction. The initiation package
(PRD, reference architecture, plan, and handoff for both the core platform and
this application) lives in
[docs/strategic/20260727-astragrid/](../../docs/strategic/20260727-astragrid/).

## Voice-Controlled Lunar Power and Thermal Maintenance Rover

### One-sentence explanation

> Through an HSAILabs Meet room, a human tells a simulated rover to inspect a lunar power station, identify the overheating or dust-degraded component, restore it, and return before exhausting its energy reserve.

This is the right single flagship because it is:

* Understandable in under 30 seconds.
* Visually demoable.
* A real autonomy problem rather than a generic chatbot wrapper.
* Broadly relevant to energy, robotics, aerospace and remote industrial operations.
* Technically rich enough to demonstrate modern AI/ML infrastructure.
* Narrow enough to build incrementally.

NASA identifies surface power and thermal systems, dust mitigation, logistics, and robotics and autonomy as important lunar infrastructure capabilities. Dust is especially useful as the first failure mode because it can degrade exposed equipment and shorten mission life without requiring AstraGrid to claim deep aerospace or materials expertise. ([NASA][1])

---

# 1. The durable problem

The enduring economic problem is:

> **How can an autonomous system maintain critical energy and thermal infrastructure in an environment where human intervention is expensive, delayed, dangerous or unavailable?**

The lunar setting makes the problem memorable, but the underlying application maps directly to:

* Remote solar farms.
* Data-center power and cooling systems.
* Battery-storage facilities.
* Nuclear and industrial plants.
* Mining sites.
* Offshore facilities.
* Defense installations.
* Space stations and planetary outposts.

The product is therefore not fundamentally a “Moon rover project.” It is an **autonomous remote-infrastructure inspection, diagnosis and recovery system** demonstrated on the Moon.

---

# 2. The Golden Mission

## Mission name

**Restore Thermal Node B**

## Environment

A compact lunar installation contains:

* Three solar-power and thermal-management nodes.
* One communications relay.
* A rover charging station.
* Uneven terrain and obstacles.
* Variable lighting.
* Limited rover battery capacity.
* Simulated communications delay.
* Dust and temperature-related failure conditions.

## Voice instruction

The operator says through Meet:

> “Inspect Thermal Node B, determine why it is overheating, restore normal operation, and return with at least 25% battery.”

## Rover behavior

The rover must:

1. Interpret the spoken objective.
2. Convert it into a structured mission.
3. Navigate to the correct asset.
4. Inspect RGB, thermal and telemetry observations.
5. Classify the likely condition.
6. Select a recovery action.
7. Verify whether power and temperature improve.
8. Replan if the action fails.
9. Return before violating its reserve.
10. Explain the result to the operator.

## Initial recovery actions

Keep the action space small:

* `INSPECT_ASSET`
* `ACTIVATE_DUST_MITIGATION`
* `RESET_THERMAL_CONTROLLER`
* `WAIT_AND_RECHECK`
* `RETURN_TO_BASE`
* `REQUEST_HUMAN_REVIEW`
* `ABORT_MISSION`

The first prototype does not need a robotic arm. “Maintenance” can initially mean activating a local mitigation or reset mechanism after inspecting the asset.

That keeps the focus on perception, planning, resource management, evaluation and reliability.

---

# 3. The five-minute demonstration

## Act 1: Human intent

The operator joins an HSAILabs Meet room.

The room shows:

* The lunar simulation video.
* Rover camera feed.
* Thermal image.
* Battery reserve.
* Asset temperatures.
* Mission event timeline.

The operator gives the voice command.

## Act 2: AI planning

A multimodal planner produces:

```yaml
objective: restore_thermal_node_b

constraints:
  minimum_return_reserve: 0.25
  maximum_thermal_exposure_seconds: 90
  human_approval_for_unsafe_action: true

plan:
  - navigate_to: thermal_node_b
  - inspect:
      sensors: [rgb, thermal, telemetry]
  - diagnose
  - apply_recovery
  - verify
  - return_to_base
```

The operator approves the plan.

## Act 3: Autonomous execution

The rover navigates using the learned policy.

During execution, AstraGrid injects one failure:

* Higher-than-expected wheel-energy consumption.
* Communication dropout.
* Sensor noise.
* Misclassified dust.
* Recovery action that does not initially work.

The rover must replan or request help.

## Act 4: Evaluation

The mission ends with:

* Success or failure.
* Remaining battery.
* Diagnosis correctness.
* Recovery effectiveness.
* Policy interventions.
* Safety violations.
* Comparison with a rule-based baseline.
* Complete replay.

## Act 5: Explanation

The agent reports:

> “Thermal Node B showed reduced solar output and increased radiator temperature consistent with simulated dust accumulation. Dust mitigation restored output by 18%. The rover returned with 31% battery after one route adjustment.”

The metrics must come from the simulation record rather than being invented by the language model.

---

# 4. Why this use case fits the immediate stack

## PyTorch

Use PyTorch for:

* Fine-tuning the multimodal diagnosis or skill-selection model.
* Training an anomaly classifier.
* A small VLA-style action head.
* Optional LoRA adaptation.
* Offline behavioral cloning.
* Policy checkpoint packaging.

The first learned multimodal policy does not need to generate wheel torques. It should convert visual observations and language into a **bounded high-level action vocabulary**.

That is an honest VLA implementation:

```text
vision + language + robot state
                ↓
        high-level action
```

## JAX and MJX

Use JAX/MJX for:

* GPU-vectorized rover simulation.
* Reinforcement-learning rollouts.
* Domain randomization.
* Energy-aware navigation.
* Fast evaluation across thousands of conditions.

MJX exposes MuJoCo through JAX and can execute on XLA-supported hardware, making it a natural way to demonstrate JAX, physics simulation and accelerated RL without duplicating the main PyTorch model stack. ([MuJoCo Documentation][2])

## Ray

Use Ray for the distributed experiment and evaluation control plane:

* Run many terrain seeds.
* Vary battery health.
* Vary lighting and sensor noise.
* Evaluate multiple policy checkpoints.
* Run fault-injection campaigns.
* Collect videos and trajectories.
* Retry failed simulation workers.

Ray’s RL architecture supports multiple environment runners and separate evaluation workers, which maps directly to distributed simulation and policy qualification. ([Ray][3])

## vLLM

Use vLLM to serve:

* The multimodal mission planner.
* Visual diagnosis explanations.
* Structured mission generation.
* Operator summaries.
* High-level recovery recommendations.

vLLM supports multimodal model inputs and OpenAI-compatible vision-style serving for supported models. ([vLLM][4])

## RL

RL solves one concrete problem:

> Select a route and sequence of inspections that maximize successful recovery while preserving sufficient energy to return.

State:

```text
rover position
terrain state
battery reserve
asset status
thermal exposure
mission progress
estimated return cost
communication availability
```

Reward:

```text
+ correct diagnosis
+ restored asset
+ mission completion
+ safe return
+ preserved battery

- unnecessary motion
- excessive thermal exposure
- wrong recovery action
- reserve violation
- collision
- unrecoverable mission state
```

Low-level emergency stopping and safety bounds remain deterministic.

## DPO

DPO is used only for **high-level plan preference**, not motor control.

Candidate plans might trade off:

* Fastest completion.
* Lowest energy consumption.
* Highest diagnostic confidence.
* Maximum inspection coverage.
* Lowest risk.

Preference order:

```text
safety
> successful return
> correct recovery
> diagnostic confidence
> energy preservation
> speed
```

This creates a credible DPO experiment without pretending that preference optimization directly learns safe rover dynamics.

---

# 5. The open robot

For the first implementation, use **TurtleBot3 Burger represented in MuJoCo** and visually adapt the environment to a lunar setting.

ROBOTIS maintains a MuJoCo model collection containing TurtleBot3 Burger and references a LeRobot workflow for collecting demonstrations and training or fine-tuning vision-language-action models on custom data. ([GitHub][5])

This choice is intentionally practical:

* Small action space.
* Established differential-drive behavior.
* Open ROS ecosystem.
* Easy simulated sensor mounting.
* Potential physical-robot path.
* Compatible with MuJoCo experimentation.
* Much less engineering risk than beginning with a six-wheel rocker-bogie model.

A later hardware or higher-fidelity embodiment can use the JPL Open Source Rover, which provides an Apache-licensed, consumer-component six-wheel research and education platform. ([GitHub][6])

The platform contracts should make the robot replaceable:

```text
TurtleBot3
    ↓
JPL Open Source Rover
    ↓
industrial inspection rover
    ↓
flight-qualified or planetary platform
```

---

# 6. Two connected intelligence loops

## Loop A: Mission intelligence

This is the primary six-week loop.

```text
voice objective
    ↓
multimodal mission plan
    ↓
RL/VLA policy execution
    ↓
distributed simulation
    ↓
failure and recovery analysis
    ↓
preference data
    ↓
policy improvement
```

It optimizes:

* Navigation.
* Inspection order.
* Energy usage.
* Failure recovery.
* Operator intervention.
* Mission success.

## Loop B: Physical-design intelligence

This is initially a small background experiment.

```text
public materials data
    ↓
material or component profile
    ↓
simulation parameters
    ↓
mission performance
    ↓
design comparison
```

Three hypothetical radiator or surface profiles might differ in:

* Thermal conductivity.
* Emissivity.
* Density.
* Dust degradation rate.
* Mass penalty.
* Recovery efficiency.

Materials Project provides an official Python API for retrieving public computational materials records. ([Materials Project][7])

In the initial prototype, material records only inform **simulation parameter profiles**. The project should not claim that it discovered a lunar-qualified material.

## Connecting the loops

The mission loop asks:

> Given this rover and thermal system, what is the best action?

The design loop asks:

> Given expected missions and environmental conditions, which simulated component profile produces better outcomes?

For example:

| Design profile           |          Rover energy |  Thermal recovery | Mission success |
| ------------------------ | --------------------: | ----------------: | --------------: |
| Lightweight coating      |    Low transport cost |          Moderate |             81% |
| High-emissivity radiator | Medium transport cost |              High |             89% |
| Dust-resistant surface   |           Higher mass | Stable under dust |             93% |

This creates a genuine connection between materials, energy and autonomy without making materials discovery part of the critical first release.

---

# 7. Application and core boundaries

```text
hsailabs-core/
├── apps/
│   └── astragrid/
│       └── scenarios/
│           └── lunar-thermal-maintenance/
├── models/
├── dtwins/
├── prod/
├── meet/
├── agents/
├── infra/
├── sdlc/
└── atlas/
```

## AstraGrid owns

* Lunar mission narrative.
* Asset definitions.
* Energy and thermal constraints.
* Mission reward composition.
* Domain-specific prompts.
* Demo UI composition.
* Scenario acceptance criteria.

## Core owns

| Core project | Reusable capability                                              |
| ------------ | ---------------------------------------------------------------- |
| `models/`    | Training, checkpoints, policy adapters and serving               |
| `dtwins/`    | Environment, sensors, actions, snapshots and rendering           |
| `prod/`      | Evaluation, telemetry, replay, fault injection and release gates |
| `meet/`      | Video, voice, commands, approval and intervention                |
| `agents/`    | Planner and supervisor contracts                                 |
| `infra/`     | Ray, GPU runtime, Kubernetes and observability                   |
| `sdlc/`      | Automated benchmark and release workflow                         |
| `atlas/`     | Dataset cards, experiment reports and research synthesis         |

AstraGrid consumes these capabilities through contracts. Core never imports AstraGrid code.

---

# 8. The stable technical invariant

Specific models will change. The durable asset is this lifecycle:

```text
dataset or generated trajectories
        ↓
training and fine-tuning
        ↓
policy serving
        ↓
physics simulation
        ↓
distributed evaluation
        ↓
fault injection
        ↓
human supervision
        ↓
replay and qualification
        ↓
new training data
```

That loop remains relevant across:

* LLM and multimodal agent infrastructure.
* Robotics.
* Autonomous vehicles.
* Industrial inspection.
* Aerospace.
* Scientific automation.
* Energy optimization.

The individual technologies are placed deliberately:

| Technology               | Durable role                                  |
| ------------------------ | --------------------------------------------- |
| PyTorch                  | Model fine-tuning and policy learning         |
| JAX/MJX                  | Accelerated physics and RL                    |
| Ray                      | Distributed training, rollouts and evaluation |
| MuJoCo                   | Reproducible physical simulation              |
| vLLM                     | Multimodal and language-model serving         |
| VLM/VLA                  | Perception, grounding and skill selection     |
| RL                       | Resource-aware behavior                       |
| DPO                      | High-level operator preference alignment      |
| LiveKit Meet             | Human-agent interface and demonstration       |
| Kafka/ClickHouse/Grafana | Telemetry, replay and operational evidence    |

DPO and any particular VLA model should remain replaceable experiments. Evaluation, serving, distributed execution and lifecycle contracts are the strategically stable parts.

---

# 9. Minimum implementation scope

## First two weeks

### Week 1: working mission without model training

Deliver:

* TurtleBot3 MuJoCo lunar scene.
* Three thermal/power assets.
* Battery-consumption model.
* RGB and synthetic thermal observations.
* Scripted navigation baseline.
* One simulated dust failure.
* Structured mission schema.
* Trajectory and replay format.
* Headless and rendered execution.
* LiveKit video track.

Acceptance:

* One command starts the mission.
* The rover reaches Node B.
* It identifies the injected failure from ground-truth telemetry.
* It activates a recovery action.
* It returns with a reported energy reserve.
* The complete execution can be replayed.

### Week 2: RL, serving and distributed evaluation

Deliver:

* JAX/MJX navigation environment.
* PPO energy-aware policy.
* vLLM-served multimodal planner.
* Voice-to-structured-mission flow.
* Ray evaluation across at least 100 randomized runs.
* Grafana evaluation dashboard.
* Baseline-versus-RL comparison.
* Meet start, pause and abort controls.

Acceptance:

* RL exceeds random navigation.
* Rule-based and RL baselines use identical evaluation seeds.
* Every run records model, policy, simulator and scenario versions.
* Operator abort works.
* LLM output cannot bypass safety constraints.

---

# 10. Six-week target

By the end of six weeks, the demonstration should include:

1. Voice mission request through Meet.
2. Multimodal interpretation through vLLM.
3. PyTorch fine-tuned skill-selection adapter.
4. JAX/MJX RL navigation.
5. Ray-distributed evaluation.
6. MuJoCo rendered lunar environment.
7. Dust, sensor, energy and communication failures.
8. DPO experiment over mission-plan preferences.
9. Materials-profile comparison.
10. Complete replay and evaluation report.
11. Public architecture document.
12. Three-minute portfolio video.

## Target benchmark

Run at least:

* 3 policies.
* 5 failure classes.
* 5 terrain configurations.
* 5 battery profiles.
* 10 random seeds.

That produces 3,750 policy episodes - large enough to demonstrate distributed evaluation while remaining manageable.

---

# 11. Economics and Communication

## General audience

> A person speaks to a rover over video. The rover repairs a failing lunar energy system and returns safely.

## Engineering audience

> A multimodal planner served with vLLM coordinates a JAX/MJX RL policy trained and evaluated through Ray, with PyTorch fine-tuning, fault injection, replay and human supervision.

## Management audience

> HSAILabs demonstrates an end-to-end physical-AI infrastructure loop covering model serving, distributed RL evaluation, simulation, observability, safety controls and operator interaction.

## Scientific and aerospace audience

> AstraGrid is an early open benchmark for resource-constrained autonomous maintenance. It provides a path toward testing energy, thermal, materials and autonomy decisions together, while clearly separating simulated assumptions from validated domain knowledge.

---

# 12. Final formulation

## Product

**AstraGrid**

## Golden application

**Lunar Power and Thermal Maintenance Rover**

## Golden task

> Inspect a degraded thermal node, select and apply a recovery action, verify the result, and return with a safe energy reserve.

## Immediate technical objective

> Build a reproducible PyTorch, JAX/MJX, Ray, MuJoCo and vLLM learning-and-evaluation loop, demonstrated through LiveKit Meet.

## Long-term objective

> Develop open infrastructure for autonomous systems that maintain critical scientific and energy assets in remote terrestrial, aerospace and planetary environments.

The project is small enough to execute, visual enough to communicate, and technically substantial enough to serve as a practical application lab and shared knowledge foundation. It gives contributors a clear place to begin, experiment, and redirect their professional journey while progressively developing capabilities relevant to energy systems, scientific materials automation, aerospace, robotics, and space exploration - without requiring or implying deep domain expertise at the outset.


[1]: https://www.nasa.gov/lunar-surface-technology/?utm_source=chatgpt.com "Lunar Surface Technology"
[2]: https://mujoco.readthedocs.io/en/stable/mjx.html?utm_source=chatgpt.com "MuJoCo XLA (MJX)"
[3]: https://docs.ray.io/en/latest/ray-references/glossary.html?utm_source=chatgpt.com "Ray Glossary - Ray 2.56.0"
[4]: https://docs.vllm.ai/en/latest/models/supported_models/?utm_source=chatgpt.com "Supported Models - vLLM"
[5]: https://github.com/ROBOTIS-GIT/robotis_mujoco_menagerie?utm_source=chatgpt.com "GitHub - ROBOTIS-GIT/robotis_mujoco_menagerie: A collection of models for the MuJoCo physics engine from ROBOTIS · GitHub"
[6]: https://github.com/nasa-jpl/open-source-rover?utm_source=chatgpt.com "GitHub - nasa-jpl/open-source-rover: A build-it-yourself, 6-wheel rover based on the rovers on Mars! · GitHub"
[7]: https://docs.materialsproject.org/downloading-data/using-the-api?utm_source=chatgpt.com "Using the API | Materials Project Documentation"

