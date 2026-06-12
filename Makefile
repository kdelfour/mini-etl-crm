SHELL := /bin/bash
export PYTHONPATH := .

.DEFAULT_GOAL := help

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

check: ## Vérifie les prérequis (python 3.11, poetry, docker + compose, démon)
	@bash scripts/preflight.sh

install: check ## Vérifie les prérequis, installe les deps (poetry) ET pull les images Docker
	poetry install
	docker compose pull

up: ## Démarre db + rabbitmq + redis (images déjà pull par `make install`)
	docker compose up -d

down: ## Arrête les services
	docker compose down

logs: ## Suit les logs des services
	docker compose logs -f

revision: ## Génère une migration (ex: make revision m="create tables")
	poetry run alembic revision --autogenerate -m "$(m)"

migrate: ## Applique les migrations
	poetry run alembic upgrade head

api: ## Lance l'API Flask (port 8000)
	poetry run python scripts/run_api.py

worker: ## Lance un worker Celery
	poetry run python scripts/run_worker.py

test: ## Lance les tests
	poetry run pytest -vv

lint: ## Lint + typecheck
	poetry run ruff check server tests
	poetry run mypy server
