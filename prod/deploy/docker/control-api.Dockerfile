# control-api image (ASC-007). Build context = repo root:
#   docker build -f deploy/docker/control-api.Dockerfile -t control-api:dev .
# Ships the orchestrator + worker in-process for phase 1 (split out when Kafka lands, ASC-021).
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29" "pydantic>=2.6" \
    "opentelemetry-sdk>=1.20" "opentelemetry-exporter-otlp-proto-grpc>=1.20" \
    "kafka-python>=2.0" "boto3>=1.34"

COPY packages ./packages
COPY services/simulation-worker ./services/simulation-worker
COPY services/simulation-orchestrator ./services/simulation-orchestrator
COPY services/control-api ./services/control-api
COPY examples ./examples

ENV PYTHONPATH=/app/packages/domain/src:/app/packages/telemetry/src:/app/packages/gate-engine/src:/app/packages/simulation-kernel/src:/app/services/simulation-worker/src:/app/services/simulation-orchestrator/src:/app/services/control-api/src
ENV ASC_EXAMPLES_DIR=/app/examples

EXPOSE 8000
USER 1000
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')"
CMD ["uvicorn", "asc_control_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
