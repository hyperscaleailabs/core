# Local K3s on this MacBook

K3s is Linux-only, so on macOS it runs inside a Linux VM. The supported local
setup is **k3d** (K3s-in-Docker) on top of **Colima** (or OrbStack/Rancher
Desktop - anything that gives you a Docker socket backed by a linux/arm64 VM).

## Setup

```bash
brew install colima docker k3d kubectl

# VM sized for model containers; adjust to taste
colima start --cpu 6 --memory 12 --disk 80

# single-node K3s cluster, NodePort range mapped to localhost
k3d cluster create hyperswarm \
  --port "30800-30810:30800-30810@server:0" \
  --agents 0

kubectl config use-context k3d-hyperswarm
kubectl get nodes
```

The `--port` mapping exposes our NodePort services (30800-30802) on
`localhost`, so `deploy/scripts/smoke-test.sh localhost` works unchanged.

## What runs locally, what doesn't

| Workload | Local (Apple Silicon, CPU) | Notes |
|----------|----------------------------|-------|
| faster-whisper | yes | int8 CPU is the default config |
| vLLM Gemma/Ultravox | no (GPU manifests) | vLLM GPU images need NVIDIA; local phase uses CPU-class stand-ins for pipeline testing |
| LoRA training smoke | yes, tiny models | e.g. a <=0.5B model on <=100 examples, minutes on CPU |
| JAX multi-worker smoke | yes | CPU workers; see docs/training-jax-k8s.md |

The local cluster's job is to prove the **pipeline** (pull -> train ->
benchmark -> report -> serve) end to end at toy scale; real model quality
numbers come from GPU targets in phase 2.

## Loading locally built images

k3d clusters can't see your local Docker images by default:

```bash
# registry.local is the neutral default the manifests use; no push needed,
# k3d imports straight into the cluster's image store
docker build -t registry.local/faster-whisper-server:latest inference/faster-whisper
k3d image import -c hyperswarm registry.local/faster-whisper-server:latest
```

## Teardown

```bash
k3d cluster delete hyperswarm
colima stop
```
