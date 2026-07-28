"""ASC-021: KafkaEmitter serialization/redaction with an injected fake producer."""

from __future__ import annotations

import json

from asc_telemetry import (
    ITERATION_EVENTS_TOPIC,
    InMemoryEmitter,
    IterationEventEnvelope,
    KafkaEmitter,
    build_emitter,
)


class FakeProducer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, bytes, bytes]] = []

    def send(self, topic: str, *, key: bytes, value: bytes):
        self.sent.append((topic, key, value))
        return None


def _envelope(**over) -> IterationEventEnvelope:
    base = {
        "experimentId": "exp-1",
        "experimentVersion": "v1",
        "runId": "run-42",
        "iteration": 7,
        "trajectoryId": "traj-7",
        "traceId": "trace-1",
        "spanId": "span-1",
        "seed": 5,
        "timestamp": "2026-07-25T00:00:00Z",
        "workflowStage": "transactional_mcp",
        "component": "worker",
        "eventType": "tool_call",
    }
    base.update(over)
    return IterationEventEnvelope(**base)


def test_kafka_emitter_produces_keyed_redacted_json():
    producer = FakeProducer()
    emitter = KafkaEmitter(producer)
    emitter.emit(_envelope(tool="make_purchase", toolInput={"password": "x", "amount": 10}))

    assert len(producer.sent) == 1
    topic, key, value = producer.sent[0]
    assert topic == ITERATION_EVENTS_TOPIC
    assert key == b"run-42"
    payload = json.loads(value.decode())
    assert payload["runId"] == "run-42"
    assert payload["toolInput"]["password"] == "[REDACTED]"  # redacted before emit
    assert payload["toolInput"]["amount"] == 10


def test_build_emitter_selection():
    producer = FakeProducer()
    assert isinstance(build_emitter(producer=producer), KafkaEmitter)
    assert isinstance(build_emitter(), InMemoryEmitter)
    assert isinstance(build_emitter(bootstrap=""), InMemoryEmitter)
