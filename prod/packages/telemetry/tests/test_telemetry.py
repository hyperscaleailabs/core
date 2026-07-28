"""ASC-005: envelope serialization + redaction."""

from __future__ import annotations

from asc_telemetry import (
    REDACTED,
    InMemoryEmitter,
    IterationEventEnvelope,
    redact,
)


def _envelope(**over) -> IterationEventEnvelope:
    base = {
        "experimentId": "exp-1",
        "experimentVersion": "v1",
        "runId": "run-1",
        "iteration": 1,
        "trajectoryId": "traj-1",
        "traceId": "trace-1",
        "spanId": "span-1",
        "seed": 42,
        "timestamp": "2026-07-24T00:00:00Z",
        "workflowStage": "transaction",
        "component": "worker",
        "eventType": "tool_call",
    }
    base.update(over)
    return IterationEventEnvelope(**base)


def test_envelope_serializes_and_keys_by_run():
    env = _envelope(tool="make_purchase")
    assert env.kafka_key() == "run-1"
    assert '"schemaVersion":"1"' in env.to_json()


def test_redaction_drops_sensitive_keys_and_patterns():
    payload = {
        "password": "hunter2",
        "note": "card 4111111111111111 for user",
        "nested": {"api_key": "sk_live_abcdefghijklmnop123456"},
        "ssn": "123-45-6789",
    }
    out = redact(payload)
    assert out["password"] == REDACTED
    assert REDACTED in out["note"]
    assert out["nested"]["api_key"] == REDACTED
    assert out["ssn"] == REDACTED


def test_emitter_redacts_structured_payloads():
    emitter = InMemoryEmitter()
    emitter.emit(_envelope(tool="make_purchase", toolInput={"password": "x", "amount": 10}))
    got = emitter.by_run("run-1")
    assert len(got) == 1
    assert got[0].toolInput["password"] == REDACTED
    assert got[0].toolInput["amount"] == 10
