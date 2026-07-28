"""ASC-024: SSE run event stream."""

from __future__ import annotations

import pytest
from asc_control_api import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_run_events_stream_contains_status_failures_and_done(client):
    exp = client.post("/experiments/seed-golden").json()["id"]
    run_id = client.post(
        "/runs", json={"experimentId": exp, "harness": "basic_retry", "iterations": 200}
    ).json()["runId"]

    body = client.get(f"/runs/{run_id}/events").text
    assert "event: status" in body
    assert "event: done" in body
    assert "Blocked" in body
    # unsafe run surfaces the duplicate-transaction-risk failure type in the stream
    assert "duplicate_transaction_risk" in body


def test_run_events_404_for_unknown_run(client):
    assert client.get("/runs/does-not-exist/events").status_code == 404
