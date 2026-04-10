.PHONY: help install dev test test-unit test-integration test-api test-cov lint lint-fix typecheck check run migrate migrate-new up down build logs shell

help: ## Mostrar ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup
install: ## Instalar dependências de produção
	cd backend && pip install -e .

dev: ## Instalar dependências de desenvolvimento
	cd backend && pip install -e ".[dev]"

# Backend
run: ## Rodar backend (dev)
	cd backend && python -m uvicorn app.main:app --reload --port {{BACKEND_PORT}}

# Database
migrate: ## Rodar migrations (alembic upgrade head)
	cd backend && alembic upgrade head

migrate-new: ## Criar nova migration (uso: make migrate-new msg="descricao")
	cd backend && alembic revision --autogenerate -m "$(msg)"

# Testes
test: ## Rodar todos os testes
	cd backend && python -m pytest -v

test-unit: ## Rodar só testes unitários
	cd backend && python -m pytest tests/unit -v

test-integration: ## Rodar só testes de integração
	cd backend && python -m pytest tests/integration -v

test-api: ## Rodar só testes de API
	cd backend && python -m pytest tests/api -v

test-cov: ## Rodar testes com cobertura
	cd backend && python -m pytest --cov=app --cov-report=term-missing -v

# Quality
lint: ## Rodar linter (ruff)
	cd backend && ruff check . && ruff format --check .

lint-fix: ## Corrigir lint automaticamente
	cd backend && ruff check --fix . && ruff format .

typecheck: ## Rodar type checker (mypy)
	cd backend && mypy app

check: ## Rodar lint + typecheck + testes
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

# Docker (produção)
up: ## Subir containers (produção)
	docker compose -f docker-compose.prod.yml up -d

down: ## Parar containers
	docker compose -f docker-compose.prod.yml down

build: ## Build containers
	docker compose -f docker-compose.prod.yml build

logs: ## Ver logs dos containers
	docker compose -f docker-compose.prod.yml logs -f

shell: ## Shell no container backend
	docker compose -f docker-compose.prod.yml exec backend bash
