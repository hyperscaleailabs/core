#!/usr/bin/env bash
# Prod module policy guards. Runs from anywhere; resolves the repository root.
#
# These live in a script rather than inline in .github/workflows/prod.yml so
# they can be run before pushing (`make -C prod policy`). A guard that exists
# only as workflow YAML is first exercised on a hosted runner, after the
# handoff - see atlas/docs/lessons/2026-07-28-atlas-integration.md, lesson L6,
# where two guards shipped broken for exactly that reason.
#
# Exit 1 on any violation.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SELF="prod/scripts/check-policy.sh"
status=0

fail() {
  echo "::error::$1"
  status=1
}

# 1. Registry references stay configurable; the k3d-local registry is the only
#    concrete name allowed, and only in deploy scripts and manifests.
echo "== no hardcoded org container registries =="
hits=$(grep -rn --include='*.yaml' --include='*.py' --include='*.sh' --include='*.md' \
         -e 'ghcr\.io/' -e '[a-z0-9-]*\.pkg\.dev/' -e 'docker\.io/hyperscale' prod \
       | grep -v "^$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "hardcoded container registry reference found; use a configurable registry"
else
  echo "ok"
fi

# 2. Archives and checkpoints are build output; kubeconfigs and virtualenvs are
#    local machine state. None of it belongs in a public tree.
echo "== no committed run artifacts, kubeconfigs, or archives =="
hits=$(git ls-files prod \
       | grep -E '\.(zip|tar|tgz|safetensors|ckpt|pt|pth)$|/\.kube/|^prod/\.venv/' || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "archive, checkpoint, or kubeconfig committed under prod/"
else
  echo "ok"
fi

# 3. Repo-wide coverage exists in the policy workflow; kept here so the prod
#    tree carries its own guard when path filters skip the others.
echo "== no absolute home-directory paths =="
hits=$(grep -rnE '/(Users|home)/[a-z0-9_-]+/' \
         --include='*.md' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.json' prod \
       | grep -v "^$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "absolute home-directory path committed; use repo-relative paths"
else
  echo "ok"
fi

# 4. Superset masks the password on export. An export that carries a real one
#    was produced some other way, and the credential is now in a public tree.
#    grep -E has no negative lookahead: match every credentialed URI, then drop
#    the ones whose password is the export mask.
echo "== exported dashboards carry no unmasked database password =="
hits=$(grep -rnE 'sqlalchemy_uri:.*://[^:/]+:[^@]+@' prod/dashboards 2>/dev/null \
       | grep -v ':XXXXXXXXXX@' || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "unmasked credential in an exported dashboard; re-export (Superset masks it)"
else
  echo "ok"
fi

if [ "$status" -eq 0 ]; then
  echo ""
  echo "prod policy guards OK"
fi
exit "$status"
