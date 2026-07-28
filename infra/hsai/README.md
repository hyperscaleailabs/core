# HSAI console

`hsai` is the operational console for HSAILabs infrastructure and workloads.
It manages multiple named K3s clusters whose nodes communicate over Tailscale
and are administered over SSH.

## Safety boundary

The public repository contains the console, schemas, tests, and generic
examples. Real target names, SSH aliases, network addresses, credentials,
kubeconfigs, and environment-specific values live in the external runtime
configuration. By default:

```text
~/.hsailabs-core/hsai/
  config.json
  kubeconfigs/<cluster>.yaml
```

Both inventory and kubeconfigs are written with mode `0600`. Set
`HSAI_CONFIG` or pass `--config` to use a different external location.

## Install

```bash
python3 -m pip install -e infra/hsai
hsai --help
```

## Targets and clusters

Create an inventory entry from an existing SSH configuration alias:

```bash
hsai target add <target> --ssh-host <ssh-alias>
hsai target inspect <target>
```

Create a cluster and add agents:

```bash
hsai cluster create <cluster> --server <server-target>
hsai cluster node-add <cluster> <agent-target>
hsai cluster plan <cluster>
```

Every cluster has exactly one server. `plan` performs only SSH inspection and
reports blockers or changes. `provision` installs the pinned K3s version on
the server first, reads its join token without persisting it, joins agents,
and writes a private kubeconfig whose API address is the server's Tailscale
IPv4 address.

```bash
hsai cluster provision <cluster>
hsai cluster status <cluster>
hsai cluster doctor <cluster>
```

Provisioning requires Debian, Tailscale IPv4, at least 50 GiB free under
`/var/lib`, and non-interactive sudo on every target. K3s uses `tailscale0`
for its node and Flannel interface.

## Models and JAX

Model and training commands address a named cluster, not a machine:

```bash
hsai model deploy gemma-vllm --target <cluster>
hsai model smoke gemma-vllm --target <cluster>

hsai train deploy --target <cluster> --image <registry>/jax-smoke:<immutable-tag>
hsai train status --target <cluster>
hsai train smoke --target <cluster>
```

Only one GPU vLLM deployment is active on a single-GPU cluster. Selecting
Gemma scales an existing Ultravox deployment to zero, and vice versa. The JAX
smoke performs deterministic training and held-out validation and reports its
evidence tier as a simulation demo. It proves the execution pipeline, not
model quality or physical-system behavior.

## Testing

```bash
PYTHONPATH=infra/hsai/src python3 -m unittest discover -s infra/hsai/tests -v
```

The mocked integration test creates a server plus two agents, verifies that
planning is non-mutating, installs the server before the agents, and proves
that preflight blockers prevent partial mutation.
