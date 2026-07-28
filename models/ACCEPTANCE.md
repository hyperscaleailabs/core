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

Evidence tiers apply ([AXIS.md](../AXIS.md#guardrails)): smoke-scale evidence
proves the pipeline, not model quality; state the tier on every record.
