"""ASC-010/011/015: control-api behavior (GW-08, GW-09, GW-14)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from asc_control_api import create_app
from fastapi.testclient import TestClient

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


@pytest.fixture
def experiment_body() -> dict:
    return json.loads((EXAMPLES / "purchase_ambiguity_experiment.json").read_text())


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def _create(client: TestClient, body: dict) -> str:
    r = client.post("/experiments", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_health(client):
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"


def test_gw08_bad_probabilities_rejected(client, experiment_body):
    experiment_body["failureProfile"]["outcomes"]["success"] = 0.5  # now totals != 100%
    r = client.post("/experiments", json=experiment_body)
    assert r.status_code == 422


def test_start_unsafe_run_is_blocked(client, experiment_body):
    exp_id = _create(client, experiment_body)
    r = client.post(
        "/runs", json={"experimentId": exp_id, "harness": "basic_retry", "iterations": 300}
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["runId"]
    result = client.get(f"/runs/{run_id}/result").json()
    assert result["status"] == "Blocked"
    assert result["metrics"]["policy_violations"] > 0


def test_start_safe_run_passes(client, experiment_body):
    exp_id = _create(client, experiment_body)
    r = client.post(
        "/runs", json={"experimentId": exp_id, "harness": "transaction_safety", "iterations": 300}
    )
    run_id = r.json()["runId"]
    assert client.get(f"/runs/{run_id}/result").json()["status"] in {
        "Passed",
        "Passed with warnings",
    }


def test_gw09_completed_experiment_is_immutable_and_offers_clone(client, experiment_body):
    exp_id = _create(client, experiment_body)
    client.post("/runs", json={"experimentId": exp_id, "harness": "basic_retry", "iterations": 50})
    r = client.patch(f"/experiments/{exp_id}", json={"note": "tweak"})
    assert r.status_code == 409
    assert r.json()["detail"]["cloneEndpoint"].endswith("/clone")
    clone = client.post(f"/experiments/{exp_id}/clone")
    assert clone.status_code == 201
    assert clone.json()["parentId"] == exp_id


def test_gw14_export_matches_result(client, experiment_body):
    exp_id = _create(client, experiment_body)
    run_id = client.post(
        "/runs", json={"experimentId": exp_id, "harness": "transaction_safety", "iterations": 100}
    ).json()["runId"]
    displayed = client.get(f"/runs/{run_id}/result").json()
    export = client.get(f"/runs/{run_id}/result/export")
    assert export.headers["content-disposition"].endswith(f'{run_id}-result.json"')
    exported = json.loads(export.content)
    assert exported["status"] == displayed["status"]
    assert exported["decision"]["status"] == displayed["decision"]["status"]


def test_observability_links_carry_run_id(client):
    links = client.get("/observability/links", params={"runId": "run-xyz"}).json()
    assert "run-xyz" in links["grafana"]
    assert "run-xyz" in links["superset"]
