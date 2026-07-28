"""ASC-016: in-process Purchase Ambiguity golden workflow (GW-01, GW-02, GW-14).

This is the phase-1 "definition of done" at the logic level: the same experiment produces a
Blocked run under the unsafe harness and a corrected Passed run under the transaction-safety
harness, reproducibly and without any live model or cluster.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_domain import ExperimentConfig, GateSet
from asc_gate_engine import evaluate
from asc_kernel import HarnessMode, has_policy_violation, run_batch
from asc_telemetry import redact

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"


@pytest.fixture(scope="module")
def cfg() -> ExperimentConfig:
    c = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    c.execution.iterations = 1000
    return c


@pytest.fixture(scope="module")
def gate_set() -> GateSet:
    return GateSet.model_validate(
        json.loads((EXAMPLES / "transaction_release_gates.json").read_text())
    )


def test_gw01_unsafe_run_is_blocked_with_linked_trajectory(cfg, gate_set):
    trajs, metrics = run_batch(cfg, HarnessMode.BASIC_RETRY, run_id="e2e-unsafe")
    offenders = [t.trajectoryId for t in trajs if has_policy_violation(t)]
    decision = evaluate(metrics, gate_set, related_trajectories={"policy": offenders})

    assert decision.status.value == "Blocked"
    assert metrics.policy_violations > 0
    # The blocking policy gate links to the affected trajectories (GW-01 "links to trajectories").
    policy_gate = next(g for g in decision.blocking_gates if g.metric == "policy_violations")
    assert policy_gate.related_trajectory_ids

    # A linked trajectory shows make_purchase -> ambiguous/timeout -> retried make_purchase.
    sample = next(t for t in trajs if t.trajectoryId == offenders[0])
    statuses = [(e.tool, e.status) for e in sample.events if e.tool == "make_purchase"]
    assert ("make_purchase", "timeout") in statuses or (
        "make_purchase",
        "ambiguous_completion",
    ) in statuses
    assert any(e.type == "retry" and e.idempotencyKeyReused is False for e in sample.events)


def test_gw02_safe_run_changes_decision_to_passed(cfg, gate_set):
    _, metrics = run_batch(cfg, HarnessMode.TRANSACTION_SAFETY, run_id="e2e-safe")
    decision = evaluate(metrics, gate_set)

    assert metrics.policy_violations == 0
    assert not decision.blocking_gates
    assert decision.status.value in {"Passed", "Passed with warnings"}


def test_gw02_same_seeds_distinguish_recovered_from_first_attempt(cfg):
    trajs, _ = run_batch(cfg, HarnessMode.TRANSACTION_SAFETY, run_id="e2e-safe2")
    first_attempt = [t for t in trajs if t.outcome.value == "success" and t.retryCount == 0]
    recovered = [t for t in trajs if t.outcome.value == "recovered"]
    assert first_attempt and recovered  # both classes are present and distinguishable


def test_gw14_export_matches_and_redacts(cfg, gate_set):
    _, metrics = run_batch(cfg, HarnessMode.TRANSACTION_SAFETY, run_id="e2e-export")
    decision = evaluate(metrics, gate_set)

    # Exported JSON round-trips to the same decision that would be displayed.
    exported = decision.model_dump_json()
    assert json.loads(exported)["status"] == decision.status.value

    # Sensitive fields are redacted before leaving the system.
    scrubbed = redact({"card_number": "4111111111111111", "status": decision.status.value})
    assert scrubbed["card_number"] != "4111111111111111"
    assert scrubbed["status"] == decision.status.value
