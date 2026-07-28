# Acceptance criteria template: infrastructure

Per the [project lifecycle](../sdlc/LIFECYCLE.md#project-shape), every project
that touches infrastructure instantiates these criteria.

- [ ] A plan shows the complete intended change without mutating a target.
- [ ] Re-running provisioning converges without replacing healthy resources.
- [ ] Failure leaves a diagnosis and a safe, resumable next action.
- [ ] Public configuration contains no target identity, address, credential,
      kubeconfig, environment-specific value, or host-generated path.
- [ ] Network exposure is explicit and defaults to the private overlay.
- [ ] Cluster lifecycle tests cover one server and multiple agents.
- [ ] Physical evidence is distinguished from mocked or simulation evidence.

## Verification

Run the HSAI unit and mocked integration suite:

```bash
PYTHONPATH=infra/hsai/src python3 -m unittest discover -s infra/hsai/tests -v
```

For a real target, preserve the generated plan, doctor output, Kubernetes node
status, and workload smoke output as evidence after removing target-specific
identifiers.
