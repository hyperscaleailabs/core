# Evidence: local gate parity

Collected 2026-07-30 on the project branch, on the host toolchain.

**Evidence tier: process.** Nothing here is a claim about a physical or
simulated system. It is proof that every gate CI runs can now be run before
pushing, that the extracted guards fire in both directions, and that the one
defect this review found in the existing workflows was real.

Absolute paths in transcripts are redacted to `<repo>`; the repository's own PII
guard rejects the raw output, which is the guard working as intended.

## 1. The defect: a piped CI step reported the wrong exit status

`atlas.yml` built the site with `npm run build | tee build.txt`. GitHub's
default shell for a `run:` step is `bash -e {0}`, which does **not** set
`pipefail`, so the step's exit status was `tee`'s. A failing Astro build passed
the gate.

Reproduced against both shells with a command that always fails:

```console
$ cat gha_sim.sh
false | tee out.txt

$ bash -e gha_sim.sh; echo "step exit=$?"          # GitHub's default
step exit=0

$ bash --noprofile --norc -eo pipefail gha_sim.sh; echo "step exit=$?"   # shell: bash
step exit=1
```

`exit=0` on the left is the defect: CI reports success for a failed build.

Fixed by declaring `shell: bash` on the step, which is how GitHub opts a step
into `-eo pipefail`. The two other piped steps in the tree
(`atlas-ingest.yml`, `models.yml`) already set `set -o pipefail` explicitly and
were never affected; `prod.yml`'s new golden step declares `shell: bash`.

## 2. Extracted guards fire in the failing direction

Seven module policy guards moved out of workflow YAML into
`models/scripts/check-policy.sh` and `prod/scripts/check-policy.sh`. Each was
exercised with a planted decoy, then the decoy removed.

| Guard | Decoy | Exit | Message |
|-------|-------|-----:|---------|
| models: registries | `image: ghcr.io/someorg/trainer:v1` | 1 | hardcoded container registry reference found |
| models: artifacts | staged `_decoy.safetensors` | 1 | weights, checkpoints, run artifacts, or kubeconfig committed |
| models: home paths | `path: /Users/<name>/models/out` | 1 | absolute home-directory path committed |
| prod: registries | `europe-west4-docker.pkg.dev/p/r/control-api:v1` | 1 | hardcoded container registry reference found |
| prod: artifacts | staged `_decoy.tgz` | 1 | archive, checkpoint, or kubeconfig committed under prod/ |
| prod: home paths | covered by the same pattern as models | 1 | absolute home-directory path committed |
| prod: dashboards | `sqlalchemy_uri: clickhouse://admin:<pw>@...` | 1 | unmasked credential in an exported dashboard |

The dashboard guard was also exercised in the **passing** direction with
Superset's export mask (`:XXXXXXXXXX@`), which correctly does not fire: the
guard distinguishes a masked export from a real credential rather than banning
the field.

Two `models/scripts/check-static.sh` checks were exercised the same way:

| Check | Decoy | Exit | Message |
|-------|-------|-----:|---------|
| YAML validity | `a: [unclosed` | 1 | `::error file=models/model/_decoy.yaml::while parsing a flow sequence` |
| Golden schema | `name: bad` in `goldens/registry/` | 1 | `'domain' is a required property` |

The inline CI version raised an unhandled traceback on both; the extracted
script names the offending file and continues, so one bad file no longer hides
the rest.

### Self-exclusion is defensive, not currently load-bearing

Both scripts exclude their own path, as `atlas/scripts/check-policy.sh` does.
Removing the exclusion was tested and **neither script currently self-matches**:
the patterns are written as escaped regexes (`ghcr\.io/`), and the escape means
the source line does not match the pattern it holds. The exclusion is kept
because the atlas guard did self-match once the pattern was a plain literal, and
the next pattern added here may be one. Recorded as defensive rather than
proven, so nobody later reads it as verified.

## 3. The hygiene guard fires on all three of its rules

`tools/policy/check_ci_hygiene.py` guards the shape of the other gates. Each
rule was exercised by reverting the corresponding fix:

| Rule | Reverted | Exit | Message |
|------|----------|-----:|---------|
| pipefail | removed `shell: bash` from the atlas build step | 1 | `atlas.yml: job 'site', step 'Build the site...' pipes into tee without pipefail` |
| extracted guards | re-inlined a grep in `prod-policy-guards` | 1 | `prod.yml: job 'prod-policy-guards' runs an inline guard (...); move it into a check-policy.sh` |
| module verify | renamed `verify` to `verify-all` in `models/Makefile` | 1 | `models/Makefile: no verify target` |

All three restored, guard green.

## 4. One command runs every gate

```console
$ make verify
bash tools/policy/check_pii.sh tree
bash tools/policy/check_links.sh
markdown links OK
== piped steps set pipefail ==
ok
== policy guards live in a script ==
ok
== every module Makefile has a verify target ==
ok

CI hygiene OK

==> atlas
npm audit --omit=dev --audit-level=high
found 0 vulnerabilities
npm run index          Search index written: 35 documents
node scripts/check-collections.mjs
collections registered consistently: case-studies, comparisons, foundations,
frameworks, lab, learning-paths, news, patterns, production
npm run check          0 errors, 0 warnings, 0 hints
npm run build          48 page(s) built
bash scripts/check-policy.sh                    atlas policy guards OK

==> models
bash scripts/check-static.sh                    models static checks OK
bash scripts/check-policy.sh                    models policy guards OK

==> prod
ruff format --check packages services stream tests conftest.py scripts
64 files already formatted
ruff check packages services stream tests conftest.py scripts
All checks passed!
shell syntax ok
<repo>/prod/scripts/verify_package.py           PACKAGE VERIFICATION PASSED
<repo>/prod/scripts/check_yaml.py               yaml OK (28 documents)
<repo>/prod/scripts/check_schemas.py            schemas up to date
pytest packages services stream -q --cov=...    57 passed, TOTAL 91%
pytest tests/e2e -q                             4 passed
bash scripts/check-golden-baseline.sh
[unsafe] Blocked   violations=19 validation=0.981 p95=900.0ms
[safe  ] Passed    violations=0  validation=1.0   p95=900.0ms
release decisions reproduce the accepted baseline exactly
bash scripts/check-policy.sh                    prod policy guards OK

prod verify OK (terraform validate excluded: needs the terraform binary)

all gates OK

$ echo $?
0
```

Elided above for length: the coverage table, the per-page build list, and the
absolute interpreter paths. Nothing was skipped; every target in
`make verify` ran and the aggregate exit status is `0`.

## Baseline

First accepted baseline for repository-level gate parity.

| Measure | Value |
|---------|-------|
| Guards runnable only in CI, before | 7 module policy + 4 models static + 2 prod inline = 13 |
| Guards runnable only in CI, after | 0 |
| Modules with a `verify` target | 3 of 3 (`atlas`, `models`, `prod`) |
| Piped CI steps without pipefail | 0 (was 1, live defect) |
| Root `make verify` exit status | 0 |
| Unit tests / e2e | 57 / 4 passed, 91% line coverage |
| Golden release decisions | reproduce the committed baseline exactly |
| Toolchain | Python 3.14.6, Node v24.18.0, npm 11.16.0, ruff/pytest from a clean venv |

CI pins Python 3.11 (models) and 3.12 (prod) and Node 22; this run used the
host's Python 3.14 and Node 24, and produced the results above on both.

## Not covered

- `make terraform` was not run: the `terraform` binary is not on this host. It
  is deliberately outside `verify` for that reason, and CI still runs it.
- `make -C models smoke` was not run: it downloads real dataset slices and needs
  network plus the goldens' dependencies. CI still runs it as the
  `golden-smoke-evidence` job.
- `pre-commit run --all-files` was not run; `pre-commit` is not installed on
  this host and the flow forbids installing tooling unasked. Its hooks were
  reproduced individually - see the PR's Evidence section.
