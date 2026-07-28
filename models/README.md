# Models

Train, benchmark, and serve models for the monorepo's subprojects (agents,
meet, dtwins, prod), anchored on **goldens**: pluggable golden datasets (local
configs pointing at Hugging Face datasets) for coding, e-commerce, and voice,
plus in-repo failure-mode packs.

Acceptance criteria template for projects touching this subproject:
[ACCEPTANCE.md](ACCEPTANCE.md).

The end-to-end workflow (select model -> fine-tune full/LoRA/DPO on a golden
slice -> benchmark on held-out cases -> generate a run article -> serve via
vLLM + OpenAI-compatible gateway -> publish config + article to this repo) is
specified in [docs/workflow.md](docs/workflow.md) and built incrementally per
[docs/PLAN.md](docs/PLAN.md).

Runtime identifiers (the `hyperswarm-models` namespace, `hyperswarm.ai/*`
labels, the `k3d-hyperswarm` context) predate the move into this monorepo and
are kept as-is; renaming them is a separate, deliberate change.

## Layout

| Path | Purpose |
|------|---------|
| `model/` | Model registry: which models we support and how each is served |
| `goldens/` | Golden datasets: HF-backed dataset configs + streaming pull script |
| `inference/` | Serving containers. vLLM-served models use the upstream vLLM image; faster-whisper has its own image |
| `train/` | Fine-tuning entrypoints (LoRA first) |
| `benchmark/` | Benchmark runner: latency, throughput, and failure-mode probes |
| `datasets/` | Domain packs: hand-curated failure-mode demonstrations |
| `deploy/k3s/` | Kubernetes manifests (kustomize) for K3s |
| `deploy/scripts/` | Provision K3s on a remote Debian box over SSH, deploy, smoke-test |
| `deploy/targets.yaml` | Deployment targets: local k3d now, SSH GPU boxes in phase 2 |
| `docs/` | Workflow spec, implementation plan, JAX-on-K8s guide, local K3s setup |

## Initial models

| Model | Modality | Served by | Manifest |
|-------|----------|-----------|----------|
| Gemma (`google/gemma-2-2b-it`) | text | vLLM | `deploy/k3s/models/gemma-vllm.yaml` |
| Ultravox (`fixie-ai/ultravox-v0_5-llama-3_2-1b`) | audio+text | vLLM | `deploy/k3s/models/ultravox-vllm.yaml` |
| faster-whisper (`Systran/faster-whisper-small`) | audio (ASR) | custom FastAPI container | `deploy/k3s/models/faster-whisper.yaml` |

All serving endpoints speak the OpenAI-compatible API (`/v1/chat/completions`,
`/v1/audio/transcriptions`), so the benchmark runner and downstream swarm agents
talk to every model the same way.

## Quick start (local K3s)

Requirements: a K3s cluster (local or remote), `kubectl` pointed at it.
GPU nodes need the NVIDIA device plugin; faster-whisper runs fine on CPU.

```bash
# deploy everything into namespace "hyperswarm-models"
./deploy/scripts/deploy.sh

# or a single model
kubectl apply -k deploy/k3s/base
kubectl apply -f deploy/k3s/models/faster-whisper.yaml

# smoke-test all deployed endpoints
./deploy/scripts/smoke-test.sh
```

## Remote deployment over SSH

Spin up a throwaway Debian VM anywhere, then:

```bash
# install K3s on the box and fetch a working kubeconfig locally
./deploy/scripts/provision-k3s-ssh.sh user@1.2.3.4

# deploy to it using the fetched kubeconfig
KUBECONFIG=.kube/remote-config ./deploy/scripts/deploy.sh
```

`provision-k3s-ssh.sh` is idempotent: re-running it upgrades K3s in place and
re-fetches the kubeconfig.

## Goldens

Goldens are the primary benchmarking/training data source: local YAML configs
in `goldens/registry/` pointing at Hugging Face datasets, pulled as normalized
JSONL slices:

```bash
pip install -r goldens/requirements.txt
python goldens/pull.py --golden ecommerce-ecinstruct --split train --limit 100
python goldens/pull.py --golden coding-mbpp --split eval --limit 100
python goldens/pull.py --golden voice-librispeech --split eval --limit 10 --smoke
```

See [goldens/README.md](goldens/README.md).

## Domain packs

A domain pack is a directory under `datasets/domain-packs/<domain>/` with:

- `pack.yaml` - metadata: domain, target modalities, referenced files
- `typical_inputs.jsonl` - representative real-world inputs for the domain
- `failure_modes.jsonl` - demonstrations of how models fail on this domain,
  each tagged with a failure category and the expected correct behavior

Packs are pluggable: the benchmark runner discovers them automatically and any
pack can be run against any registered model whose modality matches. See
`datasets/domain-packs/ecommerce/` for the reference pack and
`datasets/domain-packs/pack.schema.json` for the schema.

## Benchmarks

```bash
pip install -r benchmark/requirements.txt
python benchmark/run_benchmark.py \
  --endpoint http://<node>:30800/v1 \
  --model gemma-2-2b-it \
  --pack ecommerce
```

Outputs latency percentiles, throughput, and per-failure-category pass rates.

## Training

`train/finetune_lora.py` fine-tunes Gemma with LoRA on a domain pack's
`typical_inputs.jsonl`. It runs anywhere with a GPU; the same SSH-provisioned
box can be used by running it inside the cluster or directly on the host.

## How this subproject is developed

All work follows the repository's four-level SDLC
([sdlc/](../sdlc/README.md)); a project touching `models/` includes the
criteria from [ACCEPTANCE.md](ACCEPTANCE.md) in its acceptance criteria. CI
runs this subproject's checks (static checks, golden-smoke evidence, policy
guards) via `.github/workflows/models.yml`, path-scoped to `models/`.

This subproject was integrated from a standalone repository; its
pre-integration history, evidence, and lessons live under
[docs/](docs/PLAN.md).

## License

Apache 2.0 - see the root [LICENSE](../LICENSE).
