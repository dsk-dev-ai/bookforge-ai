# BookForge AI — development workflow
# Requires: uv (https://docs.astral.sh/uv/), python >= 3.12

PACKAGES := config core llm planner research writer

.PHONY: help install setup sync lint format type test check audit clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Bootstrap the full toolchain (uv + project tooling)
	@command -v uv >/dev/null 2>&1 || (echo "uv is required — install it from https://docs.astral.sh/uv/" && exit 1)
	@uv python install 3.12 2>/dev/null || true

setup: install ## Install dev dependencies for every package
	@for p in $(PACKAGES); do \
		echo "==> syncing packages/$$p"; \
		uv sync --extra dev --project packages/$$p; \
	done

sync: setup ## Alias for setup (dependency sync)

lint: ## Run ruff on every package
	@for p in $(PACKAGES); do \
		echo "==> ruff ($$p)"; \
		(cd packages/$$p && uv run ruff check src tests); \
	done

format: ## Auto-fix lint issues
	@for p in $(PACKAGES); do \
		echo "==> ruff --fix ($$p)"; \
		(cd packages/$$p && uv run ruff check --fix src tests); \
	done

type: ## Run mypy strict on every package
	@for p in $(PACKAGES); do \
		echo "==> mypy ($$p)"; \
		uv run --project packages/$$p mypy -p bookforge.$$p; \
	done

test: ## Run pytest on every package
	@for p in $(PACKAGES); do \
		echo "==> pytest ($$p)"; \
		(cd packages/$$p && uv run pytest -q); \
	done

check: lint type test ## Run all static checks and tests

audit: check ## Alias for check

clean: ## Remove build artifacts and caches
	@find packages -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@find packages -type d -name ".pytest_cache" -prune -exec rm -rf {} + 2>/dev/null || true
	@find packages -type d -name "*.egg-info" -mindepth 2 -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned build artifacts."