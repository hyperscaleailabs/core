# Infra

Cloud-agnostic deployment for the whole monorepo. The split of responsibilities:

- **Subprojects own their build**: each service keeps its `Dockerfile` and a
  `docker-compose.yml` next to its code, so it can be built and tested in isolation.
- **Infra owns the integrated picture**: k3d cluster definitions, Kubernetes manifests,
  and Terraform for the underlying VMs. Nothing service-specific is duplicated here;
  infra composes what subprojects publish.
- **HSAI owns cluster operations**: [`hsai`](hsai/README.md) keeps private
  target inventory outside the repository and plans, provisions, diagnoses,
  and operates named multi-node K3s clusters over Tailscale and SSH.

## Layout

| Directory | Purpose |
|-----------|---------|
| `terraform/modules/` | Reusable, provider-agnostic building blocks (VM pool, network, DNS, storage) |
| `terraform/envs/local/` | Local development stack (may be a no-op or a thin wrapper) |
| `terraform/envs/prod/` | Production VMs the k3d clusters run on. State is remote; no state or tfvars with real values in the repo |
| `k8s/base/` | Kustomize bases per service: Deployment/Job, Service, ConfigMap templates |
| `k8s/overlays/local/` | Local k3d overlay: single node, local registry, relaxed resources |
| `k8s/overlays/canary/` | Canary overlay: small replica counts, canary ingress weights |
| `k8s/overlays/prod/` | Production overlay: full replicas, autoscaling, production ingress |
| `k3d/` | Declarative k3d cluster configs (registry, ingress, port mappings) |
| `hsai/` | Console and library for target inventory, K3s cluster lifecycle, and workload dispatch |

## Conventions

- **Images**: one image per service, built from the subproject's `Dockerfile`, tagged
  with the git SHA (immutable) plus a moving environment tag. No `latest` in manifests.
- **Manifests**: plain Kubernetes YAML with Kustomize overlays. Helm only if a
  third-party chart is the natural source (e.g. ClickHouse, Kafka operators).
- **Namespaces**: one namespace per subproject (`meet`, `agents`, `dtwins`, `prod`,
  `models`, `atlas`), plus `platform` for shared services.
- **Local flow**: `docker compose up` inside a subproject for single-service work;
  `k3d cluster create --config infra/k3d/<env>.yaml` plus
  `kubectl apply -k infra/k8s/overlays/local` for the integrated environment.
- **Promotion**: local overlay, then canary, then prod, matching the release stages in
  [prod/](../prod/). Overlays differ only in scale, gating, and endpoints, never in
  application logic.

## Configuration and secrets

- No real endpoints, keys, or credentials anywhere in this repo; only `*.example`
  templates with placeholders. Policy checks enforce this.
- Runtime configuration for a deployment host is materialized under `~/.hsailabs-core`
  on that host and is assembled at deploy time from private configuration sources and
  environment-specific values (see the companion repo practice in
  [sdlc/notes.md](../sdlc/notes.md)).
- Deployment-specific workflows and environment definitions live in the private
  companion repo, not here; this directory holds only the generic,
  environment-agnostic machinery.
- Kubernetes consumes configuration via ConfigMaps/Secrets created from
  `~/.hsailabs-core` at deploy time (or via an external secrets operator later);
  manifests reference names only, never values.

## Cluster operations

Install the console from the repository, then keep the target inventory in
the external runtime configuration:

```bash
python3 -m pip install -e infra/hsai
hsai target add <target> --ssh-host <ssh-alias>
hsai cluster create <cluster> --server <target>
hsai cluster plan <cluster>
hsai cluster provision <cluster>
hsai cluster status <cluster>
hsai cluster doctor <cluster>
```

Add worker nodes with `hsai cluster node-add <cluster> <target>`. A cluster
has exactly one K3s server and zero or more K3s agents. Plans are read-only;
provisioning refuses to start unless every target passes its preflight gates.
See [the HSAI guide](hsai/README.md).

Status: cluster lifecycle is implemented in `hsai`; integrated service
manifests continue to land as services migrate.
