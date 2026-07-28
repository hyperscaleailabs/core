#!/usr/bin/env python3
"""CI schema-compat guard (docs/design/CICD_STRATEGY.md §2, step 5).

Regenerate the JSON schemas from ``packages/domain`` into a temp dir and diff against the
checked-in ``packages/domain/schemas/``. Exit non-zero on drift so a contract change without a
committed schema update (and version bump) fails the build.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "domain" / "src"))

from asc_domain.export_schemas import export  # noqa: E402

CHECKED_IN = ROOT / "packages" / "domain" / "schemas"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        generated = export(Path(tmp))
        drift = []
        for gen in generated:
            committed = CHECKED_IN / gen.name
            if not committed.exists():
                drift.append(f"missing checked-in schema: {gen.name}")
            elif committed.read_text() != gen.read_text():
                drift.append(
                    f"schema drift: {gen.name} (run `python -m asc_domain.export_schemas`)"
                )
    if drift:
        print("SCHEMA CHECK FAILED:")
        for d in drift:
            print(f"  - {d}")
        return 1
    print("schemas up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
