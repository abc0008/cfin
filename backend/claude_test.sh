#!/bin/bash
set -e

# Define colors for better output readability
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Claude API with PDF citations...${NC}"
echo "This script will create a conversation, upload a PDF, and test the Claude API response"
echo "---------------------------------------------------------------------------------"

# Base URL
API_URL="http://127.0.0.1:8000"

# Step 1: Create a new conversation
echo -e "\n${BLUE}Step 1: Creating a new conversation...${NC}"
CONVERSATION_RESPONSE=$(curl -s -X POST "$API_URL/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"title":"Mueller Industries Earnings Analysis","user_id":"default-user"}')

echo "Response: $CONVERSATION_RESPONSE"

# Extract conversation ID
CONVERSATION_ID=$(echo $CONVERSATION_RESPONSE | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CONVERSATION_ID" ]; then
    echo -e "${RED}Failed to create conversation or extract ID${NC}"
    exit 1
fi

echo -e "${GREEN}Created conversation with ID: $CONVERSATION_ID${NC}"

# Step 2: Upload a sample PDF document
echo -e "\n${BLUE}Step 2: Uploading sample PDF document...${NC}"

# Use the provided sample PDF
SAMPLE_PDF="/Users/alexc/Documents/AlexCoding/cfin/ExampleDocs/Mueller Industries Earnings Release.pdf"
if [ ! -f "$SAMPLE_PDF" ]; then
    echo -e "${RED}Sample PDF not found at $SAMPLE_PDF${NC}"
    exit 1
fi

echo -e "${GREEN}Using sample PDF: $SAMPLE_PDF${NC}"

# Upload the PDF using the correct endpoint
DOCUMENT_RESPONSE=$(curl -s -X POST "$API_URL/api/documents/upload" \
    -F "file=@$SAMPLE_PDF" \
    -F "user_id=default-user")

echo "Document response: $DOCUMENT_RESPONSE"

# Extract document ID
DOCUMENT_ID=$(echo $DOCUMENT_RESPONSE | grep -o '"document_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$DOCUMENT_ID" ]; then
    echo -e "${RED}Failed to upload document or extract ID${NC}"
    exit 1
fi

echo -e "${GREEN}Uploaded document with ID: $DOCUMENT_ID${NC}"

# Step 3: Associate document with conversation
echo -e "\n${BLUE}Step 3: Associating document with conversation...${NC}"
ASSOCIATION_RESPONSE=$(curl -s -X POST "$API_URL/api/conversation/$CONVERSATION_ID/documents/$DOCUMENT_ID" \
    -H "Content-Type: application/json")

echo "Association response: $ASSOCIATION_RESPONSE"

echo -e "${GREEN}Document associated with conversation${NC}"

# Step 4: Send a message to analyze the document
echo -e "\n${BLUE}Step 4: Sending message to analyze the document...${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "$API_URL/api/conversation/$CONVERSATION_ID/message" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"What were the key financial results in the Mueller Industries earnings release? Please provide specific figures and give me actual citations to the document that I can verify. I need explicit page numbers where each financial figure appears. Use the citations feature to link each fact directly to the source document. This is very important - please include structured citations for all data.\",\"user_id\":\"default-user\",\"session_id\":\"$CONVERSATION_ID\"}")

echo "Message response: $MESSAGE_RESPONSE"

echo -e "${GREEN}Message sent to analyze document${NC}"

# Step 5: Get conversation history to see the response
echo -e "\n${BLUE}Step 5: Getting conversation history...${NC}"
sleep 5  # Wait a bit longer for processing since we're using a real PDF
HISTORY_RESPONSE=$(curl -s -X GET "$API_URL/api/conversation/$CONVERSATION_ID/history")

echo -e "${GREEN}Conversation history:${NC}"
echo "$HISTORY_RESPONSE" | python -m json.tool

echo -e "\n${BLUE}Test completed!${NC}" 