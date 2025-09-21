# Makefile for Line Guardrail SAM project
# Simplifies common development and deployment tasks

.PHONY: help install build deploy clean test local start-api logs validate lint format

# Default target
help:
	@echo "📋 Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build SAM application"
	@echo "  make deploy     - Deploy to AWS (reads .env automatically)"
	@echo "  make local      - Start local development server"
	@echo "  make start-api  - Start local API Gateway"
	@echo "  make test       - Run tests"
	@echo "  make logs       - Fetch CloudWatch logs"
	@echo "  make validate   - Validate SAM template"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"

# Load environment variables from .env file
ifneq (,$(wildcard ../.env))
	include ../.env
	export
endif

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt

# Build the SAM application
build:
	@echo "🔨 Building SAM application..."
	sam build

# Deploy using the custom deploy script
deploy:
	@echo "🚀 Deploying application..."
	./deploy.sh

# Start local development
local: build
	@echo "🏠 Starting local development environment..."
	sam local start-lambda --warm-containers EAGER

# Start local API Gateway
start-api: build
	@echo "🌐 Starting local API Gateway..."
	sam local start-api --warm-containers EAGER

# Run tests (if test files exist)
test:
	@echo "🧪 Running tests..."
	@if [ -d "tests" ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "No tests directory found. Create tests/ directory for unit tests."; \
	fi

# Fetch CloudWatch logs
logs:
	@echo "📋 Fetching recent logs..."
	sam logs -n BedrockAgentCoreFunction --stack-name line-guardrail-stack --tail

# Validate SAM template
validate:
	@echo "✅ Validating SAM template..."
	sam validate

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf .aws-sam/

# Lint Python code
lint:
	@echo "🔍 Running linter..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --exclude=.aws-sam; \
	else \
		echo "flake8 not installed. Run: pip install flake8"; \
	fi

# Format Python code
format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black . --exclude='.aws-sam'; \
	else \
		echo "black not installed. Run: pip install black"; \
	fi

# Quick deploy (build + deploy)
quick-deploy: build deploy

# Development setup
setup:
	@echo "🔧 Setting up development environment..."
	@make install
	@make validate
	@echo "✅ Setup complete! Run 'make help' to see available commands."