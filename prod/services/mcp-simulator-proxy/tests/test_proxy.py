"""ASC-014: MCP proxy determinism, idempotency, and tool authorization (GW-07)."""

from __future__ import annotations

import pytest
from asc_mcp_proxy import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def _purchase(client, **body):
    return client.post("/tools/make_purchase/invoke", json=body)


def test_deterministic_outcome_for_same_seed(client):
    a = _purchase(client, seed=12345, callIndex=0).json()["status"]
    b = _purchase(client, seed=12345, callIndex=0).json()["status"]
    assert a == b


def test_idempotency_key_prevents_double_charge(client):
    first = _purchase(client, seed=999, idempotencyKey="idem-1").json()
    second = _purchase(client, seed=999, idempotencyKey="idem-1").json()
    assert second["idempotentReplay"] is True
    assert second["status"] == first["status"]


def test_gw07_scope_mismatch_is_refused_and_recorded(client):
    r = client.post(
        "/tools/check_balance/invoke",
        json={"seed": 1, "scope": "customer-A", "requiredScope": "customer-B"},
    )
    assert r.status_code == 403
    assert r.json()["detail"]["classification"] == "cross_scope_access"
    violations = client.get("/policy-violations").json()
    assert violations["count"] == 1


def test_transaction_status_reflects_committed_state(client):
    # Find a seed whose make_purchase committed (success/delay/timeout/ambiguous).
    committed_seed = next(
        s
        for s in range(1000)
        if _purchase(client, seed=s, idempotencyKey=f"k{s}").json()["committed"]
    )
    status = client.post(
        "/tools/transaction_status/invoke",
        json={"seed": committed_seed, "idempotencyKey": f"k{committed_seed}"},
    ).json()
    assert status["confirmed"] is True
    assert status["status"] == "purchase_confirmed"
