# mcp-simulator-proxy image (ASC-007). Build context = repo root:
#   docker build -f deploy/docker/mcp-proxy.Dockerfile -t mcp-simulator-proxy:dev .
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29" "pydantic>=2.6"

COPY packages ./packages
COPY services/mcp-simulator-proxy ./services/mcp-simulator-proxy
COPY examples ./examples

ENV PYTHONPATH=/app/packages/domain/src:/app/packages/simulation-kernel/src:/app/services/mcp-simulator-proxy/src
ENV ASC_EXAMPLES_DIR=/app/examples

EXPOSE 8000
USER 1000
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')"
CMD ["uvicorn", "asc_mcp_proxy.app:app", "--host", "0.0.0.0", "--port", "8000"]
