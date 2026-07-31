"""Deterministic simulation kernel.

Executes the WF-04 transactional-MCP workflow (the Purchase Ambiguity golden path) with seeded,
replayable dependency outcomes and produces a :class:`Trajectory` plus aggregated
:class:`RunMetrics`. No live LLM is involved - the ``AgentRuntimeAdapter`` boundary is the
deterministic simulator for this phase (ADR-0006).
"""

from __future__ import annotations

from asc_domain import (
    ExperimentConfig,
    FailureProfile,
    IterationEvent,
    Outcome,
    RunMetrics,
    Trajectory,
)

from asc_kernel.harness import (
    CHECK_INVENTORY_MS,
    COST_CHECK_INVENTORY,
    COST_MAKE_PURCHASE,
    COST_TRANSACTION_STATUS,
    MAKE_PURCHASE_MS,
    TRANSACTION_STATUS_MS,
    HarnessMode,
)
from asc_kernel.rng import uniform

# Outcomes where the underlying transaction actually completed even though the tool did not
# return a clean confirmation - the source of duplicate-transaction risk if retried blindly.
_AMBIGUOUS_BUT_COMMITTED = {"timeout", "ambiguous_completion"}


def sample_outcome(profile: FailureProfile, u: float) -> str:
    """Pick a mutually exclusive outcome from the profile given a uniform sample ``u``."""
    cumulative = 0.0
    last = ""
    for name, prob in profile.outcomes.items():
        last = name
        cumulative += prob
        if u < cumulative:
            return name
    return last


def run_iteration(
    config: ExperimentConfig,
    harness: HarnessMode,
    seed: int,
    *,
    run_id: str = "run-local",
    iteration: int = 0,
) -> Trajectory:
    """Execute one deterministic WF-04 iteration and return its trajectory."""
    profile = config.failureProfile
    events: list[IterationEvent] = [
        IterationEvent(type="persona_message", content=config.persona.initialMessage)
    ]
    latency = 0
    cost = 0.0
    retries = 0
    outcome = Outcome.SUCCESS
    failure_type: str | None = None

    # Stage 1 - inventory check (deterministically succeeds for the golden path).
    events.append(IterationEvent(type="tool_call", tool="check_inventory", status="success"))
    latency += CHECK_INVENTORY_MS
    cost += COST_CHECK_INVENTORY

    # Stage 2 - make_purchase, outcome sampled from the failure profile.
    mp = sample_outcome(profile, uniform(seed, "make_purchase", 0))
    events.append(IterationEvent(type="tool_call", tool="make_purchase", status=mp))
    latency += MAKE_PURCHASE_MS.get(mp, 350)
    cost += COST_MAKE_PURCHASE

    if mp == "success":
        outcome = Outcome.SUCCESS
    elif mp == "insufficient_funds":
        # Correctly-handled business outcome: agent informs the user. Reliable, not a failure.
        events.append(
            IterationEvent(type="failure_classification", classification="insufficient_funds")
        )
        events.append(IterationEvent(type="recovery", strategy="inform_user"))
        failure_type = "insufficient_funds"
        outcome = Outcome.SUCCESS
    elif mp == "processing_delay":
        failure_type = "processing_delay"
        outcome = Outcome.SUCCESS
    elif mp == "malformed_response":
        events.append(
            IterationEvent(type="failure_classification", classification="malformed_response")
        )
        events.append(IterationEvent(type="recovery", strategy="normalize_and_repair"))
        events.append(IterationEvent(type="final_validation", status="passed"))
        failure_type = "malformed_response"
        outcome = Outcome.SUCCESS
    elif mp in _AMBIGUOUS_BUT_COMMITTED:
        if harness == HarnessMode.BASIC_RETRY:
            # Unsafe: classify as a plain temporary failure and retry with a NEW idempotency key.
            events.append(
                IterationEvent(
                    type="failure_classification", classification="temporary_tool_failure"
                )
            )
            retries += 1
            events.append(
                IterationEvent(type="retry", tool="make_purchase", idempotencyKeyReused=False)
            )
            latency += MAKE_PURCHASE_MS["success"]
            cost += COST_MAKE_PURCHASE
            # The original transaction had committed → the retry double-charges.
            events.append(
                IterationEvent(type="policy_violation", classification="duplicate_transaction_risk")
            )
            failure_type = "duplicate_transaction_risk"
            outcome = Outcome.FAILED
        else:
            # Safe: treat as ambiguous, verify via transaction_status before any repeat.
            events.append(
                IterationEvent(
                    type="failure_classification", classification="ambiguous_transaction"
                )
            )
            events.append(IterationEvent(type="recovery", strategy="query_transaction_status"))
            events.append(
                IterationEvent(
                    type="tool_call", tool="transaction_status", status="purchase_confirmed"
                )
            )
            latency += TRANSACTION_STATUS_MS
            cost += COST_TRANSACTION_STATUS
            events.append(IterationEvent(type="final_validation", status="passed"))
            failure_type = "ambiguous_transaction"
            outcome = Outcome.RECOVERED
    elif mp == "service_unavailable":
        # Underlying transaction did NOT commit; a bounded retry recovers. The safe harness reuses
        # the idempotency key; basic retry uses a fresh one but there is no duplicate risk here.
        reuse = harness == HarnessMode.TRANSACTION_SAFETY
        events.append(
            IterationEvent(
                type="failure_classification", classification="temporary_service_unavailable"
            )
        )
        retries += 1
        events.append(
            IterationEvent(type="retry", tool="make_purchase", idempotencyKeyReused=reuse)
        )
        latency += MAKE_PURCHASE_MS["success"]
        cost += COST_MAKE_PURCHASE
        failure_type = "temporary_service_unavailable"
        outcome = Outcome.RECOVERED

    events.append(IterationEvent(type="iteration_result", status=outcome.value))

    return Trajectory(
        trajectoryId=f"{run_id}-{iteration}",
        runId=run_id,
        iteration=iteration,
        seed=seed,
        outcome=outcome,
        latencyMs=latency,
        costUsd=round(cost, 4),
        retryCount=retries,
        failureType=failure_type,
        events=events,
    )


def has_policy_violation(traj: Trajectory) -> bool:
    return any(e.type == "policy_violation" for e in traj.events)


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) - 1))))
    return float(ordered[idx])


def aggregate(
    trajectories: list[Trajectory], *, baseline_mean_cost: float | None = None
) -> RunMetrics:
    """Aggregate trajectories into gate-ready metrics (SYSTEM_DESIGN §2/§10.6)."""
    n = len(trajectories)
    if n == 0:
        return RunMetrics()

    successful = sum(1 for t in trajectories if t.outcome == Outcome.SUCCESS)
    recovered = sum(1 for t in trajectories if t.outcome == Outcome.RECOVERED)
    failed = sum(1 for t in trajectories if t.outcome == Outcome.FAILED)
    cancelled = sum(1 for t in trajectories if t.outcome == Outcome.CANCELLED)
    violations = sum(1 for t in trajectories if has_policy_violation(t))
    with_retry = sum(1 for t in trajectories if t.retryCount > 0)
    total_retries = sum(t.retryCount for t in trajectories)
    latencies = [float(t.latencyMs) for t in trajectories]
    costs = [t.costUsd for t in trajectories]
    mean_cost = sum(costs) / n
    validated = successful + recovered

    cost_change = 0.0
    if baseline_mean_cost:
        cost_change = round((mean_cost - baseline_mean_cost) / baseline_mean_cost * 100.0, 3)

    return RunMetrics(
        planned=n,
        completed=n,
        successful=successful,
        recovered=recovered,
        failed=failed,
        cancelled=cancelled,
        validation_success_rate=round(validated / n, 6),
        terminal_failure_rate=round(failed / n, 6),
        retry_rate=round(with_retry / n, 6),
        retries_per_iteration=round(total_retries / n, 6),
        policy_violations=violations,
        mean_cost_usd=round(mean_cost, 6),
        cost_per_success_usd=round(sum(costs) / validated, 6) if validated else 0.0,
        cost_change_percent=cost_change,
        mean_latency_ms=round(sum(latencies) / n, 3),
        p50_latency_ms=_percentile(latencies, 50),
        p95_latency_ms=_percentile(latencies, 95),
        p99_latency_ms=_percentile(latencies, 99),
    )


def run_batch(
    config: ExperimentConfig,
    harness: HarnessMode,
    *,
    run_id: str = "run-local",
    seed_base: int = 1_000,
    baseline_mean_cost: float | None = None,
) -> tuple[list[Trajectory], RunMetrics]:
    """Run ``config.execution.iterations`` deterministic iterations and aggregate them."""
    trajectories = [
        run_iteration(config, harness, seed=seed_base + i, run_id=run_id, iteration=i)
        for i in range(config.execution.iterations)
    ]
    return trajectories, aggregate(trajectories, baseline_mean_cost=baseline_mean_cost)
