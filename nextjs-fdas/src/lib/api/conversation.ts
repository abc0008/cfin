import { Message } from '@/types';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Conversation API service
 * Handles communication with the backend for conversation operations
 */
class ConversationApiService {
  /**
   * Send a request to the API
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData
  ): Promise<T> {
    // Ensure endpoint starts with / 
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Fixed URL construction to prevent duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') || endpoint.startsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}/api${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    try {
      const response = await fetch(finalUrl, options);
      
      // Handle non-OK responses
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        
        // Try to parse error response as JSON
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc.join('.')}: ${err.msg}`
              ).join(', ');
            } else {
              errorMessage = JSON.stringify(errorData.detail);
            }
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          // If not JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            // Keep the original error message if we can't parse the response
          }
        }
        
        throw new Error(errorMessage);
      }
      
      // Parse the response
      const responseData = await response.json();
      return responseData as T;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(data: { title: string, document_ids?: string[] }): Promise<{ session_id: string }> {
    try {
      // Send request
      const response = await this.request<any>(
        '/conversation',
        'POST',
        data
      );
      
      // Extract the session ID from the response
      if (response && response.session_id) {
        return { session_id: response.session_id };
      } else if (response && response.id) {
        // Handle alternative response format
        return { session_id: response.id };
      } else {
        throw new Error('Unexpected response format from conversation creation');
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw new Error(`Failed to create conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * List user conversations
   */
  async listConversations(): Promise<Array<{ id: string, title: string }>> {
    try {
      // Get list of conversations for the current user
      const response = await this.request<any[]>(
        '/conversation',
        'GET'
      );
      
      // Convert backend format to our frontend format
      const conversations = response.map(conv => ({
        id: conv.id || conv.session_id || conv.conversation_id,
        title: conv.title || 'Untitled Conversation'
      }));
      
      return conversations;
    } catch (error) {
      console.error('Error listing conversations:', error);
      return [];
    }
  }
  
  /**
   * Send a message to the conversation
   */
  async sendMessage(sessionId: string, message: string, documentIds: string[] = []): Promise<Message> {
    try {
      const response = await this.request<Message>(
        `/conversation/${sessionId}/message`,
        'POST',
        {
          content: message,
          document_ids: documentIds
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error(`Failed to send message: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Get messages for a conversation
   */
  async getMessages(sessionId: string): Promise<Message[]> {
    try {
      const response = await this.request<Message[]>(
        `/conversation/${sessionId}/messages`,
        'GET'
      );
      
      return response;
    } catch (error) {
      console.error('Error getting messages:', error);
      return [];
    }
  }
  
  /**
   * Get a single conversation
   */
  async getConversation(sessionId: string): Promise<{ id: string, title: string, messages: Message[] }> {
    try {
      const conversation = await this.request<any>(
        `/conversation/${sessionId}`,
        'GET'
      );
      
      const messages = await this.getMessages(sessionId);
      
      return {
        id: conversation.id || conversation.session_id,
        title: conversation.title || 'Untitled Conversation',
        messages
      };
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw new Error(`Failed to get conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Create a new analysis from conversation
   */
  async createAnalysisFromConversation(
    sessionId: string, 
    documentIds: string[], 
    analysisType: string
  ): Promise<{ analysis_id: string }> {
    try {
      const response = await this.request<{ analysis_id: string }>(
        `/conversation/${sessionId}/analysis`,
        'POST',
        {
          document_ids: documentIds,
          analysis_type: analysisType
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error creating analysis from conversation:', error);
      throw new Error(`Failed to create analysis: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

export const conversationApi = new ConversationApiService(); 