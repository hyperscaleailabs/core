"""In-memory control-plane store.

The phase-1 store keeps experiments (with immutable versions), runs, and results in memory so the
API runs without PostgreSQL. It exposes the same operations a SQLAlchemy-backed repository will in
ASC-010; swapping the backend does not change the API layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from asc_domain import ExperimentConfig, ReleaseDecision, RunMetrics


@dataclass
class ExperimentRecord:
    id: str
    draft: ExperimentConfig
    versions: list[ExperimentConfig] = field(default_factory=list)
    completed_run_ids: set[str] = field(default_factory=set)
    parent_id: str | None = None

    @property
    def has_completed_run(self) -> bool:
        return bool(self.completed_run_ids)


@dataclass
class RunRecord:
    id: str
    experiment_id: str
    harness: str
    status: str
    metrics: RunMetrics
    decision: ReleaseDecision | None
    offender_trajectory_ids: list[str] = field(default_factory=list)
    failure_types: dict[str, int] = field(default_factory=dict)


class Store:
    def __init__(self) -> None:
        self.experiments: dict[str, ExperimentRecord] = {}
        self.runs: dict[str, RunRecord] = {}

    # experiments -----------------------------------------------------------
    def create_experiment(self, cfg: ExperimentConfig) -> ExperimentRecord:
        exp_id = cfg.experiment.id or f"exp-{uuid.uuid4().hex[:8]}"
        rec = ExperimentRecord(id=exp_id, draft=cfg)
        self.experiments[exp_id] = rec
        return rec

    def freeze_version(self, exp_id: str) -> int:
        rec = self.experiments[exp_id]
        rec.versions.append(rec.draft.model_copy(deep=True))
        return len(rec.versions) - 1

    def clone_experiment(self, exp_id: str) -> ExperimentRecord:
        parent = self.experiments[exp_id]
        new_id = f"{parent.id}-clone-{uuid.uuid4().hex[:6]}"
        cfg = parent.draft.model_copy(deep=True)
        cfg.experiment.id = new_id
        rec = ExperimentRecord(id=new_id, draft=cfg, parent_id=parent.id)
        self.experiments[new_id] = rec
        return rec

    # runs ------------------------------------------------------------------
    def save_run(self, run: RunRecord) -> None:
        self.runs[run.id] = run
        if run.status not in {"Stopped"}:
            self.experiments[run.experiment_id].completed_run_ids.add(run.id)
