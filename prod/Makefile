# Agent Simulation Control Plane - developer and operator entrypoints.
# Targets are thin wrappers over deploy/scripts and per-service tooling so the same
# commands work on a local k3d cluster today and a GCP k3s cluster later.
#
# The quality gates below are the `prod` CI workflow's jobs, target for target:
# `make verify` runs what CI runs, in CI's order. Keep them in step - a local
# target that has drifted from its workflow step is worse than no target,
# because it reports success for a check that never ran.

CLUSTER_NAME ?= agentsim
K3D          ?= k3d
KUBECTL      ?= kubectl
PYTHON       ?= python3
RUFF         ?= ruff
PYTEST       ?= pytest

# Exactly the paths the `prod` workflow lints and format-checks.
LINT_PATHS   := packages services stream tests conftest.py scripts

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

## ---- Package / docs verification (works today, no cluster needed) ----
# Renamed from `verify`, which now means "run every gate". This target is one
# of them; the workflow step that calls it is "Handoff package intact".
.PHONY: verify-package
verify-package: ## Verify the v0.1.0 handoff package structure
	$(PYTHON) scripts/verify_package.py

## ---- Local cluster lifecycle ----
.PHONY: cluster-up
cluster-up: ## Create the local k3d cluster
	bash deploy/scripts/cluster-up.sh $(CLUSTER_NAME)

.PHONY: cluster-down
cluster-down: ## Delete the local k3d cluster
	$(K3D) cluster delete $(CLUSTER_NAME)

.PHONY: deploy-local
deploy-local: ## Deploy the full stack to the local cluster
	bash deploy/scripts/deploy-local.sh

.PHONY: urls
urls: ## Print the reachable URLs of the deployed stack
	bash deploy/scripts/print-urls.sh

.PHONY: dashboards
dashboards: ## Hold open port-forwards for Grafana / Superset / Flink / ClickHouse
	bash deploy/scripts/port-forward-uis.sh

.PHONY: evidence
evidence: ## Run a fresh golden run and verify every hop of the deployed chain
	bash deploy/scripts/collect-evidence.sh

.PHONY: dashboards-import
dashboards-import: ## Provision the Superset dashboards from dashboards/superset/
	bash deploy/scripts/import-superset-dashboards.sh

## ---- Quality gates (each target is one `prod` workflow step) ----
.PHONY: deps
deps: ## Install everything the gates below need
	$(PYTHON) -m pip install --quiet ruff pytest pytest-cov pydantic fastapi httpx \
	  opentelemetry-sdk pyyaml

.PHONY: fmt
fmt: ## Rewrite Python to the project format
	$(RUFF) format $(LINT_PATHS)

.PHONY: fmt-check
fmt-check: ## Fail if Python is not formatted
	$(RUFF) format --check $(LINT_PATHS)

.PHONY: lint
lint: ## Lint every Python package, service, stream job, test, and script
	$(RUFF) check $(LINT_PATHS)

.PHONY: shell-syntax
shell-syntax: ## Parse every deploy and check script
	@for f in deploy/scripts/*.sh scripts/*.sh; do [ -e "$$f" ] || continue; bash -n "$$f" || exit 1; done
	@echo "shell syntax ok"

.PHONY: yaml
yaml: ## Validate every YAML document under prod/
	$(PYTHON) scripts/check_yaml.py

.PHONY: schemas
schemas: ## Domain schemas match the checked-in contracts
	$(PYTHON) scripts/check_schemas.py

.PHONY: test
test: ## Unit tests, scoped and covered the way CI scopes them
	$(PYTEST) packages services stream -q \
	  --cov=asc_domain --cov=asc_gate_engine --cov=asc_kernel --cov=asc_telemetry \
	  --cov=asc_worker --cov=asc_orchestrator --cov=asc_control_api --cov=asc_mcp_proxy \
	  --cov=asc_aggregation --cov=asc_flink --cov-report=term-missing

.PHONY: e2e
e2e: ## Run the in-process golden end-to-end tests
	$(PYTEST) tests/e2e -q

.PHONY: golden
golden: ## Golden release decisions must reproduce the committed baseline
	bash scripts/check-golden-baseline.sh

.PHONY: terraform
terraform: ## Format and validate the Terraform (never applies)
	cd infra/terraform/gcp \
	  && terraform fmt -check -recursive \
	  && terraform init -backend=false \
	  && terraform validate

.PHONY: policy
policy: ## Module policy guards - exactly what the prod workflow runs
	bash scripts/check-policy.sh

.PHONY: verify
verify: fmt-check lint shell-syntax verify-package yaml schemas test e2e golden policy ## Every prod gate that needs no cluster, in CI's order
	@echo ""
	@echo "prod verify OK (terraform validate excluded: needs the terraform binary)"

## ---- Container images ----
.PHONY: images
images: ## Build all service container images
	bash deploy/scripts/build-images.sh
