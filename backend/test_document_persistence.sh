#!/bin/bash
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