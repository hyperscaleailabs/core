"""OpenTelemetry tracing helpers (ASC-022).

Provides a configured tracer and a context manager that stamps iteration correlation IDs
(``runId``/``iteration``/``trajectoryId``/``seed``) onto spans so one iteration is traceable
end-to-end. Exporter selection is env-driven; tests use an in-memory exporter.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanProcessor

_CONFIGURED = False


def configure_tracing(
    service_name: str = "asc",
    *,
    span_processor: SpanProcessor | None = None,
) -> None:
    """Ensure a global TracerProvider exists and attach span processors.

    OpenTelemetry allows the global provider to be set only once, so this reuses an existing real
    provider and *adds* processors to it (rather than replacing it). ``span_processor`` (tests) is
    always attached; otherwise OTLP is attached once when ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set.
    """
    global _CONFIGURED
    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        provider = current
    else:
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        trace.set_tracer_provider(provider)

    if span_processor is not None:
        provider.add_span_processor(span_processor)
    elif not _CONFIGURED and os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):  # pragma: no cover
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        except ImportError:
            # OTLP exporter not installed - tracing stays local rather than breaking startup.
            pass
    _CONFIGURED = True


def get_tracer(name: str = "asc"):
    return trace.get_tracer(name)


@contextmanager
def iteration_span(
    tracer,
    name: str,
    *,
    run_id: str,
    iteration: int,
    trajectory_id: str,
    seed: int,
    **attrs: object,
) -> Iterator[trace.Span]:
    """Start a span carrying the iteration correlation IDs (SYSTEM_DESIGN §10 / Milestone 3)."""
    with tracer.start_as_current_span(name) as span:
        span.set_attribute("asc.run_id", run_id)
        span.set_attribute("asc.iteration", iteration)
        span.set_attribute("asc.trajectory_id", trajectory_id)
        span.set_attribute("asc.seed", seed)
        for k, v in attrs.items():
            span.set_attribute(f"asc.{k}", v)  # type: ignore[arg-type]
        yield span
