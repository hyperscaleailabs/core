# Atlas - developer and publisher entrypoints.
# Thin wrappers over the npm scripts and the intake tooling, so the commands in
# the module docs, the CI workflow, and a contributor's terminal are the same
# commands. Run from atlas/.

NPM    ?= npm
NODE   ?= node
PYTHON ?= python3

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

## ---- Site ----
.PHONY: install
install: ## Install site dependencies from the lockfile
	$(NPM) ci

.PHONY: dev
dev: ## Live preview at http://localhost:4321
	$(NPM) run dev

.PHONY: index
index: ## Rebuild public/search-index.json from the corpus
	$(NPM) run index

.PHONY: check
check: ## Type and content-schema check
	$(NPM) run check

.PHONY: build
build: ## Production build (validates every article's frontmatter)
	$(NPM) run build

.PHONY: preview
preview: ## Serve the production build locally
	$(NPM) run preview

.PHONY: check-collections
check-collections: ## Fail if a collection is registered in only one of the two places
	$(NODE) scripts/check-collections.mjs

.PHONY: policy
policy: ## Module policy guards - exactly what the atlas workflow runs
	bash scripts/check-policy.sh

.PHONY: verify
verify: index check-collections check build policy ## Everything CI runs for the site, in CI's order

## ---- Publication intake ----
.PHONY: intake-check
intake-check: ## Fail if a module article has no Lab Notes entry
	$(NODE) scripts/intake-module-article.mjs --all --check

.PHONY: index-fresh
index-fresh: ## Fail if the committed search index is stale
	$(NPM) run index
	@git diff --quiet -- public/search-index.json \
	  || { echo "search-index.json is stale; commit the rebuilt index"; exit 1; }

## ---- Ingestion pipeline ----
.PHONY: pipeline-deps
pipeline-deps: ## Install the ingestion pipeline's Python dependencies
	$(PYTHON) -m pip install -r pipeline/requirements.txt

.PHONY: ingest-dry
ingest-dry: ## Fetch and plan without writing anything
	$(PYTHON) pipeline/ingest.py --dry-run
