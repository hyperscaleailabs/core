# hsailabs core - the repository's gates, in one place.
#
# Every check CI runs is reachable from here, and every target is the same
# command the workflow runs. That equivalence is the point: a local target that
# has drifted from its workflow step reports success for a check that never
# ran, and the drift is only discovered on a hosted runner after the handoff
# (atlas/docs/lessons/2026-07-28-atlas-integration.md, lesson L6).
#
# The `ci-hygiene` guard keeps the equivalence honest.
#
#   make policy    repository-wide guards (the `policy` workflow)
#   make verify    repository-wide guards, then every module's own gate
#   make help      the full list

PYTHON ?= python3

# Modules that carry their own Makefile and therefore their own `verify`.
MODULES := atlas infra models prod

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Per-module targets: make -C <module> help   ($(MODULES))"

## ---- Repository-wide guards (the `policy` workflow) ----
.PHONY: pii
pii: ## No PII anywhere in the working tree
	bash tools/policy/check_pii.sh tree

.PHONY: links
links: ## Relative markdown links and heading anchors resolve
	bash tools/policy/check_links.sh

.PHONY: writing
writing: ## Writing rules from AGENTS.md (plain dash, never an em dash)
	$(PYTHON) tools/policy/check_writing.py

.PHONY: ci-hygiene
ci-hygiene: ## Workflow hygiene: pipefail, extracted policy guards, module verify targets
	$(PYTHON) tools/policy/check_ci_hygiene.py

.PHONY: policy
policy: pii links writing ci-hygiene ## Every repository-wide guard

## ---- Modules ----
.PHONY: verify-modules
verify-modules: ## Run each module's own verify target
	@for m in $(MODULES); do \
	  echo ""; echo "==> $$m"; \
	  $(MAKE) --no-print-directory -C $$m verify || exit 1; \
	done

.PHONY: verify
verify: policy verify-modules ## Repository guards, then every module gate
	@echo ""
	@echo "all gates OK"

## ---- Setup ----
.PHONY: deps
deps: ## Install what the repository-wide guards need
	$(PYTHON) -m pip install --quiet pyyaml
	@echo "module dependencies: make -C prod deps, make -C models deps, make -C atlas install"

.PHONY: hooks
hooks: ## Install the pre-commit hooks
	pre-commit install --install-hooks
	pre-commit install --hook-type commit-msg
