# =============================================================================
# AI Payment Fraud Investigator - Developer Workflow
# =============================================================================

PYTHON ?= python
PACKAGE := src/fraud_investigator
SAMPLE := data/samples/sample_transactions.json

.PHONY: help install dev-install lint format typecheck validate test run docker-build docker-run clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

install: ## Install runtime dependencies
	$(PYTHON) -m pip install -e .

dev-install: ## Install runtime and development dependencies
	$(PYTHON) -m pip install -e ".[dev]"

lint: ## Run the linter
	ruff check $(PACKAGE) tests

format: ## Auto-format the codebase
	ruff format $(PACKAGE) tests

typecheck: ## Run static type checks
	mypy $(PACKAGE)

validate: ## Validate all SKILL.md files
	$(PYTHON) scripts/validate_skills.py

test: ## Run the test suite with coverage
	pytest --cov=fraud_investigator --cov-report=term-missing

run: ## Investigate the bundled sample dataset
	fraud-investigator investigate $(SAMPLE) --output output

docker-build: ## Build the container image
	docker build -t ai-payment-fraud-investigator:latest .

docker-run: ## Run the investigator in a container
	docker compose up --build

clean: ## Remove caches and generated artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage output
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
