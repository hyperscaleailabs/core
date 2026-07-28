"""Simulation worker: execute one iteration via the kernel and emit the event envelope.

This is the library form of the worker (ASC-013). In the deployed topology it is a long-running
consumer that pulls iteration jobs and emits to Kafka; here the same ``execute_iteration`` is
callable in-process so the orchestrator and control-api can run without a broker. The Kafka
emitter is swapped in for ASC-021 without changing this contract.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from asc_domain import ExperimentConfig, Trajectory
from asc_kernel import HarnessMode, run_iteration
from asc_telemetry import (
    ArtifactStore,
    EventEmitter,
    IterationEventEnvelope,
    get_tracer,
    iteration_span,
)

_TRACER = get_tracer("simulation-worker")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def trajectory_to_envelopes(
    traj: Trajectory,
    config: ExperimentConfig,
    *,
    trace_id: str | None = None,
    raw_output_ref: str | None = None,
) -> list[IterationEventEnvelope]:
    """Project a trajectory's events onto the iteration event envelope contract.

    ``raw_output_ref`` (a pointer into object storage) is stamped on each event; the raw payload
    itself stays in the artifact store, never on the stream.
    """
    trace_id = trace_id or uuid.uuid4().hex
    envelopes: list[IterationEventEnvelope] = []
    for i, ev in enumerate(traj.events):
        envelopes.append(
            IterationEventEnvelope(
                experimentId=config.experiment.id,
                experimentVersion=config.experiment.candidateVersion or "candidate",
                runId=traj.runId,
                iteration=traj.iteration,
                trajectoryId=traj.trajectoryId,
                traceId=trace_id,
                spanId=f"{trace_id}-{i}",
                seed=traj.seed,
                timestamp=_now_iso(),
                workflowStage=config.experiment.workflowTemplate.value,
                component="simulation-worker",
                eventType=ev.type,
                model=config.assistant.model,
                promptVersion=config.assistant.promptVersion,
                tool=ev.tool,
                sanitizedOutput={"status": ev.status} if ev.status else None,
                rawOutputRef=raw_output_ref,
                failureClassification=ev.classification,
                retryCount=traj.retryCount,
                costUsd=traj.costUsd,
                latencyMs=traj.latencyMs,
                outcome=traj.outcome.value if ev.type == "iteration_result" else None,
            )
        )
    return envelopes


def execute_iteration(
    config: ExperimentConfig,
    harness: HarnessMode,
    seed: int,
    *,
    run_id: str,
    iteration: int,
    emitter: EventEmitter | None = None,
    artifact_store: ArtifactStore | None = None,
) -> Trajectory:
    """Run one iteration (traced); store the raw trajectory and emit its event envelopes.

    When an ``artifact_store`` is provided, the full trajectory is persisted to object storage and
    referenced from the stream via ``rawOutputRef`` (the raw payload never rides the stream).
    """
    traj = run_iteration(config, harness, seed=seed, run_id=run_id, iteration=iteration)
    with iteration_span(
        _TRACER,
        "run_iteration",
        run_id=run_id,
        iteration=iteration,
        trajectory_id=traj.trajectoryId,
        seed=seed,
        outcome=traj.outcome.value,
        harness=harness.value,
    ):
        raw_ref = None
        if artifact_store is not None:
            raw_ref = artifact_store.put_trajectory(run_id, traj.trajectoryId, traj.model_dump())
        if emitter is not None:
            for env in trajectory_to_envelopes(traj, config, raw_output_ref=raw_ref):
                emitter.emit(env)
    return traj
