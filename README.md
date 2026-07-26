# hsailabs core

[![policy](https://github.com/hyperscaleailabs/core/actions/workflows/policy.yml/badge.svg?branch=main)](https://github.com/hyperscaleailabs/core/actions/workflows/policy.yml)
[![HSAILABS-CORE](https://img.shields.io/badge/HSAILABS-CORE-1f6feb)](https://github.com/hyperscaleailabs/core)

Public monorepo of hsailabs. It aggregates the lab's projects into one place with shared
governance, shared tooling, and strict hygiene rules suitable for a public repository.

License: Apache-2.0 by default (see [Licensing](#licensing) for subproject specifics).

## Subprojects

| Directory | Project | Focus |
|-----------|---------|-------|
| [`sdlc/`](sdlc/) | SDLC | Software development lifecycle: top-level loops for all subprojects, agentic engineering workflows, rotating AI Architect PR reviews, delivery automation |
| [`models/`](models/) | Models | Model training, benchmarking, optimization, and inference serving. Produced models are consumed by the other subprojects |
| [`prod/`](prod/) | Prod | Simulation, evaluation, release, and observability. Split into `ui/`, `backend/`, and `platform/` (Kafka services, data plane with telemetry, ClickHouse, presentation via Superset and Grafana) |
| [`meet/`](meet/) | Meet | LiveKit / SFU based video conferencing system with pluggable LiveKit agents and pixel streaming integrated in the browser |
| [`agents/`](agents/) | Agents | Agent services: APIs plus LiveKit agents. Starts with a text agent, extends to voice (Ultravox plus Kokoro direction), aiming at a generalist agent pipeline pluggable into Meet |
| [`dtwins/`](dtwins/) | D-twins | Digital twins: seem-to-real and real-to-seem environments, 2D/3D/4D simulation engines, an engine-under-your-engine layer, demoable in Meet via pixel streaming |
| [`atlas/`](atlas/) | Atlas | Agentic research project that aggregates lessons learned across all subprojects and produces regular white papers and posts |
| [`infra/`](infra/) | Infra | Cloud-agnostic deployment: Terraform, Kubernetes manifests, integrated k3d environments. Subprojects own their Dockerfiles and compose files; infra owns the integrated picture |

Each subproject keeps its own `README.md` and, where it deviates from the repo default,
its own license and notice files.

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
- PRs should be scoped to one subproject where possible. Cross-cutting changes state
  their blast radius explicitly in the description.
- No merge commits from long-lived divergent branches; rebase before merging.

## Licensing

- Repo default: [Apache-2.0](LICENSE). Atlas is public under Apache-2.0 by design.
- Subprojects that incorporate third-party work must record the upstream license in a
  `THIRD_PARTY_NOTICES.md` inside that subproject and stay compatible with public
  Apache-2.0 distribution. Incompatible code does not enter this repo.
- When work migrates into this monorepo from an existing repo, its license and provenance
  are reviewed at import time.

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
