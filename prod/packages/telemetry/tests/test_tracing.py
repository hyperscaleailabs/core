"""ASC-022: OTel spans carry iteration correlation IDs and are traceable end-to-end."""

from __future__ import annotations

from asc_telemetry import configure_tracing, get_tracer, iteration_span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


def test_iteration_span_stamps_correlation_ids():
    exporter = InMemorySpanExporter()
    configure_tracing("test", span_processor=SimpleSpanProcessor(exporter))
    tracer = get_tracer("test")

    with iteration_span(
        tracer, "run_iteration", run_id="run-1", iteration=3, trajectory_id="traj-3", seed=9
    ):
        pass

    spans = exporter.get_finished_spans()
    assert spans, "expected at least one exported span"
    attrs = spans[-1].attributes
    assert attrs["asc.run_id"] == "run-1"
    assert attrs["asc.iteration"] == 3
    assert attrs["asc.trajectory_id"] == "traj-3"
    assert attrs["asc.seed"] == 9
