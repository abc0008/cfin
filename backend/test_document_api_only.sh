#!/bin/bash
# Test script for FDAS Document API endpoints only

BASE_URL="http://localhost:8000"
CURRENT_USER="default-user"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting FDAS Document API tests...${NC}"

# Test health endpoint
echo -e "\n${BLUE}Testing health endpoint...${NC}"
curl -s "${BASE_URL}/health" | jq .

# Test root endpoint
echo -e "\n${BLUE}Testing root endpoint...${NC}"
curl -s "${BASE_URL}/" | jq .

# Create test_data directory if it doesn't exist
mkdir -p ./test_data

# Create a simple PDF file for testing if it doesn't exist
if [ ! -f "./test_data/sample_financial_report.pdf" ]; then
    echo -e "\n${BLUE}Creating test PDF file...${NC}"
    echo "%PDF-1.5
%Test PDF file for API testing
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 45 >>
stream
BT /F1 12 Tf 100 700 Td (Test Financial Report) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R /Size 5 >>
%%EOF" > ./test_data/sample_financial_report.pdf
    echo -e "${GREEN}Created test PDF file${NC}"
fi

# Upload a test document
echo -e "\n${BLUE}Uploading a test document...${NC}"
DOC_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/documents/upload" \
    -F "file=@./test_data/sample_financial_report.pdf" \
    -F "user_id=${CURRENT_USER}")
echo $DOC_RESPONSE | jq .
DOCUMENT_ID=$(echo $DOC_RESPONSE | jq -r '.document_id')

if [ -z "$DOCUMENT_ID" ] || [ "$DOCUMENT_ID" == "null" ]; then
    echo -e "${RED}Failed to upload document${NC}"
else
    echo -e "${GREEN}Uploaded document with ID: $DOCUMENT_ID${NC}"

    # List all documents
    echo -e "\n${BLUE}Listing all documents...${NC}"
    curl -s "${BASE_URL}/api/documents?user_id=${CURRENT_USER}" | jq .

    # Get document by ID
    echo -e "\n${BLUE}Getting document by ID...${NC}"
    curl -s "${BASE_URL}/api/documents/${DOCUMENT_ID}" | jq .

    # Get document count
    echo -e "\n${BLUE}Getting document count...${NC}"
    curl -s "${BASE_URL}/api/documents/count?user_id=${CURRENT_USER}" | jq .

    # Delete document
    echo -e "\n${BLUE}Deleting document...${NC}"
    curl -s -X DELETE "${BASE_URL}/api/documents/${DOCUMENT_ID}" | jq .
    
    # Verify document is deleted
    echo -e "\n${BLUE}Verifying document is deleted...${NC}"
    DELETE_CHECK=$(curl -s "${BASE_URL}/api/documents/${DOCUMENT_ID}")
    if [[ "$DELETE_CHECK" == *"Document not found"* ]]; then
        echo -e "${GREEN}Document deleted successfully${NC}"
    else
        echo -e "${RED}Document deletion failed${NC}"
    fi
fi

echo -e "\n${GREEN}Document API test script completed${NC}" 