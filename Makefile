# Claim Appeals V2 - Makefile
# Convenient commands for development and deployment

.PHONY: help dev prod build clean logs shell test lint

# Default target
help:
	@echo "Claim Appeals V2 - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Rebuild and start development environment"
	@echo "  make dev-down     - Stop development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Rebuild and start production environment"
	@echo "  make prod-down    - Stop production environment"
	@echo ""
	@echo "Utilities:"
	@echo "  make build        - Build all Docker images"
	@echo "  make clean        - Remove all containers and volumes"
	@echo "  make logs         - View logs from all services"
	@echo "  make logs-backend - View backend logs"
	@echo "  make shell-backend- Open shell in backend container"
	@echo "  make shell-mongo  - Open MongoDB shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run backend tests"
	@echo "  make lint         - Run linters"
	@echo "  make gitleaks     - Run gitleaks security scan"

# Development commands
dev:
	docker-compose up -d

dev-build:
	docker-compose up -d --build

dev-down:
	docker-compose down

# Production commands
prod:
	docker-compose -f docker-compose.prod.yml up -d

prod-build:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

# Build commands
build:
	docker-compose build

build-prod:
	docker-compose -f docker-compose.prod.yml build

# Clean commands
clean:
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
	docker system prune -f

# Log commands
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-mongo:
	docker-compose logs -f mongodb

# Shell commands
shell-backend:
	docker-compose exec backend /bin/bash

shell-mongo:
	docker-compose exec mongodb mongosh claim_appeals

# Testing
test:
	cd backend && python -m pytest -v

gitleaks:
	gitleaks detect --source . -c .gitleaks.toml -v

# Seed data
seed:
	docker-compose exec backend python seed_comprehensive.py

seed-simple:
	docker-compose exec backend python seed_data.py

# Health check
health:
	@echo "Checking services..."
	@curl -s http://localhost:8000/health && echo " - Backend OK" || echo " - Backend FAILED"
	@curl -s http://localhost:80/health && echo " - Frontend OK" || echo " - Frontend FAILED"
