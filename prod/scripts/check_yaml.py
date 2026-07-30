#!/usr/bin/env python3
"""Validate every YAML document under prod/.

Extracted from .github/workflows/prod.yml so `make -C prod yaml` runs exactly
what CI runs. A check that exists only as workflow YAML is first exercised on a
hosted runner, after the handoff.

Superset dashboard exports are skipped: they embed JSON blobs that the import
job validates instead.

Exit 1 if any document fails to parse.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

SKIP_FRAGMENTS = ("dashboards/superset",)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    bad = 0
    checked = 0
    for path in sorted(root.rglob("*.yaml")):
        rel = path.relative_to(root)
        if any(fragment in str(rel) for fragment in SKIP_FRAGMENTS):
            continue
        try:
            list(yaml.safe_load_all(path.read_text()))
        except yaml.YAMLError as exc:
            print(f"::error file=prod/{rel}::{exc}")
            bad = 1
        else:
            checked += 1
    if bad:
        print("::error::invalid YAML under prod/")
        return 1
    print(f"yaml OK ({checked} documents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
