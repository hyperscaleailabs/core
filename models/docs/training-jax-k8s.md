# Training at scale with JAX on Kubernetes (and locally on K3s)

This doc describes how the JAX training track works: what JAX buys us, how a
multi-host JAX job is laid out on Kubernetes, and how the same topology runs
at toy scale on the local K3s cluster on this MacBook.

The PyTorch track (`train/finetune_lora.py`) stays the default for
single-GPU LoRA; JAX is the path for **scale**: sharded training across many
hosts, and portability to TPU pods later.

## Why JAX for the scale track

- **Explicit sharding**: `jax.sharding.Mesh` + `NamedSharding` express data,
  tensor, and FSDP-style parallelism declaratively; the same training step
  runs on 1 CPU or 256 accelerators by changing the mesh.
- **Multi-host is first-class**: `jax.distributed.initialize()` turns N
  identical processes into one logical device array; there is no separate
  launcher framework to operate.
- **Mature scale stacks to borrow from**: MaxText (LLM pretraining/finetune),
  Orbax (distributed checkpointing), Grain (input pipelines).

## Topology on Kubernetes

A multi-host JAX job is N identical pods that must find each other. The
natural K8s encoding:

1. **Indexed Job** (or JobSet for multi-template jobs): `completions: N`,
   `parallelism: N`, `completionMode: Indexed`. Each pod gets
   `JOB_COMPLETION_INDEX` = its JAX `process_id`.
2. **Headless Service** selecting the job's pods gives stable DNS for the
   coordinator: pod 0 is the coordinator at
   `<job>-0.<svc>.<ns>.svc.cluster.local:1234`.
3. Each pod runs the same entrypoint:

```python
import jax, os
jax.distributed.initialize(
    coordinator_address=os.environ["COORDINATOR"],   # job-0 DNS + port
    num_processes=int(os.environ["NUM_PROCESSES"]),
    process_id=int(os.environ["JOB_COMPLETION_INDEX"]),
)
# after this, jax.devices() spans ALL hosts; build the mesh and train
```

4. **Data**: each process streams its own shard of the golden
   (`datasets` streaming + `.shard(num_processes, process_id)`), so no shared
   filesystem is needed for input.
5. **Checkpoints**: Orbax writes sharded checkpoints; on K3s that targets a
   PVC (`local-path` provisioner locally, object storage in the cloud).
6. **GPUs** (phase 2): request `nvidia.com/gpu` per pod and use the CUDA
   `jax[cuda]` wheel; the manifest is otherwise unchanged.

Manifest sketch (full version lands with PR7, see PLAN.md):

```yaml
apiVersion: batch/v1
kind: Job
metadata: {name: jax-train, namespace: hyperswarm-models}
spec:
  completions: 4
  parallelism: 4
  completionMode: Indexed
  template:
    spec:
      subdomain: jax-train          # matches the headless Service
      containers:
        - name: worker
          image: registry.local/jax-train:latest  # registry is deploy-time config
          env:
            - {name: COORDINATOR, value: "jax-train-0.jax-train:1234"}
            - {name: NUM_PROCESSES, value: "4"}
          # phase 2: resources: {limits: {nvidia.com/gpu: 1}}
      restartPolicy: Never
```

## Running it on the local K3s (this MacBook)

Local reality check, so expectations are set correctly:

- K3s runs in a Linux VM (see docs/local-k3s-macbook.md); containers are
  linux/arm64 and JAX's CPU wheels work fine there.
- `jax-metal` (Apple GPU) is not usable inside Linux containers, and there is
  no NVIDIA GPU. Local JAX training is **CPU-only**.
- Therefore the local cluster validates the *distributed topology* - N
  processes forming one mesh, sharded data, Orbax checkpoints to a PVC -
  with a tiny model (<=0.5B params) and <=100 golden items. It does not
  produce meaningful throughput numbers.

Smoke recipe (what PR7's evidence will show):

```bash
# 4-process CPU mesh on the k3d cluster, 50 items of ecommerce-ecinstruct
kubectl apply -f deploy/k3s/train/jax-train-job.yaml
kubectl -n hyperswarm-models logs -f job/jax-train -c worker --prefix
# expect: global device count = 4, loss decreasing, checkpoint in PVC
```

The identical manifest with `nvidia.com/gpu: 1` and `NUM_PROCESSES` scaled up
is the phase-2 cloud configuration - that is the point of doing the topology
work locally first.

## Scaling path

| Stage | Cluster | Mesh | Purpose |
|-------|---------|------|---------|
| Local smoke | k3d on MacBook, 4 CPU pods | `data=4` | prove topology, CI evidence |
| Single GPU box | K3s via SSH provisioner | `data=1..8` | real fine-tunes on goldens |
| Multi-box | K3s multi-node over SSH list | `data x fsdp` | larger models, full fine-tune |
| TPU/managed (optional) | GKE + JobSet | MaxText configs | pretraining-scale experiments |
