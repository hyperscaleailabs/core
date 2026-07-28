"""Deterministic gate evaluation and release-decision rule.

Pure function: ``evaluate(metrics, gate_set) -> ReleaseDecision``. No I/O, no globals.
Implements the decision precedence in ``docs/design/SYSTEM_DESIGN.md`` §5 and the golden
behaviors GW-12 (severity precedence) and GW-13 (policy blocks despite high success).
"""

from __future__ import annotations

from asc_domain import (
    DecisionStatus,
    GateOperator,
    GateResult,
    GateSet,
    GateSeverity,
    ReleaseDecision,
    RunMetrics,
)

_OPS = {
    GateOperator.GTE: lambda a, t: a >= t,
    GateOperator.LTE: lambda a, t: a <= t,
    GateOperator.EQ: lambda a, t: a == t,
    GateOperator.LT: lambda a, t: a < t,
    GateOperator.GT: lambda a, t: a > t,
}


def _passes(actual: float, operator: GateOperator, threshold: float) -> bool:
    return bool(_OPS[operator](actual, threshold))


def evaluate_gates(
    metrics: RunMetrics,
    gate_set: GateSet,
    *,
    related_trajectories: dict[str, list[str]] | None = None,
    provisional: bool = False,
) -> list[GateResult]:
    """Evaluate each gate into a GateResult. When ``provisional`` (in-flight run data), results are
    marked provisional so the live monitor can distinguish them from the final decision (ASC-034)."""
    related_trajectories = related_trajectories or {}
    sample_size = metrics.completed or metrics.planned
    results: list[GateResult] = []
    for gate in gate_set.gates:
        actual = metrics.get(gate.metric)
        results.append(
            GateResult(
                gate_id=gate.id,
                metric=gate.metric,
                operator=gate.operator,
                actual_value=actual,
                threshold=gate.threshold,
                severity=gate.severity,
                sample_size=sample_size,
                passed=_passes(actual, gate.operator, gate.threshold),
                provisional=provisional,
                related_trajectory_ids=related_trajectories.get(gate.id, []),
            )
        )
    return results


def evaluate(
    metrics: RunMetrics,
    gate_set: GateSet,
    *,
    related_trajectories: dict[str, list[str]] | None = None,
    version_identifiers: dict[str, str] | None = None,
    reproducibility: dict[str, str] | None = None,
) -> ReleaseDecision:
    """Evaluate every gate and produce an explainable release decision.

    ``related_trajectories`` maps a gate id to the trajectory ids that evidence its failure.
    """
    sample_size = metrics.completed or metrics.planned
    results = evaluate_gates(metrics, gate_set, related_trajectories=related_trajectories)

    failed = [r for r in results if not r.passed]
    passed_gates = [r for r in results if r.passed]
    blocking = [r for r in failed if r.severity == GateSeverity.BLOCKING]
    review = [r for r in failed if r.severity == GateSeverity.MANUAL_REVIEW]
    warnings = [r for r in failed if r.severity == GateSeverity.WARNING]

    # Decision precedence: blocking > manual_review > warning > pass (GW-12, GW-13).
    if blocking:
        status = DecisionStatus.BLOCKED
    elif review:
        status = DecisionStatus.MANUAL_REVIEW
    elif warnings:
        status = DecisionStatus.PASSED_WITH_WARNINGS
    else:
        status = DecisionStatus.PASSED

    explanations = [
        f"[{r.severity.value}] {r.metric} = {r.actual_value:g} "
        f"{'PASS' if r.passed else 'FAIL'} (threshold {r.operator.value} {r.threshold:g})"
        for r in results
    ]

    return ReleaseDecision(
        status=status,
        explanations=explanations,
        blocking_gates=blocking,
        review_gates=review,
        warnings=warnings,
        passed_gates=passed_gates,
        sample_size=sample_size,
        version_identifiers=version_identifiers or {},
        reproducibility=reproducibility or {},
    )
