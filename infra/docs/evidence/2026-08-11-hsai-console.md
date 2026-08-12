# Evidence: hsai operational console and the JAX smoke workload

Project: [issue #22](https://github.com/hyperscaleailabs/core/issues/22).
Collected 2026-08-11 from the project branch, rebased onto `main` at `bb6cc11`.

Evidence tier: **mocked**. Every transcript below comes from the unit and
mocked integration suite and from static guards. No command in this record ran
against a physical target, and nothing here supports a claim about real
hardware. The acceptance criteria that require a provisioned cluster are
therefore left unchecked; see "Not proven" at the end.

## Unit and mocked integration suite

`make -C infra verify` runs exactly what the `infra` workflow runs:

```text
== compile ==
ok
== unit and mocked integration tests ==
test_install_commands_pin_version_and_overlay_interface ... ok
test_kubeconfig_uses_overlay_address_and_private_mode ... ok
test_mock_provision_installs_server_then_agents ... ok
test_plan_blocks_without_sudo ... ok
test_plan_is_inspection_only ... ok
test_provision_stops_on_preflight_blocker ... ok
test_rejects_unknown_cluster_target ... ok
test_requires_exactly_one_server ... ok
test_save_uses_private_permissions ... ok
test_gpu_deploy_blocks_without_device_resource ... ok
test_gpu_deploy_scales_other_gpu_model_down ... ok
test_jax_deploy_rejects_latest_image ... ok

Ran 12 tests in 0.003s

OK
== example inventory loads ==
server-node
worker-node
ok
== no private deployment state ==
ok

hsai gates OK
```

`test_plan_is_inspection_only` is the criterion "a plan shows the complete
intended change without mutating a target": it asserts the plan path issues no
mutating command. `test_provision_stops_on_preflight_blocker` is the criterion
"failure leaves a diagnosis and a safe, resumable next action".

## Public and private state stay separated

The example inventory is the only inventory the public repository carries, and
the guard refuses real state:

```text
== no private deployment state ==
ok
```

`test_save_uses_private_permissions` asserts inventory and kubeconfigs are
written `0600`, and `test_kubeconfig_uses_overlay_address_and_private_mode`
asserts the generated kubeconfig points at the overlay address rather than a
public one.

Repository-wide, `make policy` is green on the branch:

```text
bash tools/policy/check_pii.sh tree
bash tools/policy/check_links.sh
markdown links OK
python3 tools/policy/check_ci_hygiene.py
== piped steps set pipefail ==
ok
== policy guards live in a script ==
ok
== every module Makefile has a verify target ==
ok
== every module workflow is runnable locally ==
ok

CI hygiene OK
```

## Guard added in this PR, exercised before it was relied on

The branch arrived with an `infra` workflow and no `infra/Makefile`, so
`make verify` never ran the hsai suite: the module was gated on a hosted runner
only, which is lesson L6 of
[the atlas integration lessons](../../../atlas/docs/lessons/2026-07-28-atlas-integration.md)
recurring in a new module. Rule 3 of `check_ci_hygiene.py` did not catch it,
because it only inspects the Makefiles that already exist.

Rule 4 was added and failed against the reproduced state before the fix landed.

With `infra/Makefile` removed:

```text
== every module workflow is runnable locally ==
::error::.github/workflows/infra.yml: gates infra/** but infra/Makefile does
not exist; a module workflow must be runnable before pushing
```

With `infra/Makefile` present but the root `MODULES` not listing it:

```text
== every module workflow is runnable locally ==
::error::Makefile: MODULES does not list 'infra', so `make verify` skips the
gates in .github/workflows/infra.yml
```

After wiring both:

```text
== every module workflow is runnable locally ==
ok
```

The same reasoning moved the branch's inline "HSAI name is canonical" step out
of `models.yml` and into `models/scripts/check-policy.sh`, where
`make -C models policy` runs it:

```text
== hsai is the canonical console name ==
ok
```

## GPU deploys refuse an unready cluster

`test_gpu_deploy_blocks_without_device_resource` asserts a GPU workload is
refused when the cluster advertises no GPU device resource, rather than
scheduling a pod that fails at runtime.
`test_jax_deploy_rejects_latest_image` asserts a floating `latest` tag is
refused, so a training run always names the image it ran.

## Not proven

These `infra/ACCEPTANCE.md` criteria are **not** established by this record and
their boxes stay unchecked:

- Re-running provisioning converges without replacing healthy resources.
- Cluster lifecycle tests cover one server and multiple agents *on real
  targets*. The mocked equivalent
  (`test_mock_provision_installs_server_then_agents`) passes; the physical run
  has not happened.

Physical validation needs a provisioned cluster and is tracked as follow-up
work. Per the repository contract, no simulated result is reported as physical
validation.
