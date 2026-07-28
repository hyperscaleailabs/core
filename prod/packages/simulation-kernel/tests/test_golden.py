"""ASC-004: deterministic kernel golden behaviors (GW-01..GW-04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_domain import ExperimentConfig
from asc_kernel import HarnessMode, has_policy_violation, run_batch, run_iteration

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


@pytest.fixture
def config() -> ExperimentConfig:
    cfg = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    cfg.execution.iterations = 500
    return cfg


def test_gw01_unsafe_retry_produces_duplicate_risk(config):
    trajs, metrics = run_batch(config, HarnessMode.BASIC_RETRY, run_id="unsafe")
    assert metrics.policy_violations > 0
    # At least one trajectory shows make_purchase -> timeout -> retried make_purchase.
    offenders = [t for t in trajs if has_policy_violation(t)]
    assert offenders
    ev_types = [(e.type, e.tool, e.status) for e in offenders[0].events]
    assert ("tool_call", "make_purchase", "timeout") in ev_types or any(
        e.tool == "make_purchase" and e.status == "ambiguous_completion"
        for e in offenders[0].events
    )
    assert any(e.type == "retry" and e.idempotencyKeyReused is False for e in offenders[0].events)


def test_gw02_safe_harness_has_zero_violations(config):
    trajs, metrics = run_batch(config, HarnessMode.TRANSACTION_SAFETY, run_id="safe")
    assert metrics.policy_violations == 0
    # Ambiguous transactions are recovered, not failed.
    recovered = [t for t in trajs if t.outcome.value == "recovered"]
    assert recovered
    assert all(not has_policy_violation(t) for t in trajs)


def test_gw03_same_seed_replay_is_stable(config):
    a = run_iteration(config, HarnessMode.TRANSACTION_SAFETY, seed=777, iteration=1)
    b = run_iteration(config, HarnessMode.TRANSACTION_SAFETY, seed=777, iteration=1)
    assert a.model_dump() == b.model_dump()


def test_gw04_new_seed_may_differ(config):
    outcomes = {
        run_iteration(config, HarnessMode.BASIC_RETRY, seed=s).events[2].status
        for s in range(2000, 2400)
    }
    # Across many seeds, more than one make_purchase outcome is sampled.
    assert len(outcomes) > 1


def test_safe_run_is_fully_validated(config):
    _, metrics = run_batch(config, HarnessMode.TRANSACTION_SAFETY)
    assert metrics.validation_success_rate == pytest.approx(1.0)
    assert metrics.terminal_failure_rate == 0.0
