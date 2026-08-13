# Evidence: commit identity guard runnable before pushing

Project: [issue #29](https://github.com/hyperscaleailabs/core/issues/29).
Collected 2026-08-12 on the project branch.

**Evidence tier: process.** Nothing here is a claim about a physical or
simulated system. It is proof that the extracted guard reproduces the inline
behaviour, that it fires on every violation class it claims to cover, and that
it cannot report ok without having looked.

## The guard runs locally

```console
$ make commit-identity
bash tools/policy/check_commit_identity.sh
== commit messages and author identities (origin/main..HEAD) ==
ok (1 commit(s) scanned)
```

This is the whole point of the change. Before it, the only way to learn that a
commit identity was rejected was to push and read a red job.

## It fires on every class it claims to cover

Exercised against throwaway empty commits on a scratch branch, deleted
afterwards. Each run scans a single commit, so the reported violation is
unambiguous.

| Case | Expected | Result |
|------|----------|--------|
| Author identity outside the noreply forms | fail | exit 1, `author identity must use a noreply email` |
| Co-author trailer with a non-noreply identity | fail | exit 1, `co-author trailer with non-noreply identity` |
| Email address in the message body | fail | exit 1, `email address in commit message` |
| Co-author trailer with a noreply identity | **pass** | exit 0, `ok (1 commit(s) scanned)` |
| Selection matching no commits | fail | exit 1, `commit selection matched no commits` |

The fourth case is the documented exemption: GitHub injects noreply co-author
trailers on squash merges when the branch author differs from the merging
account. A guard that rejected those would fail on its own merge commits.

The trailer decoy trips two rules at once, which is correct: the trailer carries
an address, so both the co-author rule and the message-email rule apply.

```console
== commit messages and author identities (HEAD -n 1) ==
Commit 1d462d8: co-author trailer with non-noreply identity
Commit 1d462d8: email address in commit message
```

## It cannot pass without scanning

The last row above is a behaviour the inline version did not have. `git rev-list`
on an empty range succeeds and yields nothing, so the original loop would exit 0
having examined zero commits. A selection that matches nothing is now an error,
because a guard reporting ok without looking is worse than no guard.

## Selection logic

| Caller | Selection | Why |
|--------|-----------|-----|
| CI, pull request | `<base sha>..<head sha>` | Exactly the commits under review |
| CI, fallback when the range is unresolvable | `<sha> -n 20` | A recent slice rather than nothing |
| Local, branch with commits ahead of trunk | `origin/main..HEAD` | What this branch would push |
| Local, on trunk or no `origin/main` | `HEAD -n 20` | `origin/main..HEAD` is empty there |

Held as a shell array so the two-argument fallback does not depend on word
splitting. `shellcheck` is clean with no suppressions:

```console
$ shellcheck tools/policy/check_commit_identity.sh
$ echo $?
0
```

## The self-exemption stays narrow

Extracting the scan made `check_pii.sh` fail on the new script, which must name
the `co-authored-by` pattern in order to detect it. The inline version was
exempt because `SELF_PATHS` lists `.github/workflows/policy.yml`; the exemption
is per path, so it did not follow the code out. `SELF_PATHS` now lists the new
script as well, and so does `[allowlist] paths` in `.gitleaks.toml`. These are
two independent lists that happen to name the same enforcement files; updating
only the first left the gitleaks job red.

The exemption covers that one file, not `tools/policy/` as a whole. Proven by
staging a decoy file carrying a co-author trailer with a non-noreply address at
an unexempted path:

```console
$ git add decoy-check.md && bash tools/policy/check_pii.sh tree
POLICY VIOLATION [coauthor-trailer] in decoy-check.md
$ echo $?
1
```

The decoy was removed afterwards. Note that the trailer itself is described
rather than quoted here: `check_pii.sh` has no code-fence exemption, so an
evidence file reproducing the pattern fails the very guard it documents. That
happened once while writing this file.

## Repository gates

```console
$ make policy
bash tools/policy/check_pii.sh tree
bash tools/policy/check_links.sh
markdown links OK
bash tools/policy/check_commit_identity.sh
== commit messages and author identities (origin/main..HEAD) ==
ok (1 commit(s) scanned)
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

`check_ci_hygiene.py` still passes. Note that it never objected to the inline
block in the first place: `check_policy_jobs_are_scripts` binds only jobs whose
id ends `-policy-guards`, and `pii-and-secrets` does not match. This change
closes a local-runnability gap, not a rule violation.

Local tooling note: the working interpreter had no PyYAML, so
`check_ci_hygiene.py` was run through a throwaway virtualenv via the `PYTHON`
variable rather than by installing into it.

## Pre-push hook parity

`pre-commit` is not installed on the machine this ran on. Each hook in
`.pre-commit-config.yaml` was reproduced by hand:

| Hook | How it ran | Result |
|------|------------|--------|
| `gitleaks` | `gitleaks detect --source . --config .gitleaks.toml` over 20 commits | no leaks found |
| `pii-staged` | `bash tools/policy/check_pii.sh tree` | clean |
| `pii-commit-msg` | `make commit-identity`, which is now the codified form of this hook | clean |
| `check-added-large-files` | byte count over added files against the 500 KB threshold | none over |
| `check-merge-conflict` | grep for conflict markers across changed files | none |
| `end-of-file-fixer` | last byte of each changed file checked for a newline | all end with a newline |
| `trailing-whitespace` | grep for trailing spaces across changed files | none |

`pre-commit run --all-files` did not run as such. `gitleaks` did run.

`detect` is used deliberately rather than `protect --staged`. The staged variant
reported `no leaks found` here while CI failed the same file: after an amended
commit nothing is staged, so it scanned an empty set. A check that examined
nothing is indistinguishable from a check that passed.
