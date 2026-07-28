"""Core domain contracts for the Agent Simulation Control Plane.

These Pydantic models are the single source of truth for the four contracts that
``docs/design/IMPLEMENTATION_SPEC.md`` requires to be stabilized first:

1. Experiment configuration (versioned, immutable after a run)
2. Iteration event envelope (the Kafka / Flink / Druid contract)
3. Gate result
4. Release decision

The JSON fixtures in ``examples/`` validate against these models round-trip.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = "1"


# --------------------------------------------------------------------------- enums
class WorkflowTemplate(StrEnum):
    LINEAR = "linear_user_to_agent"  # WF-01
    HIERARCHICAL = "hierarchical_depth_one"  # WF-02
    ROUTING = "department_routing_depth_two"  # WF-03
    TRANSACTIONAL = "transactional_mcp"  # WF-04


class Outcome(StrEnum):
    SUCCESS = "success"
    RECOVERED = "recovered"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FailureClassification(StrEnum):
    NONE = "none"
    TEMPORARY_TOOL_FAILURE = "temporary_tool_failure"
    AMBIGUOUS_TRANSACTION = "ambiguous_transaction"
    DUPLICATE_TRANSACTION_RISK = "duplicate_transaction_risk"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    SERVICE_UNAVAILABLE = "temporary_service_unavailable"
    MALFORMED_RESPONSE = "malformed_response"
    AUTHORIZATION_DENIED = "authorization_denied"
    CROSS_SCOPE_ACCESS = "cross_scope_access"


class GateSeverity(StrEnum):
    WARNING = "warning"
    MANUAL_REVIEW = "manual_review"
    BLOCKING = "blocking"


class GateOperator(StrEnum):
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    LT = "lt"
    GT = "gt"


class DecisionStatus(StrEnum):
    PASSED = "Passed"
    PASSED_WITH_WARNINGS = "Passed with warnings"
    MANUAL_REVIEW = "Manual review"
    BLOCKED = "Blocked"


# ------------------------------------------------------------------ failure profile
class LatencyProfile(BaseModel):
    type: str = "percentile"
    p50Ms: int | None = None
    p95Ms: int | None = None
    p99Ms: int | None = None
    maxMs: int | None = None
    fixedMs: int | None = None


class FailureProfile(BaseModel):
    source: str = "assumed"  # assumed | imported_historical | production_learned | modified
    tool: str
    outcomes: dict[str, float]
    latency: LatencyProfile = Field(default_factory=LatencyProfile)

    @model_validator(mode="after")
    def _probabilities_total_100(self) -> FailureProfile:
        total = round(sum(self.outcomes.values()), 6)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"failure profile outcome probabilities must total 1.0 (100%); got {total}"
            )
        return self


# ------------------------------------------------------------------------- harness
class RecoveryPolicy(BaseModel):
    failureType: str
    classification: str | None = None
    action: str
    maxRetries: int = 0


class HarnessBounds(BaseModel):
    maxStageRetries: int = 2
    maxTrajectoryRetries: int = 4
    maxSteps: int = 12
    maxCostUsd: float = 0.25
    maxDurationMs: int = 15000


class Harness(BaseModel):
    schemaVersion: str = "0.1"
    id: str
    name: str
    version: str = "1.0"
    validation: dict[str, bool] = Field(default_factory=dict)
    bounds: HarnessBounds = Field(default_factory=HarnessBounds)
    recoveryPolicies: list[RecoveryPolicy] = Field(default_factory=list)


# ------------------------------------------------------------------------- gates
class Gate(BaseModel):
    id: str
    metric: str
    operator: GateOperator
    threshold: float
    severity: GateSeverity


class GateSet(BaseModel):
    schemaVersion: str = "0.1"
    id: str
    name: str
    gates: list[Gate]


class GateResult(BaseModel):
    gate_id: str
    metric: str
    scope: str = "run"
    operator: GateOperator
    actual_value: float
    threshold: float
    severity: GateSeverity
    sample_size: int
    passed: bool
    provisional: bool = False  # true while computed from partial (in-flight) run data
    related_trajectory_ids: list[str] = Field(default_factory=list)


# ----------------------------------------------------------------------- experiment
class Persona(BaseModel):
    name: str
    objective: str
    initialMessage: str | None = None
    maxTurns: int = 8
    escalation: str | None = None
    satisfaction: list[str] = Field(default_factory=list)


class AssistantAgent(BaseModel):
    name: str
    model: str
    promptVersion: str | None = None
    maxSteps: int = 12
    tools: list[str] = Field(default_factory=list)


class ExecutionSettings(BaseModel):
    iterations: int = 100
    parallelism: int = 25
    deterministicSeeds: bool = True
    cachedResources: bool = True


class ExperimentMeta(BaseModel):
    id: str
    name: str
    workflowTemplate: WorkflowTemplate
    baselineVersion: str | None = None
    candidateVersion: str | None = None
    owner: str | None = None


class ExperimentConfig(BaseModel):
    """Versioned; immutable after a completed run (enforced at the control-api boundary)."""

    schemaVersion: str = "0.1"
    experiment: ExperimentMeta
    persona: Persona
    assistant: AssistantAgent
    failureProfile: FailureProfile
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    harnessRef: str | None = None
    gateSetRef: str | None = None


# -------------------------------------------------------------- iteration + metrics
class IterationEvent(BaseModel):
    """One event within an iteration (mirrors the ``events`` array in trajectory fixtures)."""

    type: str
    tool: str | None = None
    status: str | None = None
    content: str | None = None
    classification: str | None = None
    strategy: str | None = None
    idempotencyKeyReused: bool | None = None


class Trajectory(BaseModel):
    schemaVersion: str = "0.1"
    trajectoryId: str
    runId: str
    iteration: int
    seed: int
    outcome: Outcome
    latencyMs: int = 0
    costUsd: float = 0.0
    retryCount: int = 0
    failureType: str | None = None
    events: list[IterationEvent] = Field(default_factory=list)


class RunMetrics(BaseModel):
    """Aggregated metrics consumed by the gate engine. Metric ids match gate ``metric`` fields."""

    planned: int = 0
    completed: int = 0
    successful: int = 0
    recovered: int = 0
    partial: int = 0
    failed: int = 0
    cancelled: int = 0

    validation_success_rate: float = 1.0
    terminal_failure_rate: float = 0.0
    retry_rate: float = 0.0
    retries_per_iteration: float = 0.0
    policy_violations: int = 0
    escalation_rate: float = 0.0
    anomaly_count: int = 0

    mean_cost_usd: float = 0.0
    cost_per_success_usd: float = 0.0
    cost_change_percent: float = 0.0

    mean_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    latency_change_percent: float = 0.0

    def get(self, metric: str) -> float:
        if not hasattr(self, metric):
            raise KeyError(f"unknown metric '{metric}'")
        return float(getattr(self, metric))


# ------------------------------------------------------------------ release decision
class ReleaseDecision(BaseModel):
    status: DecisionStatus
    explanations: list[str] = Field(default_factory=list)
    blocking_gates: list[GateResult] = Field(default_factory=list)
    review_gates: list[GateResult] = Field(default_factory=list)
    warnings: list[GateResult] = Field(default_factory=list)
    passed_gates: list[GateResult] = Field(default_factory=list)
    sample_size: int = 0
    version_identifiers: dict[str, str] = Field(default_factory=dict)
    reproducibility: dict[str, str] = Field(default_factory=dict)
