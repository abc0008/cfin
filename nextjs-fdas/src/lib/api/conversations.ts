import { Message, ConversationMetadata } from '@/types';
import { apiService } from './apiService';
import {
  MessageSchema,
  ConversationAnalysisResponseSchema
} from '@/validation/schemas';
import { Citation, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors - keeping for backwards compatibility
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

// Define response types for better type safety
interface ConversationListResponse {
  items: ConversationMetadata[];
  total: number;
  page: number;
  pageSize: number;
}

interface ConversationCreateResponse {
  session_id: string;
  id?: string;
}

export const conversationsApi = {
  /**
   * Create a new conversation
   */
  async createConversation(data: { 
    title: string, 
    document_ids?: string[] 
  }): Promise<string> {
    try {
      const response = await apiService.post<ConversationCreateResponse>(
        '/conversation',
        data
      );
      
      // Extract the session ID from the response
      if (response.session_id) {
        return response.session_id;
      } else if (response.id) {
        // Handle alternative response format
        return response.id;
      } else {
        console.error('Unexpected response format:', response);
        throw new Error('Unexpected response format from conversation creation');
      }
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * List all conversations for the current user
   */
  async listConversations(page: number = 1, pageSize: number = 10): Promise<ConversationListResponse> {
    try {
      const conversations = await apiService.get<ConversationMetadata[]>(
        '/conversation'
      );
      
      // Get the total count (if available in the API)
      let total = conversations.length;
      try {
        const countResponse = await apiService.get<{ count: number }>(
          '/conversation/count'
        );
        total = countResponse.count;
      } catch (error) {
        console.warn('Error getting conversation count, using list length:', error);
      }
      
      // Apply pagination (if not already done by the backend)
      const paginatedItems = Array.isArray(conversations) 
        ? conversations.slice((page - 1) * pageSize, page * pageSize)
        : [];
      
      return {
        items: paginatedItems.map(conv => ({
          id: conv.id || conv.session_id || '',
          title: conv.title || 'Untitled Conversation',
          createdAt: conv.createdAt || new Date().toISOString(),
          updatedAt: conv.updatedAt || new Date().toISOString(),
          documentIds: conv.documentIds || [],
          messageCount: conv.messageCount || 0
        })),
        total,
        page,
        pageSize
      };
    } catch (error) {
      console.error('Error listing conversations:', error);
      return {
        items: [],
        total: 0,
        page,
        pageSize
      };
    }
  },
  
  /**
   * Get conversation history
   */
  async getConversationHistory(sessionId: string, limit: number = 50): Promise<Message[]> {
    try {
      const response = await apiService.get<any[]>(
        `/conversation/${sessionId}/history?limit=${limit}`
      );
      
      // Convert backend format to frontend format if necessary
      return response.map(msg => ({
        id: msg.id,
        sessionId: msg.sessionId || msg.session_id || msg.conversation_id || sessionId,
        timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
        role: msg.role,
        content: msg.content,
        referencedDocuments: msg.referencedDocuments || msg.referenced_documents || [],
        referencedAnalyses: msg.referencedAnalyses || msg.referenced_analyses || [],
        citations: msg.citations || [],
        content_blocks: msg.content_blocks || [],
        analysis_blocks: msg.analysis_blocks || []
      }));
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  },
  
  /**
   * Send a message to the AI assistant
   */
  async sendMessage(
    message: string, 
    sessionId: string, 
    documentIds: string[] = [], 
    citations: Citation[] = []
  ): Promise<Message> {
    try {
      console.log(`Sending message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data
      let documentDataMissing = false;
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            console.log('Referenced document data:', docId, docInfo.extractedData);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentDataMissing = true;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Create data payload for message
      const data = {
        session_id: sessionId,
        content: message,
        referenced_documents: documentIds,
        citation_links: citations.map(c => c.id)
      };
      
      // Send request 
      const response = await apiService.post<any>(
        `/conversation/${sessionId}/message`,
        data
      );
      
      console.log('AI response:', response);
      
      // Convert backend message to frontend format
      const frontendMessage: Message = {
        id: response.id,
        role: response.role,
        content: response.content,
        timestamp: response.timestamp || response.created_at || new Date().toISOString(),
        sessionId: response.sessionId || response.conversation_id || sessionId,
        referencedDocuments: response.referencedDocuments || response.referenced_documents || documentIds,
        referencedAnalyses: response.referencedAnalyses || response.referenced_analyses || [],
        citations: response.citations || []
      };
      
      // If we detected missing document data but the AI didn't mention it, append a note
      if (documentDataMissing && 
          !frontendMessage.content.includes("don't see any") && 
          !frontendMessage.content.toLowerCase().includes("missing") &&
          !frontendMessage.content.toLowerCase().includes("no financial data")) {
        frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
      }
      
      return frontendMessage;
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Provide more helpful error messages
      if (errorMessage.includes('404')) {
        throw new Error('Conversation endpoint not found. The backend API may not be properly configured.');
      }
      
      if (errorMessage.includes('500')) {
        throw new Error('The conversation service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  },
  
  /**
   * Send a message to the AI assistant with streaming response
   */
  async sendMessageStreaming(
    message: string,
    sessionId: string,
    documentIds: string[] = [],
    citations: Citation[] = [],
    callbacks: {
      onChunk: (chunk: any) => void,
      onComplete: (message: Message) => void,
      onError: (error: Error) => void
    }
  ): Promise<void> {
    try {
      console.log(`Sending streaming message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data (same as in non-streaming version)
      let documentDataMissing = false;
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentDataMissing = true;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Create data payload for message
      const data = {
        session_id: sessionId,
        content: message,
        referenced_documents: documentIds,
        citation_links: citations.map(c => c.id),
        stream: true // Explicitly request streaming response
      };
      
      // Store partial content during streaming
      let accumulatedContent = '';
      let messageId: string = '';
      let messageCitations: any[] = [];
      
      // Use the streaming API
      await apiService.stream<any>(
        `/conversation/${sessionId}/message/stream`,
        data,
        // Handle each chunk
        (chunk) => {
          // Different backends might format chunks differently
          const content = chunk.content || chunk.delta || chunk.text || '';
          
          if (content) {
            accumulatedContent += content;
            callbacks.onChunk({
              content,
              full: accumulatedContent
            });
          }
          
          // Some LLM services might include citations in chunks
          if (chunk.citations && Array.isArray(chunk.citations)) {
            messageCitations = [...messageCitations, ...chunk.citations];
          }
          
          // Save message ID if provided
          if (chunk.id && !messageId) {
            messageId = chunk.id;
          }
        },
        // Handle complete message
        (fullResponse) => {
          // Create the final message object
          const frontendMessage: Message = {
            id: messageId || fullResponse.id || `msg-${Date.now()}`,
            role: 'assistant',
            content: accumulatedContent || fullResponse.content || '',
            timestamp: fullResponse.timestamp || fullResponse.created_at || new Date().toISOString(),
            sessionId: fullResponse.sessionId || fullResponse.conversation_id || sessionId,
            referencedDocuments: fullResponse.referencedDocuments || fullResponse.referenced_documents || documentIds,
            referencedAnalyses: fullResponse.referencedAnalyses || fullResponse.referenced_analyses || [],
            citations: messageCitations.length > 0 ? messageCitations : (fullResponse.citations || [])
          };
          
          // Add missing document data warning if needed
          if (documentDataMissing && 
              !frontendMessage.content.includes("don't see any") && 
              !frontendMessage.content.toLowerCase().includes("missing") &&
              !frontendMessage.content.toLowerCase().includes("no financial data")) {
            frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
          }
          
          callbacks.onComplete(frontendMessage);
        },
        // Handle errors
        (error) => {
          console.error('Streaming error:', error);
          
          const errorMessage = error.message || String(error);
          
          // Provide more helpful error messages
          if (errorMessage.includes('404')) {
            callbacks.onError(new Error('Streaming endpoint not found. The backend API may not support streaming or may not be properly configured.'));
          } else if (errorMessage.includes('500')) {
            callbacks.onError(new Error('The conversation service encountered an error during streaming. This might be due to issues with document data or server configuration.'));
          } else {
            callbacks.onError(error);
          }
        }
      );
    } catch (error) {
      console.error('Error initializing message stream:', error);
      callbacks.onError(error instanceof Error ? error : new Error(String(error)));
    }
  },
  
  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      await apiService.post(
        `/conversation/${conversationId}/documents`,
        { document_id: documentId }
      );
    } catch (error) {
      console.error('Error adding document to conversation:', error);
      throw error;
    }
  },
  
  /**
   * Get comprehensive conversation analysis with multiple visualization blocks
   */
  async getConversationAnalysis(sessionId: string): Promise<ConversationAnalysisResponse> {
    try {
      const response = await apiService.get<ConversationAnalysisResponse>(
        `/conversation/${sessionId}/analysis`,
        ConversationAnalysisResponseSchema
      );
      return response;
    } catch (error) {
      console.error('Error getting conversation analysis:', error);
      
      // Return a default/empty response structure
      return {
        sessionId,
        insights: ['Unable to retrieve analysis for this conversation.'],
        visualizationBlocks: []
      };
    }
  },
  
  /**
   * Remove a document from a conversation
   */
  async removeDocumentFromConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      await apiService.delete(
        `/conversation/${conversationId}/documents/${documentId}`
      );
    } catch (error) {
      console.error('Error removing document from conversation:', error);
      throw error;
    }
  },
  
  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await apiService.delete(`/conversation/${conversationId}`);
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },
  
  /**
   * Get document content recommendations based on a message
   */
  async getContentRecommendations(message: string, documentIds: string[] = []): Promise<any> {
    try {
      const response = await apiService.post<any>(
        '/conversation/recommendations',
        {
          content: message,
          document_ids: documentIds
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error getting content recommendations:', error);
      return { recommendations: [] };
    }
  }
};
