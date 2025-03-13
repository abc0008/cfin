#!/bin/bash

# Color codes for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# API base URL
API_BASE_URL="http://localhost:8000"

# Test PDF path
TEST_PDF_PATH="./ExampleDocs/Mueller Industries Earnings Release.pdf"

# Function to print section headers
print_header() {
  echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

# Function to check if API is running
check_api() {
  print_header "Checking if API is running"
  
  if curl -s "$API_BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}API is running at $API_BASE_URL${NC}"
    return 0
  else
    echo -e "${RED}API is not running or not accessible at $API_BASE_URL${NC}"
    echo -e "Start the API server with: cd backend && python run.py"
    return 1
  fi
}

# Test document upload
test_upload() {
  print_header "Testing document upload"
  
  if [ ! -f "$TEST_PDF_PATH" ]; then
    echo -e "${RED}Test PDF not found at $TEST_PDF_PATH${NC}"
    return 1
  fi
  
  echo -e "Uploading $TEST_PDF_PATH..."
  
  UPLOAD_RESPONSE=$(curl -s -X POST \
    -F "file=@$TEST_PDF_PATH" \
    "$API_BASE_URL/api/documents/upload")
  
  echo -e "${YELLOW}Response:${NC}"
  echo "$UPLOAD_RESPONSE" | jq -C . || echo "$UPLOAD_RESPONSE"
  
  # Extract document ID from response using grep and cut
  DOC_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"document_id":"[^"]*"' | cut -d '"' -f 4)
  
  if [ -n "$DOC_ID" ]; then
    echo -e "${GREEN}Upload successful. Document ID: $DOC_ID${NC}"
    echo "$DOC_ID" > .last_doc_id
    return 0
  else
    echo -e "${RED}Failed to extract document ID from response${NC}"
    return 1
  fi
}

# Test document listing
test_list_documents() {
  print_header "Testing document listing"
  
  echo -e "Fetching document list..."
  
  LIST_RESPONSE=$(curl -s "$API_BASE_URL/api/documents?page=1&page_size=10")
  
  echo -e "${YELLOW}Response:${NC}"
  echo "$LIST_RESPONSE" | jq -C . || echo "$LIST_RESPONSE"
  
  # Count documents
  DOC_COUNT=$(echo "$LIST_RESPONSE" | jq '. | length' 2>/dev/null)
  
  if [ -n "$DOC_COUNT" ] && [ "$DOC_COUNT" -gt 0 ]; then
    echo -e "${GREEN}Successfully retrieved $DOC_COUNT documents${NC}"
    
    # Check if our uploaded document is in the list
    if [ -f .last_doc_id ]; then
      LAST_DOC_ID=$(cat .last_doc_id)
      if echo "$LIST_RESPONSE" | grep -q "$LAST_DOC_ID"; then
        echo -e "${GREEN}Found our uploaded document in the list${NC}"
      else
        echo -e "${YELLOW}Uploaded document not found in the list (may be on another page)${NC}"
      fi
    fi
    
    return 0
  else
    echo -e "${YELLOW}No documents found or error in response${NC}"
    return 1
  fi
}

# Test document retrieval
test_get_document() {
  if [ ! -f .last_doc_id ]; then
    echo -e "${YELLOW}No document ID available. Upload a document first.${NC}"
    return 1
  fi
  
  DOC_ID=$(cat .last_doc_id)
  print_header "Testing document retrieval for ID: $DOC_ID"
  
  echo -e "Fetching document..."
  
  DOC_RESPONSE=$(curl -s "$API_BASE_URL/api/documents/$DOC_ID")
  
  echo -e "${YELLOW}Response:${NC}"
  echo "$DOC_RESPONSE" | jq -C . || echo "$DOC_RESPONSE"
  
  # Check if response contains document metadata
  if echo "$DOC_RESPONSE" | grep -q "metadata"; then
    echo -e "${GREEN}Successfully retrieved document${NC}"
    return 0
  else
    echo -e "${RED}Failed to retrieve document${NC}"
    return 1
  fi
}

# Test document citations
test_document_citations() {
  if [ ! -f .last_doc_id ]; then
    echo -e "${YELLOW}No document ID available. Upload a document first.${NC}"
    return 1
  fi
  
  DOC_ID=$(cat .last_doc_id)
  print_header "Testing document citations for ID: $DOC_ID"
  
  echo -e "Fetching citations..."
  
  CITATIONS_RESPONSE=$(curl -s "$API_BASE_URL/api/documents/$DOC_ID/citations")
  
  echo -e "${YELLOW}Response:${NC}"
  echo "$CITATIONS_RESPONSE" | jq -C . || echo "$CITATIONS_RESPONSE"
  
  # Count citations
  CITATION_COUNT=$(echo "$CITATIONS_RESPONSE" | jq '. | length' 2>/dev/null)
  
  if [ -n "$CITATION_COUNT" ]; then
    if [ "$CITATION_COUNT" -gt 0 ]; then
      echo -e "${GREEN}Successfully retrieved $CITATION_COUNT citations${NC}"
    else
      echo -e "${YELLOW}Document has no citations${NC}"
    fi
    return 0
  else
    echo -e "${RED}Failed to retrieve citations${NC}"
    return 1
  fi
}

# Test document deletion
test_delete_document() {
  if [ ! -f .last_doc_id ]; then
    echo -e "${YELLOW}No document ID available. Upload a document first.${NC}"
    return 1
  fi
  
  DOC_ID=$(cat .last_doc_id)
  print_header "Testing document deletion for ID: $DOC_ID"
  
  echo -e "Deleting document..."
  
  DELETE_RESPONSE=$(curl -s -X DELETE "$API_BASE_URL/api/documents/$DOC_ID")
  
  echo -e "${YELLOW}Response:${NC}"
  echo "$DELETE_RESPONSE" | jq -C . || echo "$DELETE_RESPONSE"
  
  # Check response
  if echo "$DELETE_RESPONSE" | grep -q "success\|deleted"; then
    echo -e "${GREEN}Successfully deleted document${NC}"
    rm .last_doc_id
    return 0
  else
    echo -e "${RED}Failed to delete document${NC}"
    return 1
  fi
}

# Run all tests
run_all_tests() {
  check_api || return 1
  test_upload
  test_list_documents
  test_get_document
  test_document_citations
  test_delete_document
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo -e "${YELLOW}jq not found. Installing...${NC}"
  if command -v brew &> /dev/null; then
    brew install jq
  elif command -v apt-get &> /dev/null; then
    sudo apt-get install -y jq
  elif command -v yum &> /dev/null; then
    sudo yum install -y jq
  else
    echo -e "${RED}Cannot install jq automatically. Please install it manually.${NC}"
    echo -e "${YELLOW}Output will not be formatted.${NC}"
  fi
fi

# Run all tests
run_all_tests 