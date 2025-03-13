#!/bin/bash
# Test script for FDAS API endpoints

# ANSI colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URL for the API - change this if your server is running on a different port
API_URL=${API_URL:-"http://127.0.0.1:8000"}

# Temp file for IDs
TMP_FILE=".tmp_ids.txt"
touch $TMP_FILE

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}   FDAS API Testing Script        ${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "${YELLOW}API URL: ${API_URL}${NC}\n"

# Function to print the section header
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to test an API endpoint and capture the response
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expectation=$4
    local variable_name=$5

    echo -e "${YELLOW}Testing ${method} ${endpoint}${NC}"
    echo -e "${BLUE}Full URL: ${API_URL}${endpoint}${NC}"
    
    # Execute the appropriate curl command based on method with verbose output
    if [ "$method" = "GET" ]; then
        response=$(curl -s -X GET "${API_URL}${endpoint}")
    elif [ "$method" = "POST" ]; then
        echo -e "${BLUE}Request data: ${data}${NC}"
        response=$(curl -s -X POST "${API_URL}${endpoint}" -H "Content-Type: application/json" -d "${data}")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -X DELETE "${API_URL}${endpoint}")
    else
        echo -e "${RED}Unknown method: ${method}${NC}"
        return 1
    fi
    
    # Print actual request and response
    echo -e "${BLUE}Response: ${NC}"
    echo "$response"
    
    # Check if the response contains what we expect
    if [[ $response == *"$expectation"* ]]; then
        echo -e "${GREEN}SUCCESS: Response contains expected value${NC}"
    else
        echo -e "${RED}FAILURE: Response does not contain expected value${NC}"
    fi
    
    # If a variable name is provided, extract the ID from the response and save it
    if [ -n "$variable_name" ]; then
        id=$(echo $response | grep -o -E '"id":"[^"]+"' | head -1 | cut -d '"' -f 4)
        if [ -n "$id" ]; then
            echo "$variable_name=$id" >> $TMP_FILE
            echo -e "${GREEN}Saved $variable_name=$id${NC}"
        else
            echo -e "${RED}Could not extract ID from response${NC}"
        fi
    fi
    
    echo ""
}

# Load IDs from temporary file
load_vars() {
    if [ -f $TMP_FILE ]; then
        source $TMP_FILE
    fi
}

# Clean up on exit
cleanup() {
    if [ -f $TMP_FILE ]; then
        rm $TMP_FILE
    fi
}
trap cleanup EXIT

# 1. Create Conversation
print_section "Create Conversation"
test_endpoint "POST" "/api/conversation" \
  '{"title":"Test Conversation","user_id":"default-user"}' \
  "session_id" "conversation_id"

# Load variables from temp file
load_vars

# 2. Send Message
print_section "Send Message"
test_endpoint "POST" "/api/conversation/${conversation_id}/message" \
  '{"session_id":"'$conversation_id'","content":"What are some key financial metrics to look for in a balance sheet?","referenced_documents":[],"referenced_analyses":[],"citation_links":[]}' \
  "content" "message_id"

# Load variables from temp file
load_vars

# 3. Get Conversation History
print_section "Get Conversation History"
test_endpoint "GET" "/api/conversation/${conversation_id}/history?limit=10" \
  '' \
  "role"

# 4. List Conversations
print_section "List Conversations"
test_endpoint "GET" "/api/conversation?limit=10&offset=0" \
  '' \
  "title"

# 5. Delete Conversation
print_section "Delete Conversation"
if [ -n "$conversation_id" ]; then
    test_endpoint "DELETE" "/api/conversation/${conversation_id}" \
      '' \
      ""
else
    echo -e "${RED}Cannot delete conversation - ID not found${NC}"
fi

echo -e "\n${GREEN}===== API Testing Complete =====${NC}"