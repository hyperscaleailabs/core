"""ASC-002: the golden fixtures in examples/ must validate against the domain models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_domain import (
    ExperimentConfig,
    FailureProfile,
    GateSet,
    Harness,
    Trajectory,
)

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def _load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())


def test_experiment_fixture_round_trips():
    cfg = ExperimentConfig.model_validate(_load("purchase_ambiguity_experiment.json"))
    assert cfg.experiment.workflowTemplate.value == "transactional_mcp"
    assert "make_purchase" in cfg.assistant.tools
    # round-trip
    assert ExperimentConfig.model_validate(json.loads(cfg.model_dump_json())) == cfg


def test_gate_set_fixture_round_trips():
    gs = GateSet.model_validate(_load("transaction_release_gates.json"))
    metrics = {g.metric for g in gs.gates}
    assert "policy_violations" in metrics
    assert "validation_success_rate" in metrics


def test_harness_fixture_round_trips():
    h = Harness.model_validate(_load("transaction_safety_harness.json"))
    actions = {p.action for p in h.recoveryPolicies}
    assert "query_transaction_status" in actions


@pytest.mark.parametrize(
    "name", ["failed_purchase_trajectory.json", "recovered_purchase_trajectory.json"]
)
def test_trajectory_fixtures_round_trip(name):
    traj = Trajectory.model_validate(_load(name))
    assert traj.events
    assert traj.outcome.value in {"failed", "recovered"}


def test_failure_profile_rejects_bad_probabilities():
    with pytest.raises(ValueError):
        FailureProfile(tool="make_purchase", outcomes={"success": 0.5, "timeout": 0.4})
