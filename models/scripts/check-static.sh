#!/usr/bin/env bash
# Models static checks: Python syntax, shell syntax, YAML validity, and golden
# config conformance to the registry schema.
#
# Extracted from .github/workflows/models.yml for the same reason as
# check-policy.sh: `make -C models static` has to run exactly what CI runs, or
# the two drift and the local command stops meaning anything.
#
# Requires: pyyaml, jsonschema.
# Exit 1 on any failure.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PYTHON=${PYTHON:-python3}
status=0

fail() {
  echo "::error::$1"
  status=1
}

echo "== python syntax =="
dirs=""
for d in models/inference models/train models/benchmark models/goldens; do
  [ -d "$d" ] && dirs="$dirs $d"
done
if [ -n "$dirs" ] && ! $PYTHON -m compileall -q $dirs; then
  fail "python syntax error under models/"
else
  echo "ok"
fi

echo "== shell syntax =="
shell_bad=0
for f in models/deploy/scripts/*.sh models/scripts/*.sh; do
  [ -e "$f" ] || continue
  bash -n "$f" || shell_bad=1
done
if [ "$shell_bad" -ne 0 ]; then
  fail "shell syntax error under models/"
else
  echo "ok"
fi

echo "== yaml validity =="
if ! $PYTHON - <<'PY'
import sys
from pathlib import Path
import yaml

bad = 0
for p in sorted(Path("models").rglob("*.yaml")):
    try:
        list(yaml.safe_load_all(p.read_text()))
    except yaml.YAMLError as exc:
        print(f"::error file={p}::{exc}")
        bad = 1
sys.exit(bad)
PY
then
  fail "invalid YAML under models/"
else
  echo "ok"
fi

echo "== golden configs match the registry schema =="
if ! $PYTHON - <<'PY'
import json
import sys
from pathlib import Path

import jsonschema
import yaml

schema = json.load(open("models/goldens/golden.schema.json"))
bad = 0
for p in sorted(Path("models/goldens/registry").glob("*.yaml")):
    try:
        jsonschema.validate(yaml.safe_load(p.read_text()), schema)
        print("valid:", p.name)
    except jsonschema.ValidationError as exc:
        print(f"::error file={p}::{exc.message}")
        bad = 1
sys.exit(bad)
PY
then
  fail "a golden config does not match models/goldens/golden.schema.json"
else
  echo "ok"
fi

if [ "$status" -eq 0 ]; then
  echo ""
  echo "models static checks OK"
fi
exit "$status"
