# AXIS

Compressed direction for humans and agents. Read this before deciding what to build.
Long form: [MISSION.md](MISSION.md) (why), [docs/strategic/DIRECTION.md](docs/strategic/DIRECTION.md)
(what, with research evidence), [README.md#tech-stack](README.md#tech-stack) (how).

## Why

> Biological and synthetic intelligence expanding together toward the stars.

## What

- **Core** is the physical-AI simulation, evaluation, and supervision fabric.
- **Apps** are proving grounds that create real requirements for it.
- Core generalizes only what an app has actually demanded. Core never imports app code.
- The durable asset is the loop, not any model:
  `data -> train -> serve -> simulate -> evaluate -> supervise -> replay -> data`.

## How

Grounded, immediate, unglamorous. Frameworks are adapters, never platform semantics.

| Horizon | Stack | Substrate |
|---------|-------|-----------|
| **Short** | PyTorch, JAX, Ray, vLLM. Train / evaluate / infer at scale | Open-source models, public datasets |
| **Mid** | MuJoCo, MJX, Isaac. Vectorized RL, domain randomization, fault injection | Physics-simulated environments, declared assumptions |
| **Long** | Scientific data adapters, instruments, hardware in the loop | Materials, energy, aerospace, robotics |

Always on: k3d, Kafka, ClickHouse, OTel, Prometheus, Grafana for evidence.
LiveKit Meet for human supervision.

## Effort weighting

Every unit of work declares a horizon. The mix, not any single PR, holds this ratio.

| Horizon | Effort | What it buys | Test before starting |
|---------|-------:|--------------|----------------------|
| **Short** | **80%** | Reproducible ML/RL infra that actually runs: contracts, local runtime, Ray parity, replay, release gates, CI, AstraGrid vertical slice | Does this make a seeded run reproducible, evaluable, or replayable? |
| **Mid** | **15%** | Physics-simulated environments and the sim-to-real control plane; distributed evaluation campaigns; measured sim-to-real predictivity | Does the short-horizon foundation it depends on already exist? |
| **Long** | **5%** | Direction kept alive, not built: scientific agents, autonomous-lab orchestration, materials / energy / aerospace / robotics convergence | Is this a note, a spike, or a research entry rather than a build? |

Rules that follow:

- Ambiguous work defaults to **short**. Nothing above a horizon is credible without it.
- Mid-horizon work that has no short-horizon foundation is **deferred**, not started.
- Long-horizon work is expressed as research, ADRs, and direction documents. Building
  it early is the main failure mode this ratio exists to prevent.
- A second application does not begin before the first has exercised the contracts.

## Guardrails

- **Local semantics are the reference.** Distribution changes capacity, never meaning.
- **Evidence or it didn't happen.** No simulated result is reported as physical validation.
- **Evidence tiers on every record**: simulation demo, simulation benchmark, distributed
  benchmark, hardware in the loop, physical.
- **Safety is deterministic.** Learned policies and language models propose; deterministic
  supervisors dispose.
- **No PII, ever.** Public repo. People are referred to by role.
- **Research is input, not evidence.** Market analysis sets direction; it never supports
  a technical claim about our systems.

## Realignment

Direction is re-derived from market research roughly every six months and logged in
[DIRECTION.md](docs/strategic/DIRECTION.md#realignment-log). This file is regenerated
from that realignment. Last: **2026-07-28**. Next: **2027-01**.

If work repeatedly fights the weighting, that is a signal to realign the axis, not to
quietly ignore the ratio.
