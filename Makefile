# Makefile at the root of the project

# Use bash for more advanced features if needed
SHELL := /bin/bash

# Default command to run when `make` is called without arguments
.DEFAULT_GOAL := help

# Phony targets are not files; they are recipes that should always be executed.
.PHONY: help protos build test clean run stop

help: ## ✨ Show this help message
	@echo "------------------------------------------------------------------------"
	@echo "🚀 Sentinel AGI Agent Monorepo - Development Commands"
	@echo "------------------------------------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

protos: ## 📜 Generate gRPC and Protobuf code for all services
	@echo "--> Generating Protobuf code for all services..."
	@bash ./generate_protos.sh

build: ## 🏗️ Build all service Docker images
	@echo "--> Building all Docker images using docker-compose..."
	@docker-compose build

test:
	@if command -v docker-compose > /dev/null; then \
		docker-compose -f docker-compose.yml run --rm orchestrator pytest tests; \
	else \
		pytest tests; \
	fi
	# Add commands for testing other services here if they have tests
	# @echo "--> Running tests for Rust ast_parser..."
	# @docker-compose run --rm ast_parser cargo test
	@echo "--> All tests complete."

clean: ## 🧹 Clean up build artifacts and stop containers
	@echo "--> Stopping and removing all Docker containers..."
	@docker-compose down -v --remove-orphans
	@echo "--> Pruning Docker system..."
	@docker system prune -f
	@echo "--> Removing build artifacts..."
	@find . -name "target" -type d -prune -exec rm -rf '{}' +
	@find . -name "__pycache__" -type d -prune -exec rm -rf '{}' +
	@find . -name ".pytest_cache" -type d -prune -exec rm -rf '{}' +
	@echo "--> Clean up complete."

run: ## ▶️ Start all services in detached mode using Docker Compose
	@echo "--> Starting all services..."
	@docker-compose up -d

stop: ## ⏹️ Stop all running services
	@echo "--> Stopping all services..."
	@docker-compose down

logs: ## 📄 Tail logs for all running services
	@echo "--> Tailing logs for all services. Press Ctrl+C to exit."
	@docker-compose logs -f

lint: ## 🎨 Lint and format all services
	@echo "--> Linting Python orchestrator..."
	@docker-compose run --rm orchestrator poetry run mypy .
	# Add linting commands for other services here
	@echo "--> Linting complete."

ingest-test:  ## Run ingestion test against sample repo for CI
	@echo "--> Running ingestion test..."
	@python3 tools/ingest_git_repo.py --repo memory/data-repo --weaviate http://localhost:8080
