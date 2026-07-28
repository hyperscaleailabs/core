"""Control API — FastAPI surface for experiments, runs, results, and observability links.

Phase-1 implementation (ASC-010/011/015): in-memory store, synchronous run execution via the
orchestrator, immutability + failure-profile validation enforced at the API boundary. Kafka-backed
SSE and Postgres persistence land in later milestones without changing these routes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

from asc_domain import ExperimentConfig, GateSet
from asc_gate_engine import evaluate_gates
from asc_kernel import HarnessMode
from asc_telemetry import (
    ArtifactStore,
    EventEmitter,
    NullArtifactStore,
    NullEmitter,
    S3ArtifactStore,
    build_emitter,
    configure_tracing,
)
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError

from asc_control_api.store import RunRecord, Store

try:  # orchestrator is a sibling service (installed editable / on PYTHONPATH)
    from asc_orchestrator import execute_run, summarize_failure_types
except ImportError:  # pragma: no cover - import guard for partial checkouts
    execute_run = None  # type: ignore[assignment]
    summarize_failure_types = None  # type: ignore[assignment]

EXAMPLES_DIR = Path(
    os.environ.get("ASC_EXAMPLES_DIR", Path(__file__).resolve().parents[4] / "examples")
)
GRAFANA_BASE = os.environ.get("GRAFANA_BASE_URL", "http://grafana.localhost:8080")
SUPERSET_BASE = os.environ.get("SUPERSET_BASE_URL", "http://superset.localhost:8080")
# operator-web calls this API cross-origin; allow its origins (comma-separated) or "*" locally.
CORS_ORIGINS = [o.strip() for o in os.environ.get("ASC_CORS_ORIGINS", "*").split(",") if o.strip()]

_HARNESSES = {h.value: h for h in HarnessMode}


def _default_gate_set() -> GateSet:
    return GateSet.model_validate(
        json.loads((EXAMPLES_DIR / "transaction_release_gates.json").read_text())
    )


def _build_emitter() -> EventEmitter:
    """Kafka emitter when KAFKA_BOOTSTRAP is set and reachable; in-memory fallback otherwise.

    Analytics is derived — a broker problem must never block a run (SYSTEM_DESIGN §14, GW-11).
    """
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP")
    if not bootstrap:
        return NullEmitter()
    try:
        return build_emitter(bootstrap=bootstrap)
    except Exception:  # noqa: BLE001 - never let telemetry setup break the API
        return NullEmitter()


def _build_artifact_store() -> ArtifactStore:
    """MinIO/S3 artifact store when configured; drop otherwise (no RAM accumulation)."""
    endpoint = os.environ.get("MINIO_ENDPOINT")
    access = os.environ.get("MINIO_ROOT_USER")
    secret = os.environ.get("MINIO_ROOT_PASSWORD")
    if not (endpoint and access and secret):
        return NullArtifactStore()
    try:
        return S3ArtifactStore.from_env(endpoint, access, secret)
    except Exception:  # noqa: BLE001 - artifact storage must not break the API
        return NullArtifactStore()


class StartRunRequest(BaseModel):
    experimentId: str
    harness: str = HarnessMode.TRANSACTION_SAFETY.value
    iterations: int | None = None


def create_app(store: Store | None = None) -> FastAPI:
    app = FastAPI(title="Agent Simulation Control API", version="0.2.0")
    app.state.store = store or Store()
    configure_tracing("control-api")
    app.state.emitter = _build_emitter()
    app.state.artifact_store = _build_artifact_store()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        return {"status": "ready"}

    # experiments -------------------------------------------------------
    @app.post("/experiments", status_code=201)
    def create_experiment(body: dict) -> dict:
        try:
            cfg = ExperimentConfig.model_validate(body)  # GW-08: bad probabilities -> 422
        except ValidationError as exc:
            # Serialize errors without the non-JSON-safe ``ctx`` (which holds the raw exception).
            detail = [
                {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()
            ]
            raise HTTPException(status_code=422, detail=detail) from exc
        rec = app.state.store.create_experiment(cfg)
        return {"id": rec.id, "status": "draft"}

    @app.post("/experiments/seed-golden", status_code=201)
    def seed_golden() -> dict:
        """Convenience for demos/console: create the Purchase Ambiguity experiment from the fixture."""
        body = json.loads((EXAMPLES_DIR / "purchase_ambiguity_experiment.json").read_text())
        rec = app.state.store.create_experiment(ExperimentConfig.model_validate(body))
        return {"id": rec.id, "name": rec.draft.experiment.name, "status": "draft"}

    @app.get("/experiments")
    def list_experiments() -> dict:
        store = app.state.store
        return {
            "experiments": [
                {
                    "id": r.id,
                    "name": r.draft.experiment.name,
                    "workflow": r.draft.experiment.workflowTemplate.value,
                    "hasCompletedRun": r.has_completed_run,
                    "runs": [rr.id for rr in store.runs.values() if rr.experiment_id == r.id],
                }
                for r in store.experiments.values()
            ]
        }

    @app.get("/experiments/{exp_id}")
    def get_experiment(exp_id: str) -> dict:
        rec = app.state.store.experiments.get(exp_id)
        if not rec:
            raise HTTPException(status_code=404, detail="experiment not found")
        return {
            "id": rec.id,
            "versions": len(rec.versions),
            "hasCompletedRun": rec.has_completed_run,
            "parentId": rec.parent_id,
            "config": rec.draft.model_dump(mode="json"),
        }

    @app.post("/experiments/{exp_id}/versions", status_code=201)
    def freeze_version(exp_id: str) -> dict:
        if exp_id not in app.state.store.experiments:
            raise HTTPException(status_code=404, detail="experiment not found")
        version = app.state.store.freeze_version(exp_id)
        return {"id": exp_id, "version": version}

    @app.patch("/experiments/{exp_id}")
    def edit_experiment(exp_id: str, body: dict) -> dict:
        rec = app.state.store.experiments.get(exp_id)
        if not rec:
            raise HTTPException(status_code=404, detail="experiment not found")
        if rec.has_completed_run:  # GW-09: completed config is immutable
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "experiment has a completed run and is immutable",
                    "cloneEndpoint": f"/experiments/{exp_id}/clone",
                },
            )
        return {"id": exp_id, "status": "editable"}

    @app.post("/experiments/{exp_id}/clone", status_code=201)
    def clone_experiment(exp_id: str) -> dict:
        if exp_id not in app.state.store.experiments:
            raise HTTPException(status_code=404, detail="experiment not found")
        rec = app.state.store.clone_experiment(exp_id)
        return {"id": rec.id, "parentId": rec.parent_id, "lineage": [rec.parent_id, rec.id]}

    # runs --------------------------------------------------------------
    @app.post("/runs", status_code=201)
    def start_run(req: StartRunRequest) -> dict:
        if execute_run is None:  # pragma: no cover
            raise HTTPException(status_code=503, detail="orchestrator unavailable")
        rec = app.state.store.experiments.get(req.experimentId)
        if not rec:
            raise HTTPException(status_code=404, detail="experiment not found")
        harness = _HARNESSES.get(req.harness)
        if harness is None:
            raise HTTPException(status_code=422, detail=f"unknown harness '{req.harness}'")

        cfg = rec.draft.model_copy(deep=True)
        if req.iterations:
            cfg.execution.iterations = req.iterations
        run_id = f"run-{req.experimentId}-{len(app.state.store.runs)}"
        result = execute_run(
            cfg,
            harness,
            _default_gate_set(),
            run_id=run_id,
            emitter=app.state.emitter,
            artifact_store=app.state.artifact_store,
        )

        run_record = RunRecord(
            id=run_id,
            experiment_id=req.experimentId,
            harness=harness.value,
            status=result.status.value,
            metrics=result.metrics,
            decision=result.decision,
            offender_trajectory_ids=result.decision.blocking_gates[0].related_trajectory_ids
            if (result.decision and result.decision.blocking_gates)
            else [],
            failure_types=summarize_failure_types(result.trajectories),
        )
        app.state.store.save_run(run_record)
        return {
            "runId": run_id,
            "status": run_record.status,
            "completed": result.completed,
            "cancelled": result.cancelled,
        }

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict:
        run = app.state.store.runs.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        return {"runId": run.id, "status": run.status, "harness": run.harness}

    @app.get("/runs/{run_id}/result")
    def get_result(run_id: str) -> dict:
        run = app.state.store.runs.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        return {
            "runId": run.id,
            "status": run.status,
            "metrics": run.metrics.model_dump(),
            "decision": run.decision.model_dump(mode="json") if run.decision else None,
        }

    @app.get("/runs/{run_id}/provisional")
    def provisional_gates(run_id: str) -> dict:
        """Provisional gate scorecard for the live monitor (ASC-034), marked provisional."""
        run = app.state.store.runs.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        gates = evaluate_gates(run.metrics, _default_gate_set(), provisional=True)
        return {"runId": run.id, "gates": [g.model_dump(mode="json") for g in gates]}

    @app.get("/runs/{run_id}/events")
    def run_events(run_id: str) -> StreamingResponse:
        """SSE stream of a run's status, failure-type breakdown, and gate results (ASC-024).

        Phase-1 replays the completed run's summary; the production bridge feeds this from
        sim.run.control.v1 + sim.failure.stats.v1 for a live monitor.
        """
        run = app.state.store.runs.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")

        def sse(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        provisional = evaluate_gates(run.metrics, _default_gate_set(), provisional=True)

        def stream():
            yield sse("status", {"runId": run.id, "status": run.status})
            for ftype, count in sorted(run.failure_types.items()):
                yield sse("failure_stat", {"failureType": ftype, "count": count})
            # Provisional gate status the live monitor shows while a run is in flight (ASC-034).
            for g in provisional:
                yield sse(
                    "provisional_gate",
                    {
                        "metric": g.metric,
                        "passed": g.passed,
                        "severity": g.severity.value,
                        "actual": g.actual_value,
                        "provisional": g.provisional,
                    },
                )
            if run.decision:
                for line in run.decision.explanations:
                    yield sse("gate", {"line": line})
            yield sse("done", {"status": run.status})

        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.get("/runs/{run_id}/result/export")
    def export_result(run_id: str) -> Response:
        run = app.state.store.runs.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        payload = {
            "runId": run.id,
            "experimentId": run.experiment_id,
            "status": run.status,
            "metrics": run.metrics.model_dump(),
            "decision": run.decision.model_dump(mode="json") if run.decision else None,
        }
        # GW-14: export is the durable artifact; served as a downloadable JSON document.
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{run_id}-result.json"'},
        )

    # observability deep links (ASC-043 consumes these) -----------------
    @app.get("/observability/links")
    def observability_links(runId: str) -> dict:
        rid = quote(runId, safe="")
        return {
            "grafana": f"{GRAFANA_BASE}/d/asc-run/run-in-progress?var-runId={rid}",
            "superset": f"{SUPERSET_BASE}/superset/dashboard/experiment-overview/?runId={rid}",
        }

    return app


app = create_app()
