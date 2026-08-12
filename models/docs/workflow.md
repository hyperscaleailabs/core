# The run workflow

One **run** takes a model through select -> fine-tune -> benchmark -> report ->
serve -> publish. Everything is parameterized; a run is fully described by its
config and reproducible from it.

## The six steps

1. **Select the model** - any entry from `model/registry.yaml`
   (e.g. `gemma-2-2b-it`, `ultravox-v0_5-llama-3_2-1b`, `faster-whisper-small`).
2. **Select the fine-tuning method and data** - `lora`, `full`, or `dpo`
   (the RLHF-family method; preference-pair based), plus a golden and a train
   slice (e.g. first 100 items of `ecommerce-ecinstruct` train).
3. **Benchmark** - evaluate base model and fine-tuned checkpoint on the
   golden's *eval* slice (never the train slice). Metrics per modality:
   code pass@k (executed unit tests), text exact/contains match, ASR WER.
4. **Write the article** - each run produces `runs/<run-id>/report.md`:
   config, dataset slice, before/after metrics, per-category deltas,
   example wins and regressions. This is the run's white paper.
5. **Serve** - LoRA adapters load into the existing vLLM deployment
   (`--enable-lora`), exposed through the OpenAI-compatible gateway; full
   fine-tunes deploy as a new model revision.
6. **Publish** - push the run config and report (not weights) to the GitHub
   repo, so every run is reviewable history.

## CLI (target interface)

> **Status:** the `hsai` cluster, model-deploy, model-smoke, and JAX-smoke
> commands are implemented in [`infra/hsai`](../../infra/hsai/README.md).
> The data pull, full fine-tune, benchmark, report, and publish commands below
> remain the target interface and are implemented incrementally per
> [PLAN.md](PLAN.md). Until then, use the individual model scripts directly.

The orchestrator is `hsai` (HSAILabs). Target interface, implemented
incrementally per docs/PLAN.md:

```bash
# step 0: pull data (also implicit in `hsai run`)
hsai pull --golden ecommerce-ecinstruct --split train --limit 100

# steps 1-4 in one shot: fine-tune on 100 items, benchmark on 50 held-out items
hsai run --model gemma-2-2b-it --method lora \
        --golden ecommerce-ecinstruct --train-limit 100 --eval-limit 50 \
        --target local

# inspect the article
hsai report <run-id>

# step 5: serve the checkpoint through vLLM + gateway
hsai serve <run-id> --target local

# step 6: commit run config + report to the repo
hsai publish <run-id>
```

`--target` selects an entry in `deploy/targets.yaml`:

- `local` - the K3s/k3d cluster on this machine (phase 1)
- `<cluster>` - a named cluster in HSAI's external inventory. HSAI provisions
  its K3s server and agents over SSH/Tailscale, points kubectl at its private
  kubeconfig, and runs the same workload pipeline there.

## Run layout

```
runs/<run-id>/                # run-id: <date>-<model>-<method>-<golden>-<n>
├── config.yaml               # full resolved parameters (committed by publish)
├── report.md                 # the article (committed by publish)
├── train.jsonl, eval.jsonl   # pulled slices (local only)
├── checkpoint/               # adapter or weights (local only)
└── benchmark/                # raw before/after benchmark JSON
```

## Example session

> "Take the e-commerce golden, first 100 items, LoRA on Gemma, benchmark it."

```bash
hsai run --model gemma-2-2b-it --method lora \
        --golden ecommerce-ecinstruct --train-limit 100 --eval-limit 50
hsai report 20260726-gemma-2-2b-it-lora-ecommerce-ecinstruct-100   # read metrics
hsai serve  20260726-gemma-2-2b-it-lora-ecommerce-ecinstruct-100   # OpenAI API up
hsai publish 20260726-gemma-2-2b-it-lora-ecommerce-ecinstruct-100  # config+article to git
```
