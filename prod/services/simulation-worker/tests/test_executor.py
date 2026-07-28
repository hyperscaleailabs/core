"""ASC-013: worker executor runs the kernel and emits redacted event envelopes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_domain import ExperimentConfig
from asc_kernel import HarnessMode
from asc_telemetry import InMemoryArtifactStore, InMemoryEmitter
from asc_worker import execute_iteration, trajectory_to_envelopes

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


@pytest.fixture
def config() -> ExperimentConfig:
    return ExperimentConfig.model_validate(
        json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())
    )


def test_execute_iteration_emits_envelopes_with_correlation_ids(config):
    emitter = InMemoryEmitter()
    traj = execute_iteration(
        config, HarnessMode.TRANSACTION_SAFETY, seed=42, run_id="r1", iteration=3, emitter=emitter
    )
    events = emitter.by_run("r1")
    assert events
    assert all(e.experimentId == config.experiment.id for e in events)
    assert all(e.iteration == 3 and e.trajectoryId == traj.trajectoryId for e in events)
    # every event in the iteration shares one traceId (end-to-end correlation)
    assert len({e.traceId for e in events}) == 1


def test_artifact_store_receives_raw_trajectory_and_stamps_ref(config):
    store = InMemoryArtifactStore()
    emitter = InMemoryEmitter()
    traj = execute_iteration(
        config,
        HarnessMode.BASIC_RETRY,
        seed=840239,
        run_id="r3",
        iteration=0,
        emitter=emitter,
        artifact_store=store,
    )
    # The full raw trajectory is persisted to the store, referenced (not inlined) on the stream.
    ref = f"memory://r3/{traj.trajectoryId}.json"
    assert store.get(ref)["trajectoryId"] == traj.trajectoryId
    events = emitter.by_run("r3")
    assert events and all(e.rawOutputRef == ref for e in events)


def test_terminal_event_carries_outcome(config):
    traj = execute_iteration(config, HarnessMode.BASIC_RETRY, seed=1, run_id="r2", iteration=0)
    envs = trajectory_to_envelopes(traj, config)
    terminal = [e for e in envs if e.eventType == "iteration_result"]
    assert len(terminal) == 1
    assert terminal[0].outcome == traj.outcome.value
