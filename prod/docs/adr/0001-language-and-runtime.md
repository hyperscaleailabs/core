# ADR-0001: Python 3.12 for backend services and shared libraries

**Status:** Accepted · **Date:** 2026-07-24

## Context
The v0.1.0 handoff leaves the implementation language open. The repo already carries `.ruff_cache`
and `.pytest_cache` (Python tooling). The simulation kernel, telemetry, gate engine, and MCP proxy
are logic-heavy and benefit from a fast iteration language with strong data-validation and async
messaging libraries. PyFlink and Druid/Superset ecosystems are Python-friendly.

## Decision
Use **Python 3.12** for all backend services (`services/*`) and shared libraries (`packages/*`):
FastAPI + Uvicorn, SQLAlchemy 2 + Alembic, Pydantic v2, aiokafka, OpenTelemetry SDK. The operator
web app remains the existing static HTML served by nginx for phase 1.

## Consequences
- One language across kernel, services, tests, and the Flink job's Python parts → shared domain
  models, less duplication.
- Type safety via Pydantic + mypy (strict on `packages/`).
- CPU-bound simulation at very large scale may later need worker parallelism / native extensions;
  acceptable for phase-1 targets (100+ concurrent iterations).
