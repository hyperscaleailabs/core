# Acceptance criteria template: models

Per the [project lifecycle](../sdlc/LIFECYCLE.md#project-shape), every project
that touches this subproject includes these criteria in its acceptance
criteria, instantiated for the specific change. Cross-project work includes
the template of every subproject it touches.

- [ ] **The model is trained**: the training run completes on the target
      golden slice, with the run transcript and loss curve committed as
      evidence.
- [ ] **A regression test exists for the model**: a re-runnable benchmark on
      held-out golden cases (latency, throughput, per-failure-category pass
      rates) that detects regressions against the previous accepted run.
- [ ] **Trained, evaluated, and run on the golden dataset** for the set of
      predefined open-source models in [model/registry.yaml](model/registry.yaml):
      the pipeline (pull golden -> fine-tune -> benchmark -> serve) executes
      end to end for each registry model the change affects.

## Compact regression (per-PR scale)

The regression test at PR scale is deliberately compact - several fixed
example sets, not extensive training-correlation inference:

1. Pull the fixed golden slice (`ecommerce-ecinstruct`, train split).
2. Fine-tune the smoke model (`HuggingFaceTB/SmolLM2-135M-Instruct`, 32
   examples, 2 epochs, 16 optimizer steps) with
   [train/finetune_lora.py](train/finetune_lora.py).
3. Compare the loss trajectory against the **previous accepted baseline**
   (first: [docs/evidence/2026-07-26-lora-smoke.md](docs/evidence/2026-07-26-lora-smoke.md),
   train_loss 3.647, final 3.43): downward trajectory, final loss within
   tolerance of the baseline.
4. Commit transcript and loss curve to [docs/evidence/](docs/evidence/).

Runs on the local K3s/k3d cluster when one is reachable, otherwise directly
on the host (data + training layer only) - the evidence states which.

## Two-tier verification (module CI/CD DAG)

Per the [generic process template](../sdlc/LIFECYCLE.md#stages), change
detection decides depth on every PR and merge:

- **This module modified** -> full extensive verification: complete evidence
  collection including the **product screenshot** and the regression run
  across the **training, evaluation, and inference pipelines** against the
  accepted baseline (compact regression above at PR scale; GPU benchmarks on
  served endpoints at release gates).
- **Module untouched** -> only the less extensive top-API-level regression
  that runs across all modules on every merge.

Evidence tiers apply ([AXIS.md](../AXIS.md#guardrails)): smoke-scale evidence
proves the pipeline, not model quality; state the tier on every record.

For remote execution, the named cluster must also satisfy
[infra/ACCEPTANCE.md](../infra/ACCEPTANCE.md). Real target configuration and
kubeconfigs are never committed as model evidence.
