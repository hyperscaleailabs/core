"""ASC-017 / GW-11: the aggregation fallback agrees with the kernel's aggregation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_aggregation import aggregate_envelopes
from asc_domain import ExperimentConfig
from asc_kernel import HarnessMode, run_batch
from asc_worker import trajectory_to_envelopes

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def _run(harness: HarnessMode):
    cfg = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    cfg.execution.iterations = 400
    trajs, metrics = run_batch(cfg, harness, run_id="agg")
    envelopes = []
    for t in trajs:
        envelopes.extend(trajectory_to_envelopes(t, cfg))
    return metrics, envelopes


@pytest.mark.parametrize("harness", [HarnessMode.BASIC_RETRY, HarnessMode.TRANSACTION_SAFETY])
def test_stream_aggregation_matches_kernel(harness):
    kernel_metrics, envelopes = _run(harness)
    stream_metrics = aggregate_envelopes(envelopes)
    # The two aggregation paths must agree on the durable metric set (GW-11).
    assert stream_metrics.completed == kernel_metrics.completed
    assert stream_metrics.successful == kernel_metrics.successful
    assert stream_metrics.recovered == kernel_metrics.recovered
    assert stream_metrics.failed == kernel_metrics.failed
    assert stream_metrics.policy_violations == kernel_metrics.policy_violations
    assert stream_metrics.validation_success_rate == kernel_metrics.validation_success_rate


def test_incomplete_iterations_are_skipped():
    _, envelopes = _run(HarnessMode.BASIC_RETRY)
    # Drop all terminal events for one trajectory -> that iteration is not counted yet.
    victim = envelopes[0].trajectoryId
    partial = [
        e for e in envelopes if not (e.trajectoryId == victim and e.eventType == "iteration_result")
    ]
    full = aggregate_envelopes(envelopes)
    reduced = aggregate_envelopes(partial)
    assert reduced.completed == full.completed - 1
