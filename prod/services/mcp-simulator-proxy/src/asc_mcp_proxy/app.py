"""MCP simulator/proxy — MCP-compatible tools with deterministic failure injection (ASC-014).

Outcomes are sampled deterministically from the run's failure profile keyed by (seed, tool,
callIndex), so replay is stable (GW-03). Transactional tools honor idempotency keys (a repeated
key never double-charges) and expose ``transaction_status`` reflecting the true underlying state so
a safe harness can recover (GW-02). Tool authorization is enforced *here*, outside the model: a
scope mismatch is refused and recorded as a policy violation (GW-07).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from asc_domain import FailureProfile
from asc_kernel import sample_outcome, uniform
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

EXAMPLES_DIR = Path(
    os.environ.get("ASC_EXAMPLES_DIR", Path(__file__).resolve().parents[4] / "examples")
)

# Outcomes where the underlying transaction actually committed despite an unclean tool response.
_COMMITTED = {"success", "processing_delay", "timeout", "ambiguous_completion"}


def _default_purchase_profile() -> FailureProfile:
    data = json.loads((EXAMPLES_DIR / "purchase_ambiguity_experiment.json").read_text())
    return FailureProfile.model_validate(data["failureProfile"])


class InvokeRequest(BaseModel):
    seed: int
    callIndex: int = 0
    idempotencyKey: str | None = None
    scope: str | None = None
    requiredScope: str | None = None
    args: dict = {}


def create_app() -> FastAPI:
    app = FastAPI(title="MCP Simulator Proxy", version="0.2.0")
    app.state.profile = _default_purchase_profile()
    app.state.idempotency: dict[str, dict] = {}
    app.state.committed: dict[str, bool] = {}  # keyed by idempotencyKey or seed
    app.state.policy_violations: list[dict] = []

    def _authorize(tool: str, req: InvokeRequest) -> None:
        if req.requiredScope and req.scope != req.requiredScope:
            app.state.policy_violations.append(
                {"tool": tool, "classification": "cross_scope_access", "scope": req.scope}
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "tool authorization denied",
                    "classification": "cross_scope_access",
                },
            )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/tools/check_inventory/invoke")
    def check_inventory(req: InvokeRequest) -> dict:
        _authorize("check_inventory", req)
        return {"tool": "check_inventory", "status": "success", "available": True}

    @app.post("/tools/check_balance/invoke")
    def check_balance(req: InvokeRequest) -> dict:
        _authorize("check_balance", req)
        return {"tool": "check_balance", "status": "success", "sufficient": True}

    @app.post("/tools/make_purchase/invoke")
    def make_purchase(req: InvokeRequest) -> dict:
        _authorize("make_purchase", req)
        key = req.idempotencyKey or f"seed:{req.seed}"
        # Idempotency: a repeated key returns the original result (never double-charge).
        if req.idempotencyKey and req.idempotencyKey in app.state.idempotency:
            prior = dict(app.state.idempotency[req.idempotencyKey])
            prior["idempotentReplay"] = True
            return prior

        outcome = sample_outcome(
            app.state.profile, uniform(req.seed, "make_purchase", req.callIndex)
        )
        committed = outcome in _COMMITTED
        app.state.committed[key] = committed
        result = {"tool": "make_purchase", "status": outcome, "committed": committed}
        if req.idempotencyKey:
            app.state.idempotency[req.idempotencyKey] = dict(result)
        return result

    @app.post("/tools/transaction_status/invoke")
    def transaction_status(req: InvokeRequest) -> dict:
        _authorize("transaction_status", req)
        key = req.idempotencyKey or f"seed:{req.seed}"
        confirmed = app.state.committed.get(key, False)
        return {
            "tool": "transaction_status",
            "status": "purchase_confirmed" if confirmed else "no_transaction",
            "confirmed": confirmed,
        }

    @app.get("/policy-violations")
    def policy_violations() -> dict:
        return {"count": len(app.state.policy_violations), "items": app.state.policy_violations}

    return app


app = create_app()
