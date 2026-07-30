#!/usr/bin/env bash
# Run the golden Purchase Ambiguity workflow and fail if the release decisions
# drift from the committed baseline.
#
# Extracted from .github/workflows/prod.yml so `make -C prod golden` runs
# exactly what CI runs. A baseline nothing compares against is not a baseline,
# and a comparison that only ever runs in CI is found to be wrong at the worst
# possible moment.
#
# Exit 1 on drift.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PYTHON=${PYTHON:-python3}
ITERATIONS=${ITERATIONS:-1000}

if ! $PYTHON prod/tests/e2e/golden_runner.py --iterations "$ITERATIONS" --out prod/artifacts/golden; then
  echo "::error::the golden workflow runner failed"
  exit 1
fi

if ! git diff --quiet -- prod/artifacts/golden; then
  echo "::error::the golden release decisions drifted from the committed baseline"
  git diff -- prod/artifacts/golden
  echo ""
  echo "If the change is intended, commit the regenerated decisions and say why in the PR."
  exit 1
fi

echo "release decisions reproduce the accepted baseline exactly"
