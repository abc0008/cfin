/**
 * Utility to test API connections
 */

import { apiService } from '../services/api';

/**
 * Tests the connection to the backend API
 * @returns Object with test results
 */
export async function testApiConnection() {
  console.log('Starting API connection tests');
  
  const results = {
    endpoints: {
      createConversation: { success: false, error: null, data: null },
      sendMessage: { success: false, error: null, data: null },
      getConversationHistory: { success: false, error: null, data: null },
      listConversations: { success: false, error: null, data: null }
    },
    overallSuccess: false
  };
  
  try {
    // Test creating a conversation
    console.log('Testing createConversation endpoint');
    try {
      const createResponse = await apiService.createConversation({
        title: 'Test Conversation'
      });
      console.log('createConversation response:', createResponse);
      results.endpoints.createConversation.success = true;
      results.endpoints.createConversation.data = createResponse;
      
      const sessionId = createResponse.session_id;
      console.log('Using session ID for further tests:', sessionId);
      
      // Test sending a message
      console.log('Testing sendMessage endpoint');
      try {
        const messageResponse = await apiService.sendMessage(
          'This is a test message from the API connection test utility',
          sessionId,
          [],
          []
        );
        console.log('sendMessage response:', messageResponse);
        results.endpoints.sendMessage.success = true;
        results.endpoints.sendMessage.data = messageResponse;
      } catch (error) {
        console.error('sendMessage test failed:', error);
        results.endpoints.sendMessage.success = false;
        results.endpoints.sendMessage.error = getErrorMessage(error);
      }
      
      // Test getting conversation history
      console.log('Testing getConversationHistory endpoint');
      try {
        const historyResponse = await apiService.getConversationHistory(sessionId);
        console.log('getConversationHistory response:', historyResponse);
        results.endpoints.getConversationHistory.success = true;
        results.endpoints.getConversationHistory.data = historyResponse;
      } catch (error) {
        console.error('getConversationHistory test failed:', error);
        results.endpoints.getConversationHistory.success = false;
        results.endpoints.getConversationHistory.error = getErrorMessage(error);
      }
    } catch (error) {
      console.error('createConversation test failed:', error);
      results.endpoints.createConversation.success = false;
      results.endpoints.createConversation.error = getErrorMessage(error);
    }
    
    // Test listing conversations - this can work even if conversation creation fails
    console.log('Testing listConversations endpoint');
    try {
      const listResponse = await apiService.listConversations();
      console.log('listConversations response:', listResponse);
      results.endpoints.listConversations.success = true;
      results.endpoints.listConversations.data = listResponse;
    } catch (error) {
      console.error('listConversations test failed:', error);
      results.endpoints.listConversations.success = false;
      results.endpoints.listConversations.error = getErrorMessage(error);
    }
    
    // Calculate overall success
    results.overallSuccess = Object.values(results.endpoints)
      .every(endpoint => endpoint.success);
    
    console.log('API tests completed with result:', results.overallSuccess ? 'SUCCESS' : 'FAILURE');
    return results;
  } catch (error) {
    console.error('Error during API testing:', error);
    return {
      ...results,
      overallError: getErrorMessage(error)
    };
  }
}

/**
 * Extracts a user-friendly error message from an error object
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
} 