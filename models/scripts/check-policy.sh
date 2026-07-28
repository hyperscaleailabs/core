#!/usr/bin/env bash
# Models module policy guards. Runs from anywhere; resolves the repository root.
#
# These live in a script rather than inline in .github/workflows/models.yml so
# they can be run before pushing (`make -C models policy`). A guard that exists
# only as workflow YAML is first exercised on a hosted runner, after the
# handoff - see atlas/docs/lessons/2026-07-28-atlas-integration.md, lesson L6,
# where two guards shipped broken for exactly that reason.
#
# Exit 1 on any violation.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SELF="models/scripts/check-policy.sh"
status=0

fail() {
  echo "::error::$1"
  status=1
}

# 1. Registry references stay configurable so the same manifests run against a
#    local registry, a lab registry, and whatever a deployment uses later. Only
#    the neutral registry.local default is allowed to be concrete.
echo "== no hardcoded org container registries =="
hits=$(grep -rn --include='*.yaml' --include='*.py' --include='*.sh' --include='*.md' \
         -e 'ghcr\.io/' -e '[a-z0-9-]*\.pkg\.dev/' -e 'docker\.io/hyperscale' models \
       | grep -v "^$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "hardcoded container registry reference found; use registry.local + override"
else
  echo "ok"
fi

# 2. Weights and run outputs are regenerated from a seed and a config; the
#    reproducible thing is the recipe, never the blob. Kubeconfigs are
#    credentials.
echo "== no committed weights, checkpoints, run artifacts, or kubeconfigs =="
hits=$(git ls-files models \
       | grep -E '\.(safetensors|gguf|bin|ckpt|pt|pth)$|/\.kube/|^models/runs/|^models/out/|^models/goldens/cache/' || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "weights, checkpoints, run artifacts, or kubeconfig committed"
else
  echo "ok"
fi

# 3. Repo-wide coverage exists in the policy workflow; kept here so the models
#    tree carries its own guard when path filters skip the others.
echo "== no absolute home-directory paths =="
hits=$(grep -rnE '/(Users|home)/[a-z0-9_-]+/' \
         --include='*.md' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.json' models \
       | grep -v "^$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "absolute home-directory path committed; use repo-relative paths"
else
  echo "ok"
fi

# 4. The console is named hsai. The earlier hsm spelling was renamed, and a
#    stale reference sends an operator to a command that does not exist.
echo "== hsai is the canonical console name =="
hits=$(grep -rnE '\bhsm\b' \
         --include='*.md' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.json' models \
       | grep -v "^$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "legacy hsm command found; use hsai"
else
  echo "ok"
fi

if [ "$status" -eq 0 ]; then
  echo ""
  echo "models policy guards OK"
fi
exit "$status"
