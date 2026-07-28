"""ASC-043 support: seed-golden, list, and CORS endpoints the operator-web console uses."""

from __future__ import annotations

import pytest
from asc_control_api import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_seed_golden_creates_experiment(client):
    r = client.post("/experiments/seed-golden")
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert "Purchase" in body["name"]


def test_list_experiments_reflects_created(client):
    client.post("/experiments/seed-golden")
    listing = client.get("/experiments").json()["experiments"]
    assert len(listing) == 1
    assert listing[0]["workflow"] == "transactional_mcp"


def test_cors_headers_present_for_browser_origin(client):
    r = client.get("/healthz", headers={"Origin": "http://operator.localhost:8080"})
    assert r.headers.get("access-control-allow-origin") in {"*", "http://operator.localhost:8080"}


def test_console_end_to_end_seed_then_run(client):
    exp = client.post("/experiments/seed-golden").json()["id"]
    started = client.post(
        "/runs", json={"experimentId": exp, "harness": "basic_retry", "iterations": 200}
    ).json()
    result = client.get(f"/runs/{started['runId']}/result").json()
    assert result["status"] == "Blocked"
    links = client.get("/observability/links", params={"runId": started["runId"]}).json()
    assert started["runId"] in links["grafana"]
