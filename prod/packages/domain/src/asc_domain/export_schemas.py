"""Export JSON schemas for the four core contracts.

Run: ``python -m asc_domain.export_schemas``. CI regenerates and diffs the output against the
checked-in ``packages/domain/schemas/`` to catch backward-incompatible contract changes
(``docs/design/CICD_STRATEGY.md`` §2, step 5).
"""

from __future__ import annotations

import json
from pathlib import Path

from asc_domain.models import (
    ExperimentConfig,
    GateResult,
    GateSet,
    ReleaseDecision,
    RunMetrics,
)

SCHEMAS = {
    "experiment_config": ExperimentConfig,
    "gate_set": GateSet,
    "gate_result": GateResult,
    "run_metrics": RunMetrics,
    "release_decision": ReleaseDecision,
}


def export(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, model in SCHEMAS.items():
        path = out_dir / f"{name}.schema.json"
        path.write_text(json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n")
        written.append(path)
    return written


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[2] / "schemas"
    for p in export(target):
        print(f"wrote {p}")
