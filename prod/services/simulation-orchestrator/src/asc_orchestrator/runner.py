"""Orchestrator: expand a run into iterations, execute, aggregate, and decide (ASC-012).

Owns the run state machine (Ready → Running → Analyzing → decision) and Stop semantics (GW-10):
stopping preserves completed iterations and marks the remaining queued iterations *cancelled*, not
failed. The executor and gate engine are injected so this is testable without a broker or DB.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from asc_domain import ExperimentConfig, GateSet, Outcome, ReleaseDecision, RunMetrics, Trajectory
from asc_gate_engine import evaluate
from asc_kernel import HarnessMode, aggregate, has_policy_violation
from asc_telemetry import ArtifactStore, EventEmitter
from asc_worker import execute_iteration


class RunStatus(StrEnum):
    READY = "Ready"
    RUNNING = "Running"
    ANALYZING = "Analyzing"
    PASSED = "Passed"
    PASSED_WITH_WARNINGS = "Passed with warnings"
    MANUAL_REVIEW = "Manual review"
    BLOCKED = "Blocked"
    STOPPED = "Stopped"


_DECISION_TO_STATUS = {
    "Passed": RunStatus.PASSED,
    "Passed with warnings": RunStatus.PASSED_WITH_WARNINGS,
    "Manual review": RunStatus.MANUAL_REVIEW,
    "Blocked": RunStatus.BLOCKED,
}


@dataclass
class RunResult:
    run_id: str
    status: RunStatus
    planned: int
    completed: int
    cancelled: int
    metrics: RunMetrics
    decision: ReleaseDecision | None
    trajectories: list[Trajectory] = field(default_factory=list)


def execute_run(
    config: ExperimentConfig,
    harness: HarnessMode,
    gate_set: GateSet,
    *,
    run_id: str = "run-local",
    seed_base: int = 1_000,
    baseline_mean_cost: float | None = 0.15,
    emitter: EventEmitter | None = None,
    artifact_store: ArtifactStore | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> RunResult:
    """Execute a full run. ``should_stop`` is polled before each iteration for graceful Stop."""
    planned = config.execution.iterations
    completed: list[Trajectory] = []
    cancelled = 0

    for i in range(planned):
        if should_stop is not None and should_stop():
            cancelled = planned - i  # queued iterations are cancelled, not failed (GW-10)
            break
        completed.append(
            execute_iteration(
                config,
                harness,
                seed=seed_base + i,
                run_id=run_id,
                iteration=i,
                emitter=emitter,
                artifact_store=artifact_store,
            )
        )

    metrics = aggregate(completed, baseline_mean_cost=baseline_mean_cost)
    metrics.planned = planned
    metrics.cancelled = cancelled

    if not completed:
        return RunResult(run_id, RunStatus.STOPPED, planned, 0, cancelled, metrics, None, [])

    offenders = [t.trajectoryId for t in completed if has_policy_violation(t)]
    decision = evaluate(
        metrics,
        gate_set,
        related_trajectories={"policy": offenders[:50]},
        version_identifiers={
            "experiment": config.experiment.id,
            "candidate": config.experiment.candidateVersion or "",
            "harness": harness.value,
        },
        reproducibility={"seed_base": str(seed_base), "planned": str(planned)},
    )
    # A stopped-but-partial run reports Stopped; a fully completed run reports its decision.
    status = RunStatus.STOPPED if cancelled else _DECISION_TO_STATUS[decision.status.value]
    return RunResult(
        run_id, status, planned, len(completed), cancelled, metrics, decision, completed
    )


def summarize_failure_types(trajectories: list[Trajectory]) -> dict[str, int]:
    """Failure-type counts (the shape the Flink job computes in near-real-time downstream)."""
    counts: dict[str, int] = {}
    for t in trajectories:
        key = t.failureType or (
            "duplicate_transaction_risk" if has_policy_violation(t) else Outcome.SUCCESS.value
        )
        counts[key] = counts.get(key, 0) + 1
    return counts
