# Models - developer entrypoints.
# Thin wrappers over the check scripts, so the commands in the module docs, the
# `models` CI workflow, and a contributor's terminal are the same commands.
# Run from models/.

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

## ---- Quality gates ----
.PHONY: deps
deps: ## Install the dependencies the static checks need
	$(PIP) install --quiet pyyaml jsonschema

.PHONY: static
static: ## Python/shell syntax, YAML validity, golden schema - exactly what CI runs
	bash scripts/check-static.sh

.PHONY: policy
policy: ## Module policy guards - exactly what the models workflow runs
	bash scripts/check-policy.sh

.PHONY: verify
verify: static policy ## Every models gate that needs no network, in CI's order

## ---- Golden slices ----
# The `golden-smoke-evidence` CI job downloads real dataset slices, so it needs
# network and the goldens' own dependencies. It is deliberately outside
# `verify`: a target that cannot run offline would make `verify` unreliable as
# the pre-push gate.
.PHONY: goldens-deps
goldens-deps: ## Install the golden puller's dependencies
	$(PIP) install --quiet -r goldens/requirements.txt

.PHONY: smoke
smoke: ## Pull the golden smoke slices CI attaches as evidence (needs network)
	$(PYTHON) goldens/pull.py --golden coding-mbpp --split eval --limit 3
	$(PYTHON) goldens/pull.py --golden ecommerce-ecinstruct --split train --limit 3
	$(PYTHON) goldens/pull.py --golden voice-librispeech --split eval --limit 2 --smoke
