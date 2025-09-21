#!/bin/bash

# Deploy script for SAM application with automatic .env loading
# This script reads environment variables from .env file and passes them to SAM deploy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting SAM deployment for Line Guardrail...${NC}"

# Check if .env file exists
ENV_FILE="../.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found at $ENV_FILE${NC}"
    echo -e "${YELLOW}💡 Please copy .env.template to .env and configure your environment variables${NC}"
    exit 1
fi

echo -e "${GREEN}📄 Loading environment variables from $ENV_FILE${NC}"

# Source the .env file to load variables
set -a
source "$ENV_FILE"
set +a

# Build parameters from environment variables
PARAMETERS=""

# Add parameters if they exist in environment
if [ ! -z "$BEDROCK_AGENT_RUNTIME_ARN" ]; then
    PARAMETERS="$PARAMETERS BedrockAgentRuntimeArn=$BEDROCK_AGENT_RUNTIME_ARN"
fi

if [ ! -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    PARAMETERS="$PARAMETERS LineChannelAccessToken=$LINE_CHANNEL_ACCESS_TOKEN"
fi

if [ ! -z "$LINE_CHANNEL_SECRET" ]; then
    PARAMETERS="$PARAMETERS LineChannelSecret=$LINE_CHANNEL_SECRET"
fi

# Check if we have any parameters
if [ -z "$PARAMETERS" ]; then
    echo -e "${YELLOW}⚠️  Warning: No SAM parameters found in .env file${NC}"
    echo -e "${YELLOW}   Make sure to set BEDROCK_AGENT_RUNTIME_ARN, LINE_CHANNEL_ACCESS_TOKEN, and LINE_CHANNEL_SECRET${NC}"
fi

# Build the application
echo -e "${BLUE}🔨 Building SAM application...${NC}"
sam build

# Deploy with parameters
echo -e "${BLUE}☁️  Deploying to AWS...${NC}"
if [ ! -z "$PARAMETERS" ]; then
    echo -e "${GREEN}📝 Using parameters: $PARAMETERS${NC}"
    sam deploy --resolve-s3 --parameter-overrides $PARAMETERS
else
    echo -e "${YELLOW}⚠️  Deploying without parameter overrides${NC}"
    sam deploy --resolve-s3
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}💡 You can now test your API using the endpoint shown above${NC}"