#!/usr/bin/env bash
# HSAI console gates: compile, the unit and mocked integration suite, the
# example inventory, and the guard against committed deployment state.
#
# These live in a script rather than inline in .github/workflows/infra.yml so
# they can be run before pushing (`make -C infra verify`). A guard that exists
# only as workflow YAML is first exercised on a hosted runner, after the
# handoff - see atlas/docs/lessons/2026-07-28-atlas-integration.md, lesson L6.
#
# Runs from anywhere; resolves the repository root.
# Exit 1 on any failure.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PYTHON=${PYTHON:-python3}
status=0

fail() {
  echo "::error::$1"
  status=1
}

echo "== compile =="
if ! $PYTHON -m compileall -q infra/hsai/src infra/hsai/tests; then
  fail "python syntax error under infra/hsai"
else
  echo "ok"
fi

echo "== unit and mocked integration tests =="
if ! PYTHONPATH=infra/hsai/src $PYTHON -m unittest discover -s infra/hsai/tests -v; then
  fail "hsai test suite failed"
else
  echo "ok"
fi

# The example inventory is the only inventory the public repository carries. It
# is documentation that executes: if it stops loading, every quickstart in
# infra/hsai/README.md is wrong.
echo "== example inventory loads =="
if ! HSAI_CONFIG=infra/hsai/config.example.json PYTHONPATH=infra/hsai/src \
     $PYTHON -m hsai.cli target list; then
  fail "infra/hsai/config.example.json does not load"
else
  echo "ok"
fi

# Real inventories, kubeconfigs, and keys belong in the external runtime
# configuration, never in this repository.
echo "== no private deployment state =="
hits=$(git ls-files infra \
       | grep -E '(^|/)(config\.json|kubeconfigs?/|id_[a-z0-9]+)$' || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "private deployment state is committed"
else
  echo "ok"
fi

if [ "$status" -eq 0 ]; then
  echo ""
  echo "hsai gates OK"
fi
exit "$status"
