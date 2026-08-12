# Infra - developer entrypoints.
# Thin wrappers over the check scripts, so the commands in the module docs, the
# `infra` CI workflow, and a contributor's terminal are the same commands.
# Run from infra/.

PYTHON ?= python3

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: hsai
hsai: ## HSAI console gates - exactly what the infra workflow runs
	PYTHON=$(PYTHON) bash scripts/check-hsai.sh

.PHONY: verify
verify: hsai ## Every infra gate that needs no network, in CI's order
