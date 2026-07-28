"""ASC-030: failure-type statistics reference logic against golden-run events.

Asserts the headline acceptance: during the golden run the failure stats show a non-zero
duplicate_transaction_risk count for the unsafe config and zero for the safe config.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "stream" / "flink-job" / "pyflink"))

from asc_domain import ExperimentConfig  # noqa: E402
from asc_flink import compute_failure_stats  # noqa: E402
from asc_kernel import HarnessMode, run_batch  # noqa: E402
from asc_worker import trajectory_to_envelopes  # noqa: E402

EXAMPLES = ROOT / "examples"


def _events(harness: HarnessMode):
    cfg = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    cfg.execution.iterations = 500
    trajs, _ = run_batch(cfg, harness, run_id=f"fs-{harness.value}")
    events = []
    for t in trajs:
        events.extend(trajectory_to_envelopes(t, cfg))
    return events


def test_unsafe_run_reports_duplicate_transaction_risk():
    stats = compute_failure_stats(
        _events(HarnessMode.BASIC_RETRY), window_start="w0", window_end="w1"
    )
    dup = [s for s in stats if s.failureClassification == "duplicate_transaction_risk"]
    assert dup and dup[0].duplicateTransactionRisk > 0
    assert dup[0].count > 0
    assert dup[0].completed == 500


def test_safe_run_has_no_duplicate_transaction_risk():
    stats = compute_failure_stats(_events(HarnessMode.TRANSACTION_SAFETY))
    dup = [s for s in stats if s.failureClassification == "duplicate_transaction_risk"]
    assert dup == []
    # The safe run still reports ambiguous_transaction recoveries as a failure type.
    assert any(s.failureClassification == "ambiguous_transaction" for s in stats)


def test_rates_are_normalized_by_completed():
    stats = compute_failure_stats(_events(HarnessMode.BASIC_RETRY))
    for s in stats:
        assert 0.0 <= s.rate <= 1.0
        assert 0.0 <= s.retryRate <= 1.0


def test_pyflink_statement_loader_splits_sql():
    from job import load_statements

    stmts = load_statements("kafka:9092")
    kinds = [s.split()[0].upper() for s in stmts]
    assert kinds.count("CREATE") == 2
    assert "INSERT" in kinds
    assert all("${KAFKA_BOOTSTRAP}" not in s for s in stmts)
    assert all("kafka:9092" in s for s in stmts if "connector" in s)
