#!/bin/bash

echo "Testing POST /api/conversation endpoint"
curl -v -X POST "http://127.0.0.1:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Conversation","user_id":"default-user"}'

# Store the conversation ID from the response
CONVERSATION_ID=$(curl -s -X POST "http://127.0.0.1:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"title":"Another Test Conversation","user_id":"default-user"}' | \
    grep -o '"session_id":"[^"]*' | sed 's/"session_id":"//')

echo -e "\nConversation ID: $CONVERSATION_ID"

echo -e "\nTesting GET /api/conversation endpoint"
curl -v "http://127.0.0.1:8000/api/conversation"

echo -e "\nTesting GET specific conversation"
curl -v "http://127.0.0.1:8000/api/conversation/$CONVERSATION_ID"

echo -e "\nTesting POST /api/conversation/message endpoint"
curl -v -X POST "http://127.0.0.1:8000/api/conversation/$CONVERSATION_ID/message" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"What can you tell me about financial analysis?\",\"user_id\":\"default-user\",\"session_id\":\"$CONVERSATION_ID\"}"

echo -e "\nTesting GET conversation history"
curl -v "http://127.0.0.1:8000/api/conversation/$CONVERSATION_ID/history" 