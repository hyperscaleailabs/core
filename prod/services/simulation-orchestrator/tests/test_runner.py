"""ASC-012: orchestrator run execution, decision, and Stop semantics (GW-10)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_domain import ExperimentConfig, GateSet
from asc_kernel import HarnessMode
from asc_orchestrator import RunStatus, execute_run, summarize_failure_types

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


@pytest.fixture
def config() -> ExperimentConfig:
    c = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    c.execution.iterations = 300
    return c


@pytest.fixture
def gate_set() -> GateSet:
    return GateSet.model_validate(
        json.loads((EXAMPLES / "transaction_release_gates.json").read_text())
    )


def test_unsafe_run_is_blocked(config, gate_set):
    result = execute_run(config, HarnessMode.BASIC_RETRY, gate_set, run_id="orch-unsafe")
    assert result.status == RunStatus.BLOCKED
    assert result.completed == 300
    assert result.cancelled == 0
    assert result.metrics.policy_violations > 0


def test_safe_run_passes(config, gate_set):
    result = execute_run(config, HarnessMode.TRANSACTION_SAFETY, gate_set, run_id="orch-safe")
    assert result.status in {RunStatus.PASSED, RunStatus.PASSED_WITH_WARNINGS}
    assert result.decision is not None
    assert not result.decision.blocking_gates


def test_stop_preserves_completed_and_cancels_queued(config, gate_set):
    # Stop after the first 10 iterations (GW-10).
    state = {"n": 0}

    def should_stop() -> bool:
        stop = state["n"] >= 10
        state["n"] += 1
        return stop

    result = execute_run(
        config, HarnessMode.BASIC_RETRY, gate_set, run_id="orch-stop", should_stop=should_stop
    )
    assert result.status == RunStatus.STOPPED
    assert result.completed == 10
    assert result.cancelled == 290
    assert result.metrics.planned == 300
    assert result.metrics.cancelled == 290
    # completed evidence remains queryable
    assert len(result.trajectories) == 10


def test_failure_type_summary_shape(config, gate_set):
    result = execute_run(config, HarnessMode.BASIC_RETRY, gate_set, run_id="orch-sum")
    counts = summarize_failure_types(result.trajectories)
    assert sum(counts.values()) == result.completed
    assert "duplicate_transaction_risk" in counts
