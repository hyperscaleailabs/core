# Agent Simulation Control Plane — developer & operator entrypoints.
# Targets are thin wrappers over deploy/scripts and per-service tooling so the same
# commands work on a local k3d cluster today and a GCP k3s cluster later.

CLUSTER_NAME ?= agentsim
K3D          ?= k3d
KUBECTL      ?= kubectl
PYTHON       ?= python3

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

## ---- Package / docs verification (works today, no cluster needed) ----
.PHONY: verify
verify: ## Verify the v0.1.0 handoff package structure
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
urls: ## Print operator-web / Grafana / Superset / Druid URLs
	bash deploy/scripts/print-urls.sh

## ---- Quality gates ----
.PHONY: lint
lint: ## Lint all Python services/packages
	ruff check services packages stream tests

.PHONY: test
test: ## Run unit tests
	pytest -q

.PHONY: e2e
e2e: ## Run the golden Purchase Ambiguity workflow end-to-end
	pytest -q tests/e2e

## ---- Container images ----
.PHONY: images
images: ## Build all service container images
	bash deploy/scripts/build-images.sh
