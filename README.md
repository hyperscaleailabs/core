# hsailabs core

[![policy](https://github.com/hyperscaleailabs/core/actions/workflows/policy.yml/badge.svg?branch=main)](https://github.com/hyperscaleailabs/core/actions/workflows/policy.yml)
[![HSAILABS-CORE](https://img.shields.io/badge/HSAILABS-CORE-1f6feb)](https://github.com/hyperscaleailabs/core)

Public monorepo of hsailabs. It aggregates the lab's projects into one place with shared
governance, shared tooling, and strict hygiene rules suitable for a public repository.

License: Apache-2.0 by default (see [Licensing](#licensing) for subproject specifics).

## Start here

This README is the **entrance node of the repository graph**: every document
traces from here, and every update to the repository starts here - confirm the
changed nodes are reachable from this file and introduce no inconsistency.
Before any work, fetch in this order:

| Fetch | Where | What it gives you |
|-------|-------|-------------------|
| **The graph** | [sdlc/GRAPH.md](sdlc/GRAPH.md) | How to traverse the repo and pull per-stage context; placement rules; compaction |
| **The axis** | [AXIS.md](AXIS.md) | Compressed direction and the 80/15/5 effort weighting |
| **Strategic directions** | [docs/strategic/DIRECTION.md](docs/strategic/DIRECTION.md), [docs/strategic/](docs/strategic/) | Horizons, research evidence, strategic packages |
| **Relevant agents** | [AGENTS.md](AGENTS.md) (contract), [executive/](executive/) (CEO/CTO validation), role groups in [sdlc/LIFECYCLE.md](sdlc/LIFECYCLE.md) | Who does what, by role |
| **Relevant skills** | [`.claude/skills/`](.claude/skills/): `pr-flow`, `pr-verify`, `lessons` | Executable procedures for the cycle |

**SDLC in one paragraph**: work runs on the [four-level lifecycle](sdlc/README.md)
(strategic / tactical / daily / project). A project is a GitHub issue with a
links-only alignment header, executed as module-bounded PRs through the
[staged flow](sdlc/LIFECYCLE.md#stages) - Architect intent, MGMT documents,
BUILDER implementation, QA with **regression testing** (extensive for the
modified module, including the product screenshot and pipeline regression;
lighter API-level regression across all modules), cleanup and refinement,
acceptance review on the issue trail, article + post published from the owning
module, MGMT final review, squash merge. Evidence or it didn't happen. Module
READMEs carry the module-specific SDLC adjustments
(e.g. [models/ACCEPTANCE.md](models/ACCEPTANCE.md)).

## Mission and direction

> **Biological and synthetic intelligence expanding together toward the stars.**

HSAILabs is an open scientific application lab: infrastructure, models, simulations,
agents, and collaborative workflows for building increasingly capable autonomous
scientific and physical systems. The full statement lives in [MISSION.md](MISSION.md).

Three questions, kept deliberately separate:

| | Question | Answer |
|-|----------|--------|
| **WHY** | What is the lab ultimately for? | The line above. See [MISSION.md](MISSION.md) |
| **WHAT** | Which direction do core and apps move? | [docs/strategic/DIRECTION.md](docs/strategic/DIRECTION.md), realigned from market research each cycle |
| **HOW** | What do we build with, right now? | [Tech stack](#tech-stack) below - grounded, practical, immediate |

The direction runs across three horizons: **short**, reproducible AI/ML infrastructure
at scale on open models and open datasets; **mid**, physics-simulated environments and
the sim-to-real evaluation control plane; **long**, materials, energy, aerospace, and
robotics connected through one platform. Effort is weighted **80% short, 15% mid,
5% long**; all of it is compressed into [AXIS.md](AXIS.md), which is what contributors
and agents read before deciding what to build.

Flagship applications under [`apps/`](apps/) provide the practical proving grounds.
The first is [AstraGrid](apps/astragrid/README.md): a voice-controlled lunar power
and thermal maintenance rover - an end-to-end embodied-AI mission that exercises the
core platform (model serving, RL simulation, distributed evaluation, human
supervision through Meet) on a resource-constrained autonomous maintenance task.
Its initiation package - PRDs, reference architectures, execution plans, and
implementation handoffs for both the core platform and the application - lives in
[docs/strategic/20260727-astragrid/](docs/strategic/20260727-astragrid/).

A second direction, [NeuroDuet](apps/neuroduet/README.md), is proposed but not
scheduled: a language-aligned BCI simulation lab whose purpose is to test whether
contracts written for a rover mission survive an application with no robot, no
terrain, and no battery. Its research package is
[docs/strategic/20260728-neuroduet/](docs/strategic/20260728-neuroduet/).

## How this repository is structured

Each layer answers exactly one question, so that direction, behavior, capability,
state, and method never drift into each other.

| Layer | Answers | Where |
|-------|---------|-------|
| **Axis** | Where are we going, strategically and tactically, and how is effort weighted? | [AXIS.md](AXIS.md), long form in [MISSION.md](MISSION.md) and [docs/strategic/](docs/strategic/) |
| **Agent behavior** | How do agents and contributors work here? | [AGENTS.md](AGENTS.md) (canonical), [CLAUDE.md](CLAUDE.md) (pointer) |
| **Capability** | What can agents actually do, as executable procedure? | [`.claude/skills/`](.claude/skills/): `pr-flow`, `pr-verify`, `lessons` |
| **Method** | How does work move from research to production? | [sdlc/LIFECYCLE.md](sdlc/LIFECYCLE.md): staged project flow with QA and **regression testing** gates, pre-release and production gates |
| **State** | What are we doing, and where does it stand? | [docs/](docs/) and subproject READMEs: PRDs, ADRs, designs, plans, lessons |
| **Oversight** | Is the repo sound, from the executive perspective? | [executive/](executive/): standing CEO and CTO validation agents, outlooks, repo monitoring |
| **Value** | What does this all produce? | [apps/](apps/): the long-term value stream, evolving with core and aligned to the axis |

Everything realigns to the axis, including the axis itself: it is re-derived from
market research roughly every six months and logged in
[DIRECTION.md](docs/strategic/DIRECTION.md#realignment-log).

From this entrance node ([Start here](#start-here)), links trace into each
module's `README.md` and `ACCEPTANCE.md`, from modules into projects (GitHub
issues), and from projects into PRs, evidence, and articles. Agents pull
context by traversing the graph, not by scanning the tree.

## Subprojects

| Directory | Project | Focus |
|-----------|---------|-------|
| [`apps/`](apps/) | Apps | Flagship applications built on the core platform. [AstraGrid](apps/astragrid/README.md), a voice-controlled lunar power and thermal maintenance rover, is the first; [NeuroDuet](apps/neuroduet/README.md), a language-aligned BCI simulation lab, is proposed. Apps consume core capabilities through contracts; core never imports app code |
| [`sdlc/`](sdlc/) | SDLC | The four-level lifecycle and staged project flow (Human Architect + MGMT / BUILDER / QA / RESEARCHER-PUBLISHER agent groups), the repository graph, process lessons, delivery automation |
| [`models/`](models/) | Models | Model training, benchmarking, optimization, and inference serving on golden datasets, with its own CI/CD DAG and regression baseline. Produced models are consumed by the other subprojects |
| [`prod/`](prod/) | Prod | Simulation, evaluation, release, and observability. Split into `ui/`, `backend/`, and `platform/` (Kafka services, data plane with telemetry, ClickHouse, presentation via Superset and Grafana) |
| [`meet/`](meet/) | Meet | LiveKit / SFU based video conferencing system with pluggable LiveKit agents and pixel streaming integrated in the browser |
| [`agents/`](agents/) | Agents | Agent services: APIs plus LiveKit agents. Starts with a text agent, extends to voice (Ultravox plus Kokoro direction), aiming at a generalist agent pipeline pluggable into Meet |
| [`dtwins/`](dtwins/) | D-twins | Digital twins: seem-to-real and real-to-seem environments, 2D/3D/4D simulation engines, an engine-under-your-engine layer, demoable in Meet via pixel streaming |
| [`atlas/`](atlas/) | Atlas | Agentic research project that aggregates lessons learned across all subprojects and produces regular white papers and posts |
| [`infra/`](infra/) | Infra | Cloud-agnostic deployment: Terraform, Kubernetes manifests, integrated k3d environments. Subprojects own their Dockerfiles and compose files; infra owns the integrated picture |
| [`executive/`](executive/) | Executive | Standing CEO and CTO validation agents, strategic and tactical outlook material, repo-monitoring tooling |

Each subproject keeps its own `README.md` - which may carry module-specific
SDLC adjustments on top of the [generic process template](sdlc/LIFECYCLE.md)
(its `ACCEPTANCE.md` criteria, CI/CD DAG, regression definition) - and, where
it deviates from the repo default, its own license and notice files.

## Tech stack

The **how**: practical and immediate, grounded in ML and RL on PyTorch, JAX, and Ray
for training, evaluation, and inference at scale. Practiced first on open-source models
and datasets, then in physics-simulated environments, and finally connected to
materials, energy, aerospace, and robotics - the three horizons in
[DIRECTION.md](docs/strategic/DIRECTION.md). Frameworks here are adapters, not platform
semantics: any of them can be replaced without changing what an experiment means.

| Layer | Technologies |
|-------|--------------|
| AI & ML math | ML, RL, DPO, Transformers, LLM, VLM, V-LLM, Omni, ToT |
| OS & K8s | Debian, KVM, K3d (Helm, Kustomize) |
| Clouds | AWS, GCP, Azure, Terraform |
| Data | Kafka, Flink, Spark, PostgreSQL, Cassandra, MinIO, ClickHouse, OTel, Prometheus, Grafana, Superset |
| Scalable MLOps (model training, evaluation, inference) | JAX, Ray, vLLM |
| Services & agents infra | Custom, SDKs, LiveKit; RAGs: FAISS, Chroma, Milvus, PostgreSQL (pgvector), Helicone |
| Media & rendering | LiveKit SFU, WebRTC, UE Pixel Streaming |
| 4D sim-real | MuJoCo, Isaac Gym |
| Local models | Whisper, Gemma, Ultravox, Kokoro, Omni, and others |

## Target deployment

`hsailabs/core` runs in production as a set of services and jobs on k3d clusters on top
of VMs. Public and gated surfaces:

| Surface | Backed by | Access |
|---------|-----------|--------|
| Atlas | `atlas/` | Public. Text and video posts: agents, simulations, lessons learned, experiment results, webinar recordings |
| Meet | `meet/` | Public with approved sign-up. Conferencing with a plugged generalist voice agent and pixel streaming in the same browser |
| Internal dashboards | `prod/` | Gated to internal use. Release-into-production controls |
| APIs | `agents/`, `models/` | Requires API key |
| D-twins | `dtwins/` | Gated environment spin-up; demoable via pixel streaming in Meet |

Services and jobs are exposed as Kubernetes services and deployments, internal or
external per the table above. See [infra/](infra/) for how environments are assembled
and [sdlc/](sdlc/) for the development-to-production loops.

## Production configuration

`core` is a deployable Open Source product out of the box: clone it, stand it up on
k3d, run the full stack. Production configuration never lives in this repository.
The convention:

- Runtime configuration for a deployment host is materialized under `~/.hsailabs-core`
  on that host, outside any working tree.
- It is assembled at deploy time from private configuration sources and
  environment-specific values (endpoints, keys); see the companion repo practice in
  [sdlc/notes.md](sdlc/notes.md).
- The repo contains only templates and `*.example` files with placeholder values;
  the policy checks reject anything that looks like a real credential or identity.
- Services read configuration via environment variables or mounted files (12-factor);
  no configuration is baked into images.

## Repository rules

This repo is public. Two rules are non-negotiable and enforced by tooling:

### 1. No PII, ever

No personal names, usernames, email addresses, home directory paths, credentials, tokens,
or keys may appear anywhere in the repository. This includes source, docs, configs,
test fixtures, commit messages, and branch names. Contributors are referred to by role,
not by name.

Enforcement:

- `gitleaks` with custom PII rules ([.gitleaks.toml](.gitleaks.toml)) runs as a pre-commit
  hook and in CI on every push and pull request.
- A repo policy check ([tools/policy/check_pii.sh](tools/policy/check_pii.sh)) scans staged
  content and commit messages for emails, home paths, and co-author trailers.
- Git identity for commits must be a neutral role identity, not a personal one.

If PII ever lands in history, the remedy is history rewrite plus secret rotation,
not a follow-up commit. Treat prevention as the only cheap option.

### 2. Deliberate merges

- `main` is protected. No direct pushes; all changes arrive via pull request.
- Squash merge only. History on `main` stays linear, one commit per PR.
- Required checks (policy scan, lint, tests) must pass before merge.
- PRs are **module-bounded** (one subproject or app per PR) to keep boundaries
  clear and avoid coupling; genuinely cross-module changes state their blast
  radius explicitly and publish to [docs/projects/](docs/projects/).
- No merge commits from long-lived divergent branches; rebase before merging.

## Licensing

- Repo default: [Apache-2.0](LICENSE). Atlas is public under Apache-2.0 by design.
- Subprojects that incorporate third-party work must record the upstream license in a
  `THIRD_PARTY_NOTICES.md` inside that subproject and stay compatible with public
  Apache-2.0 distribution. Incompatible code does not enter this repo.
- When work migrates into this monorepo from an existing repo, its license and provenance
  are reviewed at import time.

## Documentation

| Location | Content |
|----------|---------|
| [AXIS.md](AXIS.md) | Compressed direction and effort weighting: read before deciding what to build |
| [AGENTS.md](AGENTS.md) | Canonical agent contract; [CLAUDE.md](CLAUDE.md) points at it |
| [MISSION.md](MISSION.md) | Lab mission and long-term direction |
| [docs/strategic/DIRECTION.md](docs/strategic/DIRECTION.md) | Directional axis: mission, vision, and the short/mid/long horizons, realigned each research cycle |
| [docs/strategic/](docs/strategic/) | Strategic packages: market research, PRDs, reference architectures, plans, and handoffs per initiative |
| [docs/adr/](docs/adr/) | Architecture decision records |
| [docs/projects/](docs/projects/), [docs/weekly/](docs/weekly/) | Cross-module publications: project whitepapers; weekly digests as short books |
| [sdlc/GRAPH.md](sdlc/GRAPH.md) | The repository graph: traversal, placement rules, compaction |
| [sdlc/docs/lessons/](sdlc/docs/lessons/) | Process lessons; module lessons live in `<module>/docs/lessons/` |
| [sdlc/](sdlc/) | Lifecycle, workflows, and delivery automation |
| [executive/](executive/) | CEO and CTO standing validation charters and repo monitoring |

## Getting started

```bash
git clone <repo-url> hsailabs-core
cd hsailabs-core
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

The pre-commit installation is mandatory for contributors; CI runs the same checks and
will reject anything the hooks would have caught.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, commit conventions, and the
full policy checklist.
