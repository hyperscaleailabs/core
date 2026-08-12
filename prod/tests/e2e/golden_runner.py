"""Simulator-as-a-check: run the Purchase Ambiguity golden workflow and emit a release decision.

Runs the unsafe (basic-retry) and safe (transaction-safety) variants end-to-end through the
kernel and gate engine, writes ``release-decision.json`` for each, and prints a summary. CI runs
this on every PR and uploads the artifacts (ASC-062, docs/design/CICD_STRATEGY.md §2).

Usage: ``python tests/e2e/golden_runner.py [--iterations N] [--out DIR]``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"

# Make the monorepo packages importable from a bare checkout, the same way conftest.py does
# for pytest. Without this the script only runs with a hand-set PYTHONPATH, which means the
# local invocation and the CI invocation are different commands - and the one people actually
# run is the one that is never exercised.
for _group in ("packages", "services", "stream"):
    for _src in sorted((ROOT / _group).glob("*/src")):
        _p = str(_src.resolve())
        if _p not in sys.path:
            sys.path.insert(0, _p)

from asc_domain import ExperimentConfig, GateSet  # noqa: E402
from asc_gate_engine import evaluate  # noqa: E402
from asc_kernel import HarnessMode, has_policy_violation, run_batch  # noqa: E402

# The unsafe variant uses the experiment's own basic-retry harness; the safe variant swaps in the
# transaction-safety harness (examples/transaction_safety_harness.json) - modeled here as the
# kernel HarnessMode. Baseline mean cost anchors cost_change_percent for the demo.
BASELINE_MEAN_COST = 0.15


def run(iterations: int, out_dir: Path) -> dict[str, str]:
    cfg = ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )
    cfg.execution.iterations = iterations
    gate_set = GateSet.model_validate(
        json.loads((EXAMPLES / "transaction_release_gates.json").read_text())
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = {
        "unsafe": HarnessMode.BASIC_RETRY,
        "safe": HarnessMode.TRANSACTION_SAFETY,
    }
    decisions: dict[str, str] = {}
    for label, mode in variants.items():
        trajs, metrics = run_batch(
            cfg, mode, run_id=f"golden-{label}", baseline_mean_cost=BASELINE_MEAN_COST
        )
        related = {
            "policy": [t.trajectoryId for t in trajs if has_policy_violation(t)][:20],
        }
        decision = evaluate(
            metrics,
            gate_set,
            related_trajectories=related,
            version_identifiers={
                "experiment": cfg.experiment.id,
                "candidate": cfg.experiment.candidateVersion or "",
                "harness": mode.value,
            },
            reproducibility={"iterations": str(iterations), "seed_base": "1000"},
        )
        artifact = out_dir / f"release-decision-{label}.json"
        artifact.write_text(
            json.dumps(
                {
                    "variant": label,
                    "harness": mode.value,
                    "metrics": metrics.model_dump(),
                    "decision": decision.model_dump(mode="json"),
                },
                indent=2,
            )
            + "\n"
        )
        decisions[label] = decision.status.value
        print(
            f"[{label:6}] {decision.status.value:22} "
            f"violations={metrics.policy_violations} "
            f"validation={metrics.validation_success_rate} "
            f"p95={metrics.p95_latency_ms}ms -> {artifact.name}"
        )
    return decisions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=1000)
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts" / "golden")
    args = ap.parse_args()
    decisions = run(args.iterations, args.out)
    # The check "passes" when the golden invariants hold: unsafe Blocked, safe not Blocked.
    ok = decisions.get("unsafe") == "Blocked" and decisions.get("safe") != "Blocked"
    print(
        f"\nGOLDEN CHECK: {'PASS' if ok else 'FAIL'} "
        f"(unsafe={decisions.get('unsafe')}, safe={decisions.get('safe')})"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
