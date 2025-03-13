#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Restarting FastAPI server...${NC}"

# Check if server is already running
PID=$(lsof -t -i:8000 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo -e "${BLUE}Server is running with PID $PID. Stopping...${NC}"
    kill -9 $PID
    sleep 1
    
    # Verify it's stopped
    if lsof -t -i:8000 &>/dev/null; then
        echo -e "${RED}Failed to stop server. Please check manually.${NC}"
        exit 1
    else
        echo -e "${GREEN}Server stopped successfully.${NC}"
    fi
else
    echo -e "${BLUE}No server running on port 8000.${NC}"
fi

# Start the server in the background
echo -e "${BLUE}Starting server...${NC}"
cd "$(dirname "$0")"
nohup python -m app.main > server.log 2>&1 &
NEW_PID=$!

echo -e "${GREEN}Server started with PID $NEW_PID${NC}"

# Wait for server to be ready
echo -e "${BLUE}Waiting for server to be ready...${NC}"
MAX_ATTEMPTS=10
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT+1))
    echo -e "${BLUE}Checking server status (attempt $ATTEMPT/$MAX_ATTEMPTS)...${NC}"
    
    # Check if process is still running
    if ! ps -p $NEW_PID > /dev/null; then
        echo -e "${RED}Server process died. Check server.log for details.${NC}"
        exit 1
    fi
    
    # Try to connect to the server
    if curl -s http://127.0.0.1:8000/api/health > /dev/null; then
        echo -e "${GREEN}Server is up and running!${NC}"
        exit 0
    fi
    
    sleep 2
done

echo -e "${RED}Server did not start properly within the timeout period.${NC}"
echo -e "${BLUE}Check server.log for details.${NC}"
exit 1 