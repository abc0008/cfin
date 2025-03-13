# Testing the API Connection

This document provides instructions for testing the connection between the frontend chat interface and the backend conversation API, which was implemented as part of Action Item 3.1.

## Prerequisites

1. Make sure both the backend and frontend servers are running:

   **Backend:**
   ```bash
   cd cfin/backend
   python run.py
   ```

   **Frontend:**
   ```bash
   cd cfin
   npm run dev
   ```

## Testing Methods

### 1. Using the API Test UI Component

The API Connection Test component helps verify that all API endpoints are working correctly. To use it:

1. Add the `apitest=true` query parameter to your URL:
   ```
   http://localhost:5173/?apitest=true
   ```

2. Click the "Run API Tests" button at the top of the page.

3. The component will test the following endpoints:
   - `createConversation`: Creates a test conversation
   - `sendMessage`: Sends a test message to the conversation
   - `getConversationHistory`: Retrieves the conversation history
   - `listConversations`: Lists all available conversations

4. Check the results to see if any endpoints are failing. If any endpoint fails, the test will provide detailed error information.

### 2. Manual Testing through the UI

1. Navigate to the main application (without any query parameters).

2. Observe that a new session is automatically created when you first load the page.

3. Type a message in the chat interface and press enter or click the send button.

4. Verify that the message is sent to the backend and a response is received. You should see:
   - Your message in the chat interface
   - A loading indicator while waiting for the response
   - The AI's response once it's received from the backend

5. Test error handling by temporarily stopping the backend server while sending a message. You should see a user-friendly error message.

6. If multiple conversations are available, test switching between them using the session selector dropdown.

### 3. Testing Session Management

1. Create a new conversation by selecting "+ New Conversation" from the dropdown.

2. Send a few messages in this conversation to establish some history.

3. Note the current session ID in the URL (or console logs).

4. Create another new conversation and send different messages.

5. Use the session selector to switch back to the first conversation.

6. Verify that the message history is correctly loaded and displays messages from the first conversation.

## Common Issues and Troubleshooting

1. **API Endpoint URL Mismatch**: Make sure the API endpoint paths in the frontend match what the backend expects. Check for missing or incorrect prefixes like `/api` or `/v1`.

2. **CORS Issues**: If you see CORS errors in the console, ensure that the backend is properly configured to allow requests from the frontend domain.

3. **Authentication/Session Issues**: If you're seeing 401 or 403 errors, there might be an issue with authentication or session handling.

4. **Data Format Issues**: Verify that the request payloads and response handling match what the backend expects and provides.

## Next Steps

After confirming that the API connection is working correctly, proceed to implementing Action Item 3.2: Connect Frontend Document Upload to Backend Document API.

## Reporting Issues

If you encounter any issues during testing, please:

1. Check the browser console for error messages
2. Verify the backend server logs for any errors
3. Ensure the environment variables are correctly set up
4. Document the steps to reproduce the issue
5. Report the issue with as much detail as possible 