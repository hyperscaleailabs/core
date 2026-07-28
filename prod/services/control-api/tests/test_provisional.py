"""ASC-034: provisional gates in the live monitor."""

from __future__ import annotations

import pytest
from asc_control_api import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def _run(client, harness: str) -> str:
    exp = client.post("/experiments/seed-golden").json()["id"]
    return client.post(
        "/runs", json={"experimentId": exp, "harness": harness, "iterations": 200}
    ).json()["runId"]


def test_provisional_endpoint_marks_gates_provisional(client):
    run_id = _run(client, "basic_retry")
    body = client.get(f"/runs/{run_id}/provisional").json()
    assert body["gates"]
    assert all(g["provisional"] is True for g in body["gates"])
    # the unsafe run's policy gate is failing provisionally
    policy = next(g for g in body["gates"] if g["metric"] == "policy_violations")
    assert policy["passed"] is False


def test_sse_includes_provisional_gate_events(client):
    run_id = _run(client, "transaction_safety")
    body = client.get(f"/runs/{run_id}/events").text
    assert "event: provisional_gate" in body
