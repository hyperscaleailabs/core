"""Iteration event envelope — the single schema Kafka, Flink, and Druid agree on.

See ``docs/design/SYSTEM_DESIGN.md`` §4.2. Correlation IDs let one iteration be traced
end-to-end (experiment/run/iteration/trajectory/trace/span/session/request).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

ENVELOPE_SCHEMA_VERSION = "1"


class IterationEventEnvelope(BaseModel):
    schemaVersion: str = ENVELOPE_SCHEMA_VERSION

    # correlation
    experimentId: str
    experimentVersion: str
    runId: str
    iteration: int
    trajectoryId: str
    traceId: str
    spanId: str
    sessionId: str | None = None
    requestId: str | None = None
    seed: int
    timestamp: str  # ISO-8601 UTC

    # body
    workflowStage: str
    component: str
    eventType: str
    promptVersion: str | None = None
    model: str | None = None
    tool: str | None = None
    toolInput: dict | None = None
    sanitizedOutput: dict | None = None
    rawOutputRef: str | None = None  # pointer into object storage (MinIO); never the raw payload
    processedOutput: dict | None = None
    validationStatus: str | None = None
    failureClassification: str | None = None
    retryCount: int = 0
    tokens: int = 0
    costUsd: float = 0.0
    latencyMs: int = 0
    outcome: str | None = None

    def kafka_key(self) -> str:
        return self.runId

    def to_json(self) -> str:
        return self.model_dump_json()


class FailureStat(BaseModel):
    """Row emitted by the Flink failure-statistics job to ``sim.failure.stats.v1``."""

    schemaVersion: str = ENVELOPE_SCHEMA_VERSION
    runId: str
    failureClassification: str
    windowStart: str
    windowEnd: str
    count: int
    completed: int
    rate: float = 0.0
    p50LatencyMs: float = 0.0
    p95LatencyMs: float = 0.0
    retryRate: float = 0.0
    duplicateTransactionRisk: int = 0
    labels: dict[str, str] = Field(default_factory=dict)
