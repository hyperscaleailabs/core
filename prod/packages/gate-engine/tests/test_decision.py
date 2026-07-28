"""ASC-003: gate-engine decision rule. Covers GW-12 (severity precedence) and GW-13."""

from __future__ import annotations

import json
from pathlib import Path

from asc_domain import Gate, GateOperator, GateSet, GateSeverity, RunMetrics
from asc_gate_engine import evaluate

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def _gate(gid, metric, op, thr, sev):
    return Gate(id=gid, metric=metric, operator=op, threshold=thr, severity=sev)


def test_all_pass_is_passed():
    gs = GateSet(
        id="g",
        name="g",
        gates=[
            _gate("v", "validation_success_rate", GateOperator.GTE, 0.99, GateSeverity.BLOCKING)
        ],
    )
    m = RunMetrics(completed=100, validation_success_rate=1.0)
    assert evaluate(m, gs).status.value == "Passed"


def test_gw12_severity_precedence_is_manual_review():
    # one failed warning + one failed manual-review + no failed blocking -> Manual review
    gs = GateSet(
        id="g",
        name="g",
        gates=[
            _gate("retry", "retry_rate", GateOperator.LTE, 0.1, GateSeverity.WARNING),
            _gate("latency", "p95_latency_ms", GateOperator.LTE, 2500, GateSeverity.MANUAL_REVIEW),
            _gate("policy", "policy_violations", GateOperator.EQ, 0, GateSeverity.BLOCKING),
        ],
    )
    m = RunMetrics(completed=100, retry_rate=0.2, p95_latency_ms=3000, policy_violations=0)
    decision = evaluate(m, gs)
    assert decision.status.value == "Manual review"
    assert any(w.metric == "retry_rate" for w in decision.warnings)


def test_gw13_policy_blocks_despite_high_success():
    gs = GateSet(
        id="g",
        name="g",
        gates=[
            _gate("v", "validation_success_rate", GateOperator.GTE, 0.99, GateSeverity.BLOCKING),
            _gate("policy", "policy_violations", GateOperator.EQ, 0, GateSeverity.BLOCKING),
        ],
    )
    m = RunMetrics(completed=1000, validation_success_rate=0.999, policy_violations=1)
    assert evaluate(m, gs).status.value == "Blocked"


def test_fixture_gate_set_evaluates():
    gs = GateSet.model_validate(
        json.loads((EXAMPLES / "transaction_release_gates.json").read_text())
    )
    # A clean safe run: high validation, no policy violations, latency under threshold.
    m = RunMetrics(
        completed=1000,
        validation_success_rate=0.999,
        terminal_failure_rate=0.0,
        p95_latency_ms=2300,
        cost_change_percent=-5,
        retry_rate=0.02,
        policy_violations=0,
    )
    assert evaluate(m, gs).status.value in {"Passed", "Passed with warnings"}
