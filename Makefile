SHELL := /bin/bash
.DEFAULT_GOAL := help

VERSION ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "dev")

.PHONY: help up down ci fmt-check lint type-check test-unit test-int build \
        security-scan migrate hooks release-check

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

up: ## Start all services and verify health
	VERSION=$(VERSION) docker compose up -d
	bash scripts/docker-verify.sh

down: ## Stop all services
	docker compose down

ci: fmt-check lint type-check test-unit test-int build security-scan ## Run full CI pipeline locally

fmt-check: ## Check formatting (Black + Prettier)
	docker compose run --rm backend black --check .
	cd frontend && pnpm prettier --check "src/**/*"

lint: ## Lint code (Ruff + ESLint)
	docker compose run --rm backend ruff check .
	cd frontend && pnpm eslint src

type-check: ## Static analysis (mypy + tsc)
	docker compose run --rm backend mypy .
	cd frontend && pnpm tsc --noEmit

test-unit: ## Run unit tests (pytest + vitest)
	docker compose run --rm backend pytest -m unit
	cd frontend && pnpm vitest run

test-int: ## Run integration tests (requires Docker)
	docker compose run --rm backend pytest -m integration

build: ## Build container images (requires clean git tree)
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "ERROR: working tree is dirty — commit or stash changes before building release images"; \
		exit 1; \
	fi
	VERSION=$(VERSION) docker build --build-arg VERSION=$(VERSION) -t math-racers/backend:$(VERSION) backend/
	VERSION=$(VERSION) docker build -t math-racers/frontend:$(VERSION) frontend/

security-scan: ## Run security scans (trivy + pip-audit + npm audit)
	trivy image math-racers/backend:$(VERSION)
	trivy image math-racers/frontend:$(VERSION)
	cd backend && pip-audit
	cd frontend && npm audit --audit-level=critical

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

hooks: ## Install git hooks
	mkdir -p .git/hooks
	cp scripts/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed"

release-check: ## Run automated release criteria checks
	@echo "=== Release Criteria Check ==="
	@echo "1. Running CI pipeline..."
	$(MAKE) ci
	@echo "2. Checking health endpoint..."
	$(MAKE) up
	@curl -sf http://localhost/health | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d['status']=='ok' else 1)"
	@echo "All automated release criteria passed."
