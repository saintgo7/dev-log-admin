.PHONY: start stop status start-no-legacy start-legacy start-backend start-frontend \
       db-init db-migrate migrate-sqlite sync-legacy discover \
       test-backend test-frontend lint-backend lint-frontend \
       install help

# ==========================================
# Service Management
# ==========================================

start: ## Start all services (legacy + backend + frontend)
	@./scripts/start.sh all

stop: ## Stop all services
	@./scripts/stop.sh all

status: ## Show service status
	@./scripts/status.sh

start-no-legacy: ## Start backend + frontend (no legacy)
	@./scripts/start.sh all --no-legacy

start-legacy: ## Start legacy server only (port 8100)
	@./scripts/start.sh legacy

start-backend: ## Start backend only (port 8200)
	@./scripts/start.sh backend

start-frontend: ## Start frontend only (port 3000)
	@./scripts/start.sh frontend

stop-legacy: ## Stop legacy server
	@./scripts/stop.sh legacy

stop-backend: ## Stop backend server
	@./scripts/stop.sh backend

stop-frontend: ## Stop frontend
	@./scripts/stop.sh frontend

# ==========================================
# Database
# ==========================================

db-init: ## Initialize legacy SQLite database
	@python3 legacy/database.py

db-migrate: ## Run Alembic migrations (PostgreSQL)
	@cd backend && alembic upgrade head

migrate-sqlite: ## Migrate SQLite data to PostgreSQL
	@./scripts/migrate.sh

migrate-sqlite-dry: ## Dry run: show what would be migrated
	@./scripts/migrate.sh --dry-run

# ==========================================
# Data Sync
# ==========================================

sync-legacy: ## Sync JSON data to SQLite
	@./scripts/sync-legacy.sh

discover: ## Auto-discover projects and sync
	@./scripts/sync-legacy.sh --discover

# ==========================================
# Testing
# ==========================================

test-backend: ## Run backend tests
	@cd backend && python3 -m pytest tests/ -v

test-frontend: ## Run frontend tests
	@cd frontend && npm test

lint-backend: ## Lint backend code
	@cd backend && python3 -m ruff check app/

lint-frontend: ## Lint frontend code
	@cd frontend && npm run lint

# ==========================================
# Setup
# ==========================================

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	@cd backend && pip3 install -r requirements.txt
	@echo ""
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo ""
	@echo "Done!"

# ==========================================
# Help
# ==========================================

help: ## Show this help
	@echo ""
	@echo "Dev Log Admin - Available Commands"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
