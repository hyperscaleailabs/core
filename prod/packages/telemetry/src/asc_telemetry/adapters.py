"""Event emitters.

- ``InMemoryEmitter`` — test/in-process double used by the golden workflow (no broker).
- ``KafkaEmitter`` — production path (ASC-021): serializes the redacted envelope and produces to
  ``sim.iteration.events.v1`` keyed by ``runId``. The Kafka client is injected (or lazily built via
  ``from_bootstrap``) so the package imports and unit-tests without a broker or client library.
"""

from __future__ import annotations

from typing import Protocol

from asc_telemetry.envelope import IterationEventEnvelope
from asc_telemetry.redaction import redact

ITERATION_EVENTS_TOPIC = "sim.iteration.events.v1"


def redact_event(event: IterationEventEnvelope) -> IterationEventEnvelope:
    """Return a copy of the envelope with structured payloads redacted (never mutates input)."""
    return event.model_copy(
        update={
            "toolInput": redact(event.toolInput) if event.toolInput else None,
            "sanitizedOutput": redact(event.sanitizedOutput) if event.sanitizedOutput else None,
            "processedOutput": redact(event.processedOutput) if event.processedOutput else None,
        }
    )


class EventEmitter(Protocol):
    def emit(self, event: IterationEventEnvelope) -> None: ...


class KafkaProducerLike(Protocol):
    def send(self, topic: str, *, key: bytes, value: bytes) -> object: ...


class NullEmitter:
    """Drops events. Used by the deployed service when no Kafka is configured, so telemetry never
    accumulates in RAM (analytics is derived and optional — the run's durable result is unaffected)."""

    def emit(self, event: IterationEventEnvelope) -> None:  # noqa: D401 - intentional no-op
        return None


class InMemoryEmitter:
    """Collects redacted events in memory (test/in-process double for the Kafka emitter)."""

    def __init__(self) -> None:
        self.events: list[IterationEventEnvelope] = []

    def emit(self, event: IterationEventEnvelope) -> None:
        self.events.append(redact_event(event))

    def by_run(self, run_id: str) -> list[IterationEventEnvelope]:
        return [e for e in self.events if e.runId == run_id]


class KafkaEmitter:
    """Produces redacted iteration events to Kafka keyed by ``runId``.

    The producer is injected (duck-typed ``send(topic, key=, value=)``, kafka-python style) so this
    is unit-testable with a fake. Use :meth:`from_bootstrap` to build a real producer at runtime.
    """

    def __init__(self, producer: KafkaProducerLike, topic: str = ITERATION_EVENTS_TOPIC) -> None:
        self._producer = producer
        self._topic = topic

    @classmethod
    def from_bootstrap(cls, bootstrap: str, topic: str = ITERATION_EVENTS_TOPIC) -> KafkaEmitter:
        try:
            from kafka import KafkaProducer  # runtime dep; provided in the service image
        except ImportError as exc:  # pragma: no cover - exercised only without the client installed
            raise RuntimeError(
                "kafka-python is required for KafkaEmitter.from_bootstrap; "
                "install it or inject a producer"
            ) from exc
        producer = KafkaProducer(
            bootstrap_servers=bootstrap.split(","),
            acks="all",
            linger_ms=20,
            retries=3,
        )
        return cls(producer, topic)

    def emit(self, event: IterationEventEnvelope) -> None:
        safe = redact_event(event)
        self._producer.send(
            self._topic,
            key=safe.kafka_key().encode(),
            value=safe.to_json().encode(),
        )


def build_emitter(
    *, bootstrap: str | None = None, producer: KafkaProducerLike | None = None
) -> EventEmitter:
    """Select an emitter: explicit producer > Kafka bootstrap > in-memory fallback."""
    if producer is not None:
        return KafkaEmitter(producer)
    if bootstrap:
        return KafkaEmitter.from_bootstrap(bootstrap)
    return InMemoryEmitter()
