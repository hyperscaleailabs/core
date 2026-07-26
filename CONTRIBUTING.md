# Contributing

This is a public repository. Read [README.md](README.md) first, especially the
repository rules. The short version: no PII ever, deliberate merges only.

## Workflow

1. Branch from `main`. Branch names: `<subproject>/<short-topic>`, e.g. `agents/text-agent-api`.
   No personal names or usernames in branch names.
2. Keep the change scoped to one subproject where possible.
3. Install the hooks before your first commit:

   ```bash
   pre-commit install --install-hooks
   pre-commit install --hook-type commit-msg
   ```

4. Open a pull request against `main`. CI must be green.
5. Squash merge. The squash commit message follows the commit conventions below.

## Commit conventions

- Format: `<subproject>: <imperative summary>`, e.g. `dtwins: add pixel streaming stub`.
  Repo-wide changes use `repo:` as the prefix.
- No `Co-Authored-By` or similar trailers. No tool or agent attributions.
- No personal names, usernames, or email addresses in commit messages.
- Git identity must be a neutral role identity. This repo sets a local
  `user.name`/`user.email` for that purpose; do not override it with a personal one.

## PII and secrets policy

Never commit, in any file or message:

- Personal names, usernames, or email addresses (role-neutral noreply identities excepted)
- Home directory paths (`/Users/...`, `/home/...`, `C:\Users\...`)
- Credentials, API keys, tokens, private keys, connection strings with passwords
- Hostnames, IPs, or IDs that identify a person or a private environment

Fixtures and examples use obviously fake placeholders (`user@example.com`,
`/path/to/project`). If a check flags a false positive, extend the allowlist in
[.gitleaks.toml](.gitleaks.toml) in the same PR and justify it in the description.

If something slips through: stop, do not push further commits on top. The remedy is
history rewrite plus rotation of anything secret. Open an issue titled `policy: incident`
without including the leaked value.

## Licensing

By contributing you agree your contribution is licensed under the repository's
Apache-2.0 license, or the subproject's license where one is declared. Imported
third-party work requires a `THIRD_PARTY_NOTICES.md` entry in the subproject and a
compatibility check at import time.
