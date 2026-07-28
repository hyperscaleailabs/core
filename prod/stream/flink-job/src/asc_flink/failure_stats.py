"""Reference implementation of the failure-type statistics the Flink job computes.

The deployed job is Flink SQL over ``sim.iteration.events.v1`` (see ``sql/failure_stats.sql``).
This pure-Python function computes the same aggregation so the logic is unit-testable without a
cluster and so the two paths can be checked against each other: keyed by
``(runId, failureClassification)`` it emits :class:`FailureStat` rows to ``sim.failure.stats.v1``.
"""

from __future__ import annotations

from collections import defaultdict

from asc_telemetry import FailureStat, IterationEventEnvelope


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) - 1))))
    return float(ordered[idx])


def compute_failure_stats(
    events: list[IterationEventEnvelope],
    *,
    window_start: str = "",
    window_end: str = "",
) -> list[FailureStat]:
    """Aggregate iteration events into failure-type statistics for one window.

    Counts every event that carries a ``failureClassification`` (failure_classification and
    policy_violation events), keyed by ``(runId, failureClassification)``. Rate is normalized by
    the number of completed iterations in the run (``iteration_result`` events). Latency and retry
    are attributed via the classified event's trajectory.
    """
    # Per-trajectory latency/retry from the terminal iteration_result event.
    traj_latency: dict[str, float] = {}
    traj_retries: dict[str, int] = {}
    completed_per_run: dict[str, int] = defaultdict(int)
    for e in events:
        if e.eventType == "iteration_result":
            traj_latency[e.trajectoryId] = float(e.latencyMs)
            traj_retries[e.trajectoryId] = e.retryCount
            completed_per_run[e.runId] += 1

    # Group classified events by (runId, classification).
    grouped: dict[tuple[str, str], list[IterationEventEnvelope]] = defaultdict(list)
    for e in events:
        if e.failureClassification:
            grouped[(e.runId, e.failureClassification)].append(e)

    rows: list[FailureStat] = []
    for (run_id, classification), evs in sorted(grouped.items()):
        latencies = [traj_latency.get(e.trajectoryId, 0.0) for e in evs]
        retried = sum(1 for e in evs if traj_retries.get(e.trajectoryId, 0) > 0)
        completed = completed_per_run.get(run_id, 0)
        count = len(evs)
        rows.append(
            FailureStat(
                runId=run_id,
                failureClassification=classification,
                windowStart=window_start,
                windowEnd=window_end,
                count=count,
                completed=completed,
                rate=round(count / completed, 6) if completed else 0.0,
                p50LatencyMs=_percentile(latencies, 50),
                p95LatencyMs=_percentile(latencies, 95),
                retryRate=round(retried / count, 6) if count else 0.0,
                duplicateTransactionRisk=count
                if classification == "duplicate_transaction_risk"
                else 0,
            )
        )
    return rows
