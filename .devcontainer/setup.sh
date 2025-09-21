#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Line Guardrail development environment setup..."

# Install uv package manager
echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install AWS SAM CLI
echo "☁️ Installing AWS SAM CLI..."
pip3 install aws-sam-cli

# Install Bedrock AgentCore Starter Toolkit
echo "🤖 Installing Bedrock AgentCore Starter Toolkit..."
pip3 install bedrock-agentcore-starter-toolkit

# Install project dependencies
echo "🐍 Installing Python dependencies..."
uv sync

# Initialize Bedrock AgentCore project
echo "🔧 Initializing Bedrock AgentCore project..."

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cp .env.template .env 2>/dev/null || echo "# Environment variables for Line Guardrail
AWS_REGION=us-east-1
# Add your AWS credentials and other environment variables here
" > .env
fi

# Set up pre-commit hooks if available
if [ -f .pre-commit-config.yaml ]; then
    echo "🎣 Setting up pre-commit hooks..."
    uv run pre-commit install
fi

echo "✅ Development environment setup complete!"
echo "💡 Next steps:"
echo "   1. Configure your AWS credentials in .env"
echo "   2. Run 'uv run python main.py' to test the setup"
echo "   3. Start developing! 🎉"