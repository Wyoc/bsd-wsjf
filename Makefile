.PHONY: help setup dev dev-backend dev-frontend install install-backend install-frontend test test-backend test-frontend lint lint-backend lint-frontend build build-backend build-frontend clean docker-up docker-down docker-build docker-logs

# Default target
help: ## Show this help message
	@echo "WSJF Excel Generator - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup
setup: ## Initial project setup
	@echo "Setting up WSJF Excel Generator..."
	$(MAKE) install
	@echo "Setup complete! Run 'make dev' to start development."

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	cd backend && uv pip install -e .[dev]

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development
dev: ## Start development environment (both frontend and backend)
	docker-compose up --build

dev-backend: ## Start backend development server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

# Testing
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# Linting
lint: lint-backend lint-frontend ## Run all linting

lint-backend: ## Run backend linting and formatting
	cd backend && black . && isort . && flake8 . && mypy .

lint-frontend: ## Run frontend linting
	cd frontend && npm run lint && npm run type-check

# Building
build: build-backend build-frontend ## Build all components

build-backend: ## Build backend
	cd backend && python -m build

build-frontend: ## Build frontend
	cd frontend && npm run build

# Cleaning
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf backend/dist/
	rm -rf backend/build/
	rm -rf backend/*.egg-info/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-up: ## Start docker containers
	docker-compose up -d

docker-down: ## Stop docker containers
	docker-compose down

docker-build: ## Build docker containers
	docker-compose build

docker-logs: ## Show docker logs
	docker-compose logs -f

docker-clean: ## Clean docker containers and images
	docker-compose down -v --rmi all

# Production
prod-build: ## Build for production
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down