#!/bin/bash
# Test script specifically for Document API endpoints

BASE_URL="http://localhost:8001"
CURRENT_USER="default-user"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Document API Endpoint Tests...${NC}"

# Test health endpoint to make sure the server is running
echo -e "\n${BLUE}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "${BASE_URL}/health")
echo $HEALTH_RESPONSE | jq .

if [[ $HEALTH_RESPONSE != *"ok"* ]]; then
  echo -e "${RED}Server is not responding correctly. Make sure it's running.${NC}"
  exit 1
fi

# 1. Upload a test document
echo -e "\n${BLUE}1. Testing document upload...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/documents/upload" \
    -F "file=@./test_data/sample.pdf" \
    -F "user_id=${CURRENT_USER}")
echo $UPLOAD_RESPONSE | jq .

DOCUMENT_ID=$(echo $UPLOAD_RESPONSE | jq -r '.document_id')

if [ -z "$DOCUMENT_ID" ] || [ "$DOCUMENT_ID" == "null" ]; then
    echo -e "${RED}Failed to upload document${NC}"
    exit 1
else
    echo -e "${GREEN}Uploaded document with ID: $DOCUMENT_ID${NC}"
    
    # Wait for processing to start
    echo -e "\n${BLUE}Waiting for document processing to begin...${NC}"
    sleep 2

    # 2. Test retrieving a specific document
    echo -e "\n${BLUE}2. Testing GET /api/documents/{document_id}...${NC}"
    GET_DOC_RESPONSE=$(curl -s -v "${BASE_URL}/api/documents/${DOCUMENT_ID}" 2>&1)
    echo "$GET_DOC_RESPONSE" | jq 2>/dev/null || echo "$GET_DOC_RESPONSE"
    
    # 3. Test listing all documents
    echo -e "\n${BLUE}3. Testing GET /api/documents...${NC}"
    LIST_DOCS_RESPONSE=$(curl -s -v "${BASE_URL}/api/documents?user_id=${CURRENT_USER}&page=1&page_size=10" 2>&1)
    echo "$LIST_DOCS_RESPONSE" | jq 2>/dev/null || echo "$LIST_DOCS_RESPONSE"
    
    # 4. Test getting document count
    echo -e "\n${BLUE}4. Testing GET /api/documents/count...${NC}"
    COUNT_RESPONSE=$(curl -s -v "${BASE_URL}/api/documents/count?user_id=${CURRENT_USER}" 2>&1)
    echo "$COUNT_RESPONSE" | jq 2>/dev/null || echo "$COUNT_RESPONSE"
    
    # Wait for processing to complete
    echo -e "\n${BLUE}Waiting for document processing to complete...${NC}"
    sleep 5
    
    # 5. Test getting document citations
    echo -e "\n${BLUE}5. Testing GET /api/documents/{document_id}/citations...${NC}"
    CITATIONS_RESPONSE=$(curl -s "${BASE_URL}/api/documents/${DOCUMENT_ID}/citations")
    echo $CITATIONS_RESPONSE | jq .
    
    # Check if there are any citations
    CITATION_COUNT=$(echo $CITATIONS_RESPONSE | jq 'length')
    if [ "$CITATION_COUNT" -gt 0 ]; then
        CITATION_ID=$(echo $CITATIONS_RESPONSE | jq -r '.[0].id')
        
        # 6. Test getting a specific citation
        echo -e "\n${BLUE}6. Testing GET /api/documents/{document_id}/citations/{citation_id}...${NC}"
        curl -s "${BASE_URL}/api/documents/${DOCUMENT_ID}/citations/${CITATION_ID}" | jq .
    else
        echo -e "${BLUE}No citations available to test citation retrieval endpoints${NC}"
    fi
    
    # 7. Test deleting the document
    echo -e "\n${BLUE}7. Testing DELETE /api/documents/{document_id}...${NC}"
    DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/api/documents/${DOCUMENT_ID}")
    echo $DELETE_RESPONSE | jq .
    
    # Verify document was deleted by trying to retrieve it again
    echo -e "\n${BLUE}Verifying document deletion...${NC}"
    GET_DELETED_RESPONSE=$(curl -s -w "%{http_code}" "${BASE_URL}/api/documents/${DOCUMENT_ID}" -o /dev/null)
    
    if [ "$GET_DELETED_RESPONSE" == "404" ]; then
        echo -e "${GREEN}Document successfully deleted (received 404 Not Found)${NC}"
    else
        echo -e "${RED}Document may not have been deleted. Received HTTP $GET_DELETED_RESPONSE${NC}"
    fi
fi

echo -e "\n${GREEN}Document API endpoint tests completed${NC}" 