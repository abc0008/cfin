#!/bin/bash

# Set environment variables for testing
export PYTHONPATH=.
export ANTHROPIC_API_KEY="test-key"
export CLAUDE_MODEL="claude-3-5-sonnet-latest"

# Install test dependencies if not already installed
pip install pytest pytest-asyncio pytest-cov

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit -v

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration -v

# Run performance tests (optional)
if [ "$1" == "--with-performance" ]; then
    echo "Running performance tests..."
    python -m pytest tests/performance -v
fi

# Run all tests with coverage
echo "Running all tests with coverage..."
python -m pytest --cov=api --cov=pdf_processing --cov=utils --cov=models --cov-report=term --cov-report=html tests/

echo "Coverage report generated in htmlcov/ directory"

# Script to run document persistence tests

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running document persistence tests...${NC}"

# Run unit tests for DocumentRepository
echo -e "\n${BLUE}Running DocumentRepository unit tests...${NC}"
python -m pytest tests/test_document_repository.py -v

# Run API tests for document endpoints
echo -e "\n${BLUE}Running document API tests...${NC}"
python -m pytest tests/test_document_api.py -v

# Run the API test script
echo -e "\n${BLUE}Running API test script...${NC}"
bash test_api.sh

echo -e "\n${GREEN}Tests completed.${NC}" 