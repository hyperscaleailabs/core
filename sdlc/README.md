# SDLC

Software development lifecycle for the whole monorepo. This subproject defines the
top-level loops that every other subproject plugs into, plus the tooling that runs them.

## Development-to-production loops

Highest level loops, each with its own sub-loops:

1. **Development cycle** (defined here, applies to all subprojects): iterative
   development with a rotating AI Architect review on PRs, cycling across projects.
2. **Models**: a group of agents training, benchmarking, and optimizing models, with
   explicit work planning, execution, and acceptance criteria at the end. Accepted
   models are published for use by the other subprojects.
3. **Prod**: pre-release simulation with internal dashboard and configuration,
   promotion to canary, then ramped-up production.
4. **Agents**: run as APIs and LiveKit agents, pluggable and configurable into Meet.
5. **D-twins**: containerized service with autoscale and startup/shutdown orchestration
   via API and command line, operable by agents.
6. **Atlas**: publishes aggregated lessons learned as posts and white papers.
7. **Deployment**: models, prod, meet, agents, dtwins, and atlas are exposed as
   Kubernetes services/deployments, internal or external per the access tiers in the
   root [README](../README.md).

Status: placeholder. Structure and code migrate here in upcoming iterations.
See the root [README](../README.md) for repository rules (public repo: no PII, squash merges, policy checks required).
