# Evidence: retiring the em dash guard

Decision: [ADR 0001](../../../docs/adr/0001-repo-retire-the-em-dash-guard.md).
Collected 2026-08-12 on the project branch.

**Evidence tier: process.** Nothing here is a claim about a physical or
simulated system. It is proof that the guard is gone, that the remaining
repository gates still pass, and that no dangling reference to the deleted file
survives.

## The guard is removed and nothing references it

```console
$ ls tools/policy/
check_ci_hygiene.py
check_links.sh
check_pii.sh

$ make help | grep -i writing
(no output)

$ grep -n '^policy:' Makefile
43:policy: pii links ci-hygiene ## Every repository-wide guard
```

The rule is out of `AGENTS.md`; the other three Writing rules are untouched.
The writing step is out of the `docs-links` job in
`.github/workflows/policy.yml`, and `check_links.sh` still runs there.

## Repository gates pass

```console
$ make policy
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

`check_ci_hygiene.py` is the one that mattered here: removing a step from a
policy job could have tripped `policy guards live in a script`. It did not.

Local note, not a repository defect: the checked-out Python had no PyYAML, so
`check_ci_hygiene.py` was run through a throwaway virtualenv via the `PYTHON`
variable rather than by installing into the working interpreter. The command
and its output are otherwise as shown.

## Dangling links

Deleting `tools/policy/check_writing.py` broke two Markdown links that pointed
at it from the retained lesson. Both were converted to code spans, since the
text still needs to name the file it is describing.

```console
$ grep -rn "check_writing" --include="*.md" .
docs/adr/0001-repo-retire-the-em-dash-guard.md:14: `tools/policy/check_writing.py` in the same change, on the principle that a
docs/adr/0001-repo-retire-the-em-dash-guard.md:28: - Delete `tools/policy/check_writing.py`.
sdlc/docs/articles/2026-07-30-em-dash/article.md:68: - **`tools/policy/check_writing.py`**, in the `policy` workflow and `make policy`,
sdlc/docs/evidence/2026-07-30-em-dash.md:96: `tools/policy/check_writing.py`, exercised with decoys in seven directions:
sdlc/docs/lessons/2026-07-30-em-dash.md:26: **Codified:** `tools/policy/check_writing.py`,
sdlc/docs/lessons/2026-07-30-em-dash.md:133: **Codified:** `tools/policy/check_writing.py`
```

Every remaining mention is a code span. `check_links.sh` passes.

## History retained and marked

The three 2026-07-30 documents are kept and each carries a superseded banner
pointing at ADR 0001, so the reversal reads as a decision rather than as drift:

- `sdlc/docs/articles/2026-07-30-em-dash/article.md`
- `sdlc/docs/lessons/2026-07-30-em-dash.md`
- `sdlc/docs/evidence/2026-07-30-em-dash.md`

## Pre-push hook parity

`pre-commit` is not installed on the machine this ran on. Per the `pr-flow`
skill, each hook in `.pre-commit-config.yaml` was reproduced by hand rather
than skipped:

| Hook | How it ran | Result |
|------|------------|--------|
| `gitleaks` | `gitleaks protect --staged` | no leaks found, 0 commits scanned |
| `pii-staged` | `bash tools/policy/check_pii.sh tree` (wider scope than staged) | clean |
| `pii-commit-msg` | commit message inspected for names, emails, home paths, co-author trailers | clean |
| `check-added-large-files` | byte count over added files against the 500 KB threshold | none over |
| `check-merge-conflict` | grep for conflict markers across changed files | none |
| `end-of-file-fixer` | last byte of each changed file checked for a newline | all end with a newline |
| `trailing-whitespace` | grep for trailing spaces across changed files | none |

`pre-commit run --all-files` itself did not run as such. `gitleaks` did run,
and it is the stronger of the two secret scans.
