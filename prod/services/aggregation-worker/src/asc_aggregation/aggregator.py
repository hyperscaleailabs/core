"""Aggregation fallback (ASC-017 / GW-11).

Recomputes run metrics directly from the iteration event stream so a run's final result is never
lost when Flink/Druid lag or are unavailable. It reconstructs per-trajectory outcomes from the
envelopes and reuses the kernel's aggregation, so this path and the streaming path agree on the
same metric definitions.
"""

from __future__ import annotations

from collections import defaultdict

from asc_domain import IterationEvent, Outcome, RunMetrics, Trajectory
from asc_kernel import aggregate
from asc_telemetry import IterationEventEnvelope


def _trajectory_from_events(events: list[IterationEventEnvelope]) -> Trajectory | None:
    terminal = next((e for e in events if e.eventType == "iteration_result"), None)
    if terminal is None or terminal.outcome is None:
        return None  # incomplete iteration; skip until its terminal event arrives
    has_violation = any(e.eventType == "policy_violation" for e in events)
    failure_type = next((e.failureClassification for e in events if e.failureClassification), None)
    return Trajectory(
        trajectoryId=terminal.trajectoryId,
        runId=terminal.runId,
        iteration=terminal.iteration,
        seed=terminal.seed,
        outcome=Outcome(terminal.outcome),
        latencyMs=terminal.latencyMs,
        costUsd=terminal.costUsd,
        retryCount=terminal.retryCount,
        failureType=failure_type,
        # A single marker event is enough for has_policy_violation() during aggregation.
        events=[IterationEvent(type="policy_violation")] if has_violation else [],
    )


def aggregate_envelopes(
    envelopes: list[IterationEventEnvelope], *, baseline_mean_cost: float | None = None
) -> RunMetrics:
    """Group envelopes by trajectory, reconstruct trajectories, and aggregate to RunMetrics."""
    by_traj: dict[str, list[IterationEventEnvelope]] = defaultdict(list)
    for e in envelopes:
        by_traj[e.trajectoryId].append(e)
    trajectories = [
        t for evs in by_traj.values() if (t := _trajectory_from_events(evs)) is not None
    ]
    trajectories.sort(key=lambda t: t.iteration)
    return aggregate(trajectories, baseline_mean_cost=baseline_mean_cost)
