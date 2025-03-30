import { Message, ProcessedDocument, AnalysisResult, DocumentUploadResponse } from '../types';
import { mockBackendService } from './mockBackend';
import { Citation, ConversationAnalysisResponse } from '../types/enhanced';
import { z } from 'zod';
import { validate, safeParse } from '../validation/validate';
import {
  ProcessedDocumentSchema,
  MessageSchema,
  AnalysisResultSchema,
  ConversationAnalysisResponseSchema,
  EnhancedAnalysisResultSchema,
  DocumentUploadResponseSchema
} from '../validation/schemas';

// API base URL - would be configured based on environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  /**
   * Send a request to the API with validation
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData,
    schema?: z.ZodType<T>
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
      
      // Validate the response if a schema is provided
      if (schema) {
        return validate(schema, responseData);
      }
      
      return responseData as T;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  /**
   * Upload a document to the server
   */
  async uploadDocument(file: File): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', 'default-user');
      
      // Make the API request to upload the document
      const uploadResponse = await this.request<DocumentUploadResponse>(
        '/documents/upload',
        'POST',
        undefined,
        formData,
        DocumentUploadResponseSchema
      );
      
      // Poll the document status until processing is complete
      const documentId = uploadResponse.document_id;
      let document: ProcessedDocument | null = null;
      let retries = 0;
      const maxRetries = 20; // Increased for potentially longer processing times
      const retryInterval = 1500; // 1.5 seconds
      
      // Poll for document processing
      while (retries < maxRetries) {
        try {
          console.log(`Polling document status: attempt ${retries + 1}/${maxRetries}`);
          
          // Get the document
          const response = await this.request<any>(`/documents/${documentId}`);
          console.log('Document polling response:', response);
          
          // Check if the document has a processing_status field
          if (response.processing_status) {
            // If the document is completed, return it
            if (response.processing_status === 'completed') {
              console.log('Document processing completed');
              
              // Get the document ID from the initial upload response or the polling response
              const documentId = response.document_id || response.metadata?.id;
              
              // Determine appropriate content type
              let contentType = response.content_type || 'unknown';
              // If we have raw text and it contains financial terms, consider it a financial document
              if (response.extracted_data?.raw_text) {
                const rawText = response.extracted_data.raw_text;
                const financialTerms = ['balance sheet', 'income statement', 'cash flow', 'financial', 'assets', 'liabilities', 'equity', 'revenue', 'profit', 'loss'];
                if (financialTerms.some(term => rawText.toLowerCase().includes(term))) {
                  contentType = 'financial_report';
                  console.log('Document detected as financial report based on content');
                }
              }
              
              // Create a properly formatted document with camelCase properties
              document = {
                metadata: {
                  id: documentId || 'unknown',
                  filename: response.metadata?.filename || 'unknown.pdf',
                  uploadTimestamp: response.metadata?.upload_timestamp || new Date().toISOString(),
                  fileSize: response.metadata?.file_size || 0,
                  mimeType: response.metadata?.mime_type || 'application/pdf',
                  userId: response.metadata?.user_id || 'default-user'
                },
                contentType: contentType,
                extractionTimestamp: response.extraction_timestamp || new Date().toISOString(),
                periods: response.periods || [],
                extractedData: response.extracted_data || {},
                confidenceScore: response.confidence_score || 0,
                processingStatus: response.processing_status || 'completed'
              };
              
              console.log('Processed document:', document);
              break;
            } 
            // If the document failed, throw an error
            else if (response.processing_status === 'failed') {
              throw new Error(`Document processing failed: ${response.error_message || 'Unknown error'}`);
            }
            // Otherwise (pending or processing), continue polling
            else {
              console.log(`Document status: ${response.processing_status}`);
            }
          } 
          // If no processing_status field but metadata exists, create a basic document
          else if (response.metadata) {
            // Check if the document is in a usable state for the application
            if (response.content_type) {
              document = {
                metadata: response.metadata,
                contentType: response.content_type,
                extractionTimestamp: response.extraction_timestamp || new Date().toISOString(),
                periods: response.periods || [],
                extractedData: response.extracted_data || {},
                confidenceScore: response.confidence_score || 0,
                processingStatus: 'processing'
              };
            }
          }
          
          retries++;
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryInterval));
          
          // Provide progress updates to console
          if (retries % 5 === 0) {
            console.log(`Still waiting for document processing... (${retries}/${maxRetries})`);
          }
        } catch (error) {
          console.error('Error polling document status:', error);
          retries++;
          
          // If we've reached max retries, throw the error
          if (retries >= maxRetries) {
            throw error;
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
      }
      
      // If we've exhausted retries and don't have a document, create a mock one
      if (!document) {
        console.warn('Document processing not completed within retry limit, returning mock data');
        document = {
          metadata: {
            id: documentId,
            filename: uploadResponse.filename,
            uploadTimestamp: new Date().toISOString(),
            fileSize: 0,
            mimeType: 'application/pdf',
            userId: 'default-user'
          },
          contentType: 'other',
          extractionTimestamp: new Date().toISOString(),
          periods: [],
          extractedData: {},
          confidenceScore: 0.5,
          processingStatus: 'processing'
        };
      }
      
      return document;
    } catch (error) {
      console.error('Error uploading document:', error);
      
      // If we have a document ID but polling failed, return a minimal document to avoid losing track of the upload
      if (uploadResponse?.document_id) {
        console.warn('Upload succeeded but processing status polling failed. Returning minimal document.');
        return {
          metadata: {
            id: uploadResponse.document_id,
            filename: uploadResponse.filename || 'unknown.pdf',
            uploadTimestamp: new Date().toISOString(),
            fileSize: 0,
            mimeType: 'application/pdf',
            userId: 'default-user'
          },
          contentType: 'other',
          extractionTimestamp: new Date().toISOString(),
          periods: [],
          extractedData: {},
          confidenceScore: 0,
          processingStatus: 'processing'
        };
      }
      
      throw error;
    }
  }
  
  /**
   * List documents for the current user
   */
  async listDocuments(page: number = 1, pageSize: number = 10): Promise<{ items: DocumentMetadata[], total: number, page: number, pageSize: number }> {
    try {
      // Call the API to get documents list
      const documents = await this.request<DocumentMetadata[]>(
        `/documents?page=${page}&page_size=${pageSize}`,
        'GET'
      );
      
      // Get the total count
      const countResponse = await this.request<{ count: number }>(
        '/documents/count',
        'GET'
      );
      
      return {
        items: documents,
        total: countResponse.count,
        page,
        pageSize
      };
    } catch (error) {
      console.error('Error listing documents:', error);
      throw error;
    }
  }
  
  /**
   * Get document content URL (PDF file)
   */
  async getDocumentUrl(documentId: string): Promise<string> {
    try {
      // This endpoint would return a URL to the actual PDF file
      // which could be stored in cloud storage or served directly by the API
      const response = await this.request<{url: string}>(
        `/documents/${documentId}/content`,
        'GET'
      );
      
      return response.url;
    } catch (error) {
      console.error('Error getting document URL:', error);
      throw error;
    }
  }
  
  /**
   * Get document citations
   */
  async getDocumentCitations(documentId: string): Promise<Citation[]> {
    try {
      const citations = await this.request<Citation[]>(
        `/documents/${documentId}/citations`,
        'GET'
      );
      
      return citations;
    } catch (error) {
      console.error('Error getting document citations:', error);
      throw new Error(`Failed to get document citations: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Send a message to the AI assistant
   */
  async sendMessage(message: string, sessionId: string, documentIds: string[] = [], citations: any[] = []): Promise<Message> {
    try {
      console.log(`Sending message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data
      let documentDataMissing = false;
      let documentData = null;
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await this.request<any>(`/documents/${docId}`, 'GET');
            console.log('Referenced document data:', docId, docInfo.extracted_data);
            
            // Check if the document has actual financial data
            if (!docInfo.extracted_data || 
                !docInfo.extracted_data.financial_data || 
                Object.keys(docInfo.extracted_data.financial_data).length === 0) {
              documentDataMissing = true;
            } else {
              documentData = docInfo.extracted_data;
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
      
      // Create request schema for validation
      const messageRequestSchema = z.object({
        session_id: z.string(),
        content: z.string(),
        referenced_documents: z.array(z.string()),
        citation_links: z.array(z.string())
      });
      
      // Send request with validation of both request and response data
      const response = await this.request<any>(
        `/conversation/${sessionId}/message`,
        'POST',
        data
      );
      
      console.log('AI response:', response);
      
      // Convert backend message to frontend format
      const frontendMessage: Message = {
        id: response.id,
        role: response.role,
        content: response.content,
        timestamp: response.created_at,
        sessionId: response.conversation_id,
        referencedDocuments: response.referenced_documents || documentIds, // Ensure document references are preserved
        referencedAnalyses: response.referenced_analyses || [],
        citations: response.citations || []
      };
      
      // If we detected missing document data but the AI didn't mention it, append a note
      if (documentDataMissing && !frontendMessage.content.includes("don't see any") && 
          !frontendMessage.content.toLowerCase().includes("missing") &&
          !frontendMessage.content.toLowerCase().includes("no financial data")) {
        frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
      }
      
      return frontendMessage;
    } catch (error: unknown) {
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
  }
  
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(documentIds: string[], analysisType: string): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis on documents: ${JSON.stringify(documentIds)}`);
      
      // First verify documents have processed financial data
      let documentsWithFinancialData = [];
      let documentsWithoutFinancialData = [];
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await this.request<any>(`/documents/${docId}`, 'GET');
            
            // Check if the document has actual financial data
            if (!docInfo.extracted_data || 
                !docInfo.extracted_data.financial_data || 
                Object.keys(docInfo.extracted_data.financial_data).length === 0) {
              documentsWithoutFinancialData.push(docId);
            } else {
              documentsWithFinancialData.push(docId);
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // If no documents have financial data, show diagnostic information
      if (documentsWithFinancialData.length === 0 && documentsWithoutFinancialData.length > 0) {
        console.warn('No documents with financial data found. Cannot run analysis.');
        
        // Generate a mock result with diagnostic information
        return {
          id: `analysis-${Date.now()}`,
          documentIds: documentIds,
          analysisType: analysisType,
          timestamp: new Date().toISOString(),
          metrics: [],
          ratios: [],
          insights: [
            `Unable to perform financial analysis because the document does not contain structured financial data.`,
            `This might be due to one of the following reasons:`,
            `1. The document format is not supported for financial extraction`,
            `2. The document does not contain proper financial statements`,
            `3. The backend extraction service encountered an issue processing the document`
          ],
          visualizationData: {}
        };
      }
      
      // If some documents have financial data, only analyze those
      const dataToAnalyze = documentsWithFinancialData.length > 0 ? documentsWithFinancialData : documentIds;
      
      // Create request data
      const data = {
        document_ids: dataToAnalyze,
        analysis_type: analysisType,
        parameters: {}
      };
      
      // Send request to run analysis
      const response = await this.request<AnalysisResult>(
        '/analysis/run',
        'POST',
        data,
        undefined,
        AnalysisResultSchema
      );
      
      // If some documents were missing financial data, add a warning insight
      if (documentsWithoutFinancialData.length > 0 && response && response.insights) {
        response.insights.unshift(`Note: ${documentsWithoutFinancialData.length} document(s) were excluded from analysis due to missing financial data.`);
      }
      
      return response;
    } catch (error: unknown) {
      console.error('Error running analysis:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // If 404 error, likely an issue with backend route
      if (errorMessage.includes('404')) {
        throw new Error('Analysis endpoint not found. The backend API may not be properly configured.');
      }
      
      // If 405 Method Not Allowed, it's a routing issue
      if (errorMessage.includes('405')) {
        throw new Error('Analysis endpoint method not allowed. Check the backend API route configuration.');
      }
      
      // If 500 error, there might be backend processing issues
      if (errorMessage.includes('500')) {
        throw new Error('The analysis service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  }
  
  /**
   * Get conversation history
   */
  async getConversationHistory(sessionId: string, limit: number = 50): Promise<Message[]> {
    try {
      const response = await this.request<any[]>(
        `/conversation/${sessionId}/history?limit=${limit}`,
        'GET',
        undefined,
        undefined,
        // Use the more flexible schema that accepts the backend format
        undefined
      );
      
      // Convert backend format to frontend format
      const messages: Message[] = response.map(msg => ({
        id: msg.id,
        sessionId: msg.session_id || msg.conversation_id || sessionId,
        timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
        role: msg.role,
        content: msg.content,
        referencedDocuments: msg.referenced_documents || [],
        referencedAnalyses: msg.referenced_analyses || [],
        citations: msg.citations || []
      }));
      
      return messages;
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  }
  
  /**
   * Create a new conversation
   */
  async createConversation(data: { title: string, document_ids?: string[] }): Promise<{ session_id: string }> {
    try {
      // Create request schema for validation
      const conversationCreateSchema = z.object({
        title: z.string(),
        document_ids: z.array(z.string()).optional()
      });
      
      // Use validation for request data
      let validatedData = data;
      if (conversationCreateSchema) {
        const validationResult = safeParse(conversationCreateSchema, data);
        if (!validationResult.success) {
          throw new Error(`Request validation failed: ${validationResult.error}`);
        }
        validatedData = validationResult.data;
      }
      
      // Send request
      const response = await this.request<any>(
        '/conversation',
        'POST',
        validatedData,
        undefined
      );
      
      // Extract the session ID from the response
      if (response && response.session_id) {
        return { session_id: response.session_id };
      } else if (response && response.id) {
        // Handle alternative response format
        return { session_id: response.id };
      } else {
        console.error('Unexpected response format:', response);
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
        'GET',
        undefined,
        undefined,
        // Don't validate with schema, as backend format may vary
        undefined
      );
      
      // Convert backend format to our frontend format
      // The backend might return conversations with session_id or id
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
   * Get enhanced analysis for a specific analysis result
   */
  async getEnhancedAnalysis(analysisId: string): Promise<any> {
    try {
      console.log(`Attempting to get enhanced analysis for ${analysisId}`);
      
      // First try to get the standard analysis result
      const response = await this.request<any>(
        `/analysis/${analysisId}`,
        'GET',
        undefined,
        undefined,
        AnalysisResultSchema
      );
      
      // Add enhanced post-processing to the standard analysis result
      const enhanced = {
        trends: this.generateTrendsFromAnalysis(response),
        insights: this.generateEnhancedInsightsFromAnalysis(response)
      };
      
      return enhanced;
    } catch (error) {
      console.error('Error getting enhanced analysis:', error);
      
      // Give more specific guidance based on error type
      if (error instanceof Error) {
        const errorMessage = error.message || 'Unknown error';
        
        if (errorMessage.includes('Not Found')) {
          console.error(`Analysis with ID ${analysisId} not found in the backend. This could mean:`);
          console.error('1. The analysis was not saved correctly in the database');
          console.error('2. The analysis ID is incorrect');
          console.error('3. The analysis was removed from the database');
        } else if (errorMessage.includes('Internal Server Error')) {
          console.error('Backend server returned a 500 Internal Server Error when retrieving analysis.');
          console.error('Check backend server logs for more details.');
        }
      }
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetEnhancedAnalysis(analysisId);
    }
  }
  
  // Helper methods for enhanced analysis
  private generateTrendsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate trends based on the metrics from the standard analysis
    return analysis.metrics.map(metric => ({
      id: `trend-${Math.random().toString(16).slice(2)}`,
      name: `${metric.name} Trend`,
      description: `Trend analysis for ${metric.name}`,
      value: metric.value,
      change: Math.random() * 0.2 - 0.1, // Random change between -10% and +10%
      direction: Math.random() > 0.5 ? 'increasing' : 'decreasing',
      significance: Math.random() > 0.7 ? 'high' : 'medium',
      category: metric.category
    }));
  }
  
  private generateEnhancedInsightsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate enhanced insights based on the standard analysis
    return analysis.insights.map((insight, index) => ({
      id: `insight-${Math.random().toString(16).slice(2)}`,
      text: insight,
      category: index % 3 === 0 ? 'critical' : index % 3 === 1 ? 'important' : 'informational',
      relatedMetrics: analysis.metrics.slice(0, 2).map(m => m.name),
      confidence: 0.8 + Math.random() * 0.15
    }));
  }
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<any> {
    try {
      const response = await this.request<any>(
        `/analysis/${analysisId}/chart/${chartType}`,
        'GET'
      );
      
      return response;
    } catch (error) {
      console.error('Error getting chart data:', error);
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetChartData(analysisId, chartType);
    }
  }
  
  /**
   * Get comprehensive conversation analysis with multiple visualization blocks
   */
  async getConversationAnalysis(sessionId: string): Promise<ConversationAnalysisResponse> {
    try {
      const response = await this.request<ConversationAnalysisResponse>(
        `/conversation/${sessionId}/analysis`,
        'GET',
        undefined,
        undefined,
        ConversationAnalysisResponseSchema
      );
      
      return response;
    } catch (error) {
      console.error('Error getting conversation analysis:', error);
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetConversationAnalysis(sessionId);
    }
  }
  
  /**
   * Mock method for getting enhanced analysis
   */
  private mockGetEnhancedAnalysis(analysisId: string): any {
    // Use the stored enhanced data if available
    if (this.analysisEnhancements[analysisId]) {
      return this.analysisEnhancements[analysisId];
    }
    
    // Otherwise generate mock data
    return mockBackendService.getEnhancedAnalysis({
      id: analysisId,
      documentIds: [],
      analysisType: 'financial_trends',
      timestamp: new Date().toISOString(),
      metrics: this.generateMockMetrics(),
      ratios: this.generateMockRatios(),
      insights: [
        "Revenue growth remains strong at 12.5% year-over-year.",
        "Operating expenses increased at a manageable rate of 8%.",
        "Profit margin improved by 2.1 percentage points."
      ],
      visualizationData: {
        timeSeriesData: [
          { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
          { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
          { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
          { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
        ]
      }
    });
  }
  
  /**
   * Mock method for getting chart data
   */
  private mockGetChartData(analysisId: string, chartType: string): any {
    const baseData = {
      timeSeriesData: [
        { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
        { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
        { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
        { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
      ]
    };
    
    // Add citation data to chart points
    const chartData = baseData.timeSeriesData.map((dataPoint: any, index: number) => {
      return {
        ...dataPoint,
        citation: {
          id: crypto.randomUUID(),
          text: `${dataPoint.period} financial data`,
          documentId: 'mock-doc-id',
          highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
          page: index + 1,
          rects: [{
            x1: 120,
            y1: 150 + (index * 30),
            x2: 500,
            y2: 170 + (index * 30),
            width: 380,
            height: 20
          }]
        }
      };
    });
    
    return { chartData };
  }
  
  /**
   * Mock method for getting conversation analysis data with multiple blocks
   */
  private mockGetConversationAnalysis(sessionId: string): ConversationAnalysisResponse {
    // Create a unique message ID
    const messageId = crypto.randomUUID();
    
    // Create a shared highlight ID for citations
    const highlightId1 = `highlight-${Math.random().toString(16).slice(2)}`;
    const highlightId2 = `highlight-${Math.random().toString(16).slice(2)}`;
    
    // Generate mock revenue analysis block
    const revenueBlock = {
      id: crypto.randomUUID(),
      title: "Revenue Analysis",
      description: "Quarter-over-quarter revenue growth analysis",
      chartType: "bar" as const,
      chartData: [
        { period: "2022-Q1", revenue: 18.2, prevYearRevenue: 15.3 },
        { period: "2022-Q2", revenue: 19.8, prevYearRevenue: 16.8 },
        { period: "2022-Q3", revenue: 22.3, prevYearRevenue: 18.5 },
        { period: "2022-Q4", revenue: 24.5, prevYearRevenue: 20.1 }
      ],
      insights: [
        {
          text: "Revenue has grown consistently each quarter, with Q4 showing the strongest YoY growth at 21.9%",
          importance: "high" as const,
          categoryTags: ["revenue", "growth"],
          citations: [{
            id: crypto.randomUUID(),
            text: "Revenue has increased by 21.9% compared to the same quarter last year",
            documentId: 'mock-doc-id',
            highlightId: highlightId1,
            page: 2,
            rects: [{
              x1: 120,
              y1: 150,
              x2: 500,
              y2: 170,
              width: 380,
              height: 20
            }]
          }],
          confidenceScore: 0.95
        },
        {
          text: "Average quarterly growth rate was 5.2%, exceeding industry average of 3.8%",
          importance: "medium" as const,
          categoryTags: ["revenue", "benchmark"],
          citations: [],
          confidenceScore: 0.88
        }
      ],
      trends: [{
        metric: "Revenue",
        periods: ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"],
        values: [18.2, 19.8, 22.3, 24.5],
        growthRate: 0.346,
        trendDirection: "up" as const,
        seasonalityDetected: false,
        citations: []
      }],
      timestamp: new Date().toISOString()
    };
    
    // Generate mock profit margin analysis block
    const profitBlock = {
      id: crypto.randomUUID(),
      title: "Profit Margin Analysis",
      description: "Quarterly profit margin trends and benchmarks",
      chartType: "line" as const,
      chartData: [
        { period: "2022-Q1", margin: 15.4, industryAvg: 12.1 },
        { period: "2022-Q2", margin: 15.7, industryAvg: 12.3 },
        { period: "2022-Q3", margin: 17.0, industryAvg: 12.5 },
        { period: "2022-Q4", margin: 17.1, industryAvg: 12.8 }
      ],
      insights: [
        {
          text: "Profit margins have increased every quarter, with a significant jump in Q3 2022",
          importance: "high" as const,
          categoryTags: ["profitability", "trend"],
          citations: [{
            id: crypto.randomUUID(),
            text: "Q3 2022 saw the largest increase in profit margin, growing to 17.0% from 15.7%",
            documentId: 'mock-doc-id',
            highlightId: highlightId2,
            page: 3,
            rects: [{
              x1: 150,
              y1: 180,
              x2: 550,
              y2: 200,
              width: 400,
              height: 20
            }]
          }],
          confidenceScore: 0.92
        },
        {
          text: "Margins have consistently outperformed industry average by approximately 4 percentage points",
          importance: "medium" as const,
          categoryTags: ["profitability", "benchmark"],
          citations: [],
          confidenceScore: 0.85
        }
      ],
      trends: [{
        metric: "Profit Margin",
        periods: ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"],
        values: [15.4, 15.7, 17.0, 17.1],
        growthRate: 0.11,
        trendDirection: "up" as const,
        seasonalityDetected: false,
        citations: []
      }],
      timestamp: new Date().toISOString()
    };
    
    // Create and validate response object
    const mockResponse = {
      messageId,
      sessionId,
      timestamp: new Date().toISOString(),
      analysisBlocks: [revenueBlock, profitBlock]
    };
    
    // Validate the response against our schema
    return validate(ConversationAnalysisResponseSchema, mockResponse);
  }
  
  // ====== MOCK IMPLEMENTATIONS ======
  // These are used as fallbacks if the API is not available
  
  /**
   * Process a document with Claude API to extract content and citations
   * This uses the mock backend service for simulation
   */
  private async processDocumentWithClaude(file: File): Promise<ProcessedDocument> {
    try {
      // Use the mock backend service to process the document
      const claudeResponse = await mockBackendService.processPdfWithClaude(file);
      
      // Convert the Claude response to our ProcessedDocument format
      const document: ProcessedDocument = {
        metadata: {
          id: crypto.randomUUID(),
          filename: file.name,
          uploadTimestamp: new Date().toISOString(),
          fileSize: file.size,
          mimeType: file.type,
          userId: 'mock-user-id',
          citationLinks: claudeResponse.citations.map(c => c.highlightId)
        },
        contentType: claudeResponse.content_type as any,
        extractionTimestamp: new Date().toISOString(),
        periods: claudeResponse.periods,
        extractedData: claudeResponse.extractedData,
        confidenceScore: claudeResponse.confidence,
        processingStatus: 'completed'
      };
      
      // Store citations for later use
      this.storeCitations(document.metadata.id, claudeResponse.citations);
      
      return document;
    } catch (error) {
      console.error('Error processing document with Claude:', error);
      throw error;
    }
  }
  
  // Store citations in-memory (in real app, this would be in a database)
  private citationStore: Record<string, Citation[]> = {};
  
  private storeCitations(documentId: string, citations: Citation[]) {
    this.citationStore[documentId] = citations;
  }
  
  private getCitationsByDocumentId(documentId: string): Citation[] {
    return this.citationStore[documentId] || [];
  }
  
  private mockUploadDocument(file: File): Promise<ProcessedDocument> {
    // Use the enhanced Claude API simulation with the mock backend
    return this.processDocumentWithClaude(file);
  }
  
  private mockSendMessage(message: string, sessionId: string, documentIds: string[] = [], citations: any[] = []): Message {
    // Generate appropriate AI responses based on message content
    const responseContent = this.generateMockResponse(message, documentIds);
    
    // Generate mock citations if none were provided
    const responseCitations = citations.length > 0 ? citations : this.generateMockCitations(responseContent, documentIds);
    
    return {
      id: crypto.randomUUID(),
      sessionId,
      timestamp: new Date().toISOString(),
      role: 'assistant',
      content: responseContent,
      referencedDocuments: documentIds,
      referencedAnalyses: [],
      citations: responseCitations
    };
  }
  
  private async mockRunAnalysis(documentIds: string[], analysisType: string): Promise<AnalysisResult> {
    try {
      // Get document citations for analysis
      const allCitations: Citation[] = [];
      for (const docId of documentIds) {
        const citations = this.getCitationsByDocumentId(docId);
        allCitations.push(...citations);
      }
      
      // Use the mock backend service to run the analysis
      const result = await mockBackendService.runFinancialAnalysis(
        documentIds,
        analysisType
      );
      
      // Enrich the analysis result with enhanced data
      const { trends, insights } = await mockBackendService.getEnhancedAnalysis(result);
      
      // Store the enhanced data for later use (in a real app, this would be in a database)
      this.analysisEnhancements[result.id] = { trends, insights };
      
      return result;
    } catch (error) {
      console.error('Error running mock analysis:', error);
      
      // Fall back to basic mock result
      const result: AnalysisResult = {
        id: crypto.randomUUID(),
        documentIds,
        analysisType,
        timestamp: new Date().toISOString(),
        metrics: this.generateMockMetrics(),
        ratios: this.generateMockRatios(),
        insights: [
          "Operating expenses growing faster than revenue may impact profitability in future quarters.",
          "Liquidity appears stable but below industry average.",
          "Debt-to-equity ratio is favorable compared to industry benchmarks."
        ],
        visualizationData: {
          timeSeriesData: [
            { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
            { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
            { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
            { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
          ]
        },
        citationReferences: {
          "revenue": "page-2-paragraph-3",
          "expenses": "page-4-table-1",
          "profit": "page-6-chart-2"
        }
      };
      
      return result;
    }
  }
  
  // Store enhanced analysis data (in real app, this would be in a database)
  private analysisEnhancements: Record<string, any> = {};
  
  // Helper functions
  private determineContentType(filename: string): ProcessedDocument['contentType'] {
    const lower = filename.toLowerCase();
    if (lower.includes('balance')) return 'balance_sheet';
    if (lower.includes('income')) return 'income_statement';
    if (lower.includes('cash')) return 'cash_flow';
    if (lower.includes('notes')) return 'notes';
    return 'other';
  }
  
  // Generate mock citations for message text with specific document references
  private generateMockCitations(content: string, documentIds: string[] = []): any[] {
    if (documentIds.length === 0) return [];
    
    const documentId = documentIds[0];
    const citations = [];
    
    // Specific citations for revenue analysis
    if (content.includes("Revenue increased by 12.5% year-over-year")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("main drivers for this growth")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "The main drivers for this growth were new product launches (contributing 60% of growth) and expansion into international markets (30% of growth).",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 180,
          x2: 500,
          y2: 200,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("Recurring revenue")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Recurring revenue now represents 72% of total revenue, up from 65% in the previous year.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 3,
        rects: [{
          x1: 120,
          y1: 120,
          x2: 500,
          y2: 140,
          width: 380,
          height: 20
        }]
      });
    }
    
    // Specific citations for profit margin analysis
    if (content.includes("Gross profit margin improved")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Gross profit margin improved to 68.4% in Q4 2022, compared to 64.2% in the same period last year.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 200,
          x2: 500,
          y2: 220,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("Operating profit margin")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Operating profit margin increased by 2.1 percentage points to 17.8%.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 230,
          x2: 450,
          y2: 250,
          width: 330,
          height: 20
        }]
      });
    }
    
    if (content.includes("Net profit margin")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Net profit margin stood at 12.4%, which is 2.2 percentage points above the industry average of 10.2%.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 260,
          x2: 500,
          y2: 280,
          width: 380,
          height: 20
        }]
      });
    }
    
    // If no specific citations matched, fall back to general approach
    if (citations.length === 0) {
      // Find key phrases in the message that could be citations
      const financialTerms = [
        "revenue", "profit margin", "assets", "liabilities", 
        "equity", "debt-to-equity ratio", "ebitda", "operating expenses"
      ];
      
      // Look for these terms in the content
      financialTerms.forEach(term => {
        const termIndex = content.toLowerCase().indexOf(term);
        if (termIndex >= 0) {
          // Get the surrounding context (sentence or phrase)
          const startIndex = Math.max(0, content.lastIndexOf('.', termIndex) + 1);
          const endIndex = content.indexOf('.', termIndex + term.length);
          const citationText = content.substring(
            startIndex, 
            endIndex > 0 ? endIndex + 1 : content.length
          ).trim();
          
          if (citationText.length > 0) {
            citations.push({
              id: crypto.randomUUID(),
              text: citationText,
              documentId: documentId,
              highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
              page: Math.floor(Math.random() * 5) + 1, // Random page number between 1-5
              rects: [{
                x1: 100,
                y1: 100 + (citations.length * 30),
                x2: 500,
                y2: 120 + (citations.length * 30),
                width: 400,
                height: 20
              }]
            });
            
            // Limit to a reasonable number of citations
            if (citations.length >= 3) return;
          }
        }
      });
    }
    
    return citations;
  }
  
  private generateMockResponse(message: string, documentIds: string[]): string {
    const financialTerms = [
      "balance sheet",
      "income statement",
      "cash flow", 
      "revenue",
      "profit margin",
      "assets",
      "liabilities",
      "equity",
      "debt-to-equity ratio",
      "ebitda",
      "operating expenses"
    ];
    
    // Check if message contains financial terms
    const containsFinancialTerm = financialTerms.some(term => 
      message.toLowerCase().includes(term)
    );
    
    if (containsFinancialTerm) {
      const term = financialTerms.find(term => message.toLowerCase().includes(term));
      if (term === "revenue") {
        return `Based on my analysis of your financial document, I can see several key points about your revenue:
      
1. Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.
2. The main drivers for this growth were new product launches (contributing 60% of growth) and expansion into international markets (30% of growth).
3. Recurring revenue now represents 72% of total revenue, up from 65% in the previous year.

The company's revenue growth exceeded industry average (8.3%) by 4.2 percentage points. Would you like me to analyze any specific aspect in more detail?`;
      }
      
      if (term === "profit margin") {
        return `Based on my analysis of your financial document, here are the key points about your profit margins:
      
1. Gross profit margin improved to 68.4% in Q4 2022, compared to 64.2% in the same period last year.
2. Operating profit margin increased by 2.1 percentage points to 17.8%.
3. Net profit margin stood at 12.4%, which is 2.2 percentage points above the industry average of 10.2%.

The margin improvements were primarily driven by economies of scale and more favorable supplier contracts negotiated in Q2 2022. Would you like me to explain any specific aspect in more detail?`;
      }
      
      return `Based on the analysis of your financial document, I can see several key points related to your question about ${term}:
      
1. The document shows significant data in this area from the last 3 fiscal periods.
2. There appears to be a trend that would be worth exploring further.
3. The cited sections on pages 12-14 provide additional context that could be relevant.

Would you like me to generate a visualization of this data or explain any specific aspect in more detail?`;
    }
    
    if (message.toLowerCase().includes("ratio") || message.toLowerCase().includes("analysis")) {
      return `I've analyzed the key financial ratios from your document:

- Current Ratio: 1.8 (industry avg: 2.1)
- Quick Ratio: 1.2 (industry avg: 1.5)
- Debt-to-Equity: 0.85 (industry avg: 0.7)
- Profit Margin: 12.4% (industry avg: 10.2%)

The company appears to have slightly lower liquidity than industry averages but better profitability. Would you like a deeper analysis of any specific ratio?`;
    }
    
    if (message.toLowerCase().includes("summary") || message.toLowerCase().includes("overview")) {
      return `Here's a summary of your financial document:

This appears to be a quarterly financial report for Q3 2023. Key highlights:
- Revenue: $24.5M (↑ 12% YoY)
- Operating Expenses: $18.3M (↑ 8% YoY)
- Net Income: $4.2M (↑ 15% YoY)
- Cash Position: $15.6M (↑ 5% from previous quarter)

The company shows strong growth in both revenue and profitability compared to the same period last year. Cash position remains healthy with a slight increase from Q2 2023.`;
    }
    
    if (message.toLowerCase().includes("visualiz") || message.toLowerCase().includes("chart") || message.toLowerCase().includes("graph")) {
      return `I've prepared a visualization based on the financial data. You can view it in the Analysis tab. The visualization shows the trend of revenue, expenses, and profit over the past 4 quarters. Would you like me to explain any specific aspect of this visualization?`;
    }
    
    // Default response
    return "I understand you're asking about this financial document. Could you be more specific about what aspects you'd like me to analyze? I can help with ratio analysis, trends, cash flow projections, or comparisons to industry benchmarks.";
  }
  
  private generateMockMetrics(): AnalysisResult['metrics'] {
    return [
      {
        category: 'Revenue',
        name: 'Total Revenue',
        period: 'Q4 2022',
        value: 24.5,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Revenue',
        name: 'YoY Growth',
        period: 'Q4 2022',
        value: 12,
        unit: 'percent',
        isEstimated: false
      },
      {
        category: 'Expenses',
        name: 'Operating Expenses',
        period: 'Q4 2022',
        value: 18.3,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Profitability',
        name: 'Net Income',
        period: 'Q4 2022',
        value: 4.2,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Liquidity',
        name: 'Cash Position',
        period: 'Q4 2022',
        value: 15.6,
        unit: 'million USD',
        isEstimated: false
      }
    ];
  }
  
  private generateMockRatios(): AnalysisResult['ratios'] {
    return [
      {
        name: 'Current Ratio',
        value: 1.8,
        description: 'Measures the company\'s ability to pay short-term obligations',
        benchmark: 2.1,
        trend: -0.1
      },
      {
        name: 'Quick Ratio',
        value: 1.2,
        description: 'Measures the company\'s ability to pay short-term obligations using liquid assets',
        benchmark: 1.5,
        trend: -0.05
      },
      {
        name: 'Debt-to-Equity',
        value: 0.85,
        description: 'Measures the company\'s financial leverage',
        benchmark: 0.7,
        trend: 0.03
      },
      {
        name: 'Profit Margin',
        value: 12.4,
        description: 'Measures the company\'s profitability as a percentage of revenue',
        benchmark: 10.2,
        trend: 0.5
      },
      {
        name: 'Return on Assets',
        value: 8.2,
        description: 'Measures how efficiently the company is using its assets to generate profit',
        benchmark: 7.5,
        trend: 0.3
      }
    ];
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<void> {
    try {
      await this.request(
        `/documents/${documentId}`,
        'DELETE'
      );
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  }

  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      console.log(`Adding document ${documentId} to conversation ${conversationId}`);
      await this.request<any>(
        `/conversation/${conversationId}/documents/${documentId}`,
        'POST'
      );
    } catch (error) {
      console.error(`Error adding document to conversation: ${error}`);
      throw error;
    }
  }

  /**
   * A diagnostic method to check backend API health
   * This can be called from the console for debugging
   */
  async checkBackendHealth(): Promise<void> {
    try {
      console.log('Checking backend API health...');
      console.log(`API base URL: ${API_BASE_URL}`);
      
      // Helper function to construct URLs consistently
      const getUrl = (path: string) => {
        // Ensure path starts with /
        const normalizedPath = path.startsWith('/') ? path : `/${path}`;
        
        // Prevent duplicated /api in URLs
        return API_BASE_URL.endsWith('/api') || normalizedPath.startsWith('/api') 
          ? `${API_BASE_URL}${normalizedPath}`
          : `${API_BASE_URL}/api${normalizedPath}`;
      };
      
      // Check if we can connect to the API at all
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Connection timeout')), 5000)
      );
      
      // Try to make a basic request to the API
      const fetchPromise = fetch(`${API_BASE_URL}/`);
      
      // Race the fetch against a timeout
      const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;
      
      if (response.ok) {
        console.log('✅ Basic API connection successful');
      } else {
        console.error('❌ API connection failed:', response.status, response.statusText);
      }
      
      // Try to check specific endpoints
      const endpoints = [
        { method: 'GET', url: '/documents' },
        { method: 'GET', url: '/conversation' },
        { method: 'POST', url: '/analysis/run', body: { document_ids: ["test-id"], analysis_type: 'test', parameters: {} } }
      ];
      
      console.log('Testing specific endpoints:');
      
      for (const endpoint of endpoints) {
        try {
          const options: RequestInit = { 
            method: endpoint.method,
            headers: { 'Accept': 'application/json' }
          };
          
          if (endpoint.body) {
            options.headers = { ...options.headers, 'Content-Type': 'application/json' };
            options.body = JSON.stringify(endpoint.body);
          }
          
          // Use the corrected URL construction
          const resp = await fetch(getUrl(endpoint.url), options);
          
          console.log(`${endpoint.method} ${endpoint.url}: ${resp.status} ${resp.statusText}`);
          
          if (!resp.ok) {
            try {
              const errorText = await resp.text();
              console.log('  Error details:', errorText.substring(0, 200) + (errorText.length > 200 ? '...' : ''));
            } catch (e) {
              console.log('  Could not read error details');
            }
          }
        } catch (e) {
          console.error(`❌ Error testing ${endpoint.method} ${endpoint.url}:`, e);
        }
      }
      
      // Check for available documents
      try {
        console.log('\nChecking for available documents:');
        const documentsResponse = await fetch(getUrl('/documents'));
        
        if (documentsResponse.ok) {
          const documents = await documentsResponse.json();
          
          if (Array.isArray(documents) && documents.length > 0) {
            console.log(`✅ Found ${documents.length} documents:`);
            documents.forEach((doc, index) => {
              console.log(`  ${index + 1}. ID: ${doc.id}, Filename: ${doc.filename}, Status: ${doc.processing_status}`);
            });
          } else {
            console.log('❌ No documents found in the database. You need to upload documents before running analysis.');
          }
        } else {
          console.error('❌ Could not retrieve documents:', documentsResponse.status, documentsResponse.statusText);
        }
      } catch (e) {
        console.error('❌ Error checking documents:', e);
      }
      
      // Check server configuration
      try {
        console.log('\nChecking server configuration:');
        const rootResponse = await fetch(`${API_BASE_URL}/`);
        
        if (rootResponse.ok) {
          const rootInfo = await rootResponse.json();
          console.log('Server info:', rootInfo);
        } else {
          console.error('❌ Could not retrieve server info:', rootResponse.status, rootResponse.statusText);
        }
      } catch (e) {
        console.error('❌ Error checking server configuration:', e);
      }
      
      console.log('\nDiagnostic check complete. If you are experiencing issues:');
      console.log('1. Ensure the backend server is running on the correct port');
      console.log('2. Check that you have uploaded documents before running analysis');
      console.log('3. Verify that the API_BASE_URL is correctly set to:', API_BASE_URL);
    } catch (error) {
      console.error('Error running health check:', error);
    }
  }

  /**
   * Checks if a document has financial data extracted properly
   * @param documentId The ID of the document to check
   * @returns Object with hasFinancialData flag and diagnosis
   */
  async checkDocumentFinancialData(documentId: string): Promise<{ hasFinancialData: boolean; diagnosis: string }> {
    try {
      console.log(`Checking financial data for document: ${documentId}`);
      
      // Get the document details
      const docInfo = await this.request<any>(`/documents/${documentId}`, 'GET');
      console.log('Document data:', docInfo);
      
      // First check if the document processing is complete
      if (docInfo.processing_status !== 'completed') {
        return {
          hasFinancialData: false,
          diagnosis: `Document is still being processed (status: ${docInfo.processing_status}). Please wait for processing to complete.`
        };
      }
      
      // Check if the extracted_data field exists
      if (!docInfo.extracted_data) {
        return {
          hasFinancialData: false,
          diagnosis: "Document has no extracted data. This may indicate a processing failure."
        };
      }
      
      // Check if raw_text was extracted
      const hasRawText = !!(docInfo.extracted_data.raw_text && docInfo.extracted_data.raw_text.length > 0);
      
      // Check if financial_data field exists and has content
      const financialDataExists = !!(docInfo.extracted_data.financial_data);
      const hasFinancialData = financialDataExists && Object.keys(docInfo.extracted_data.financial_data).length > 0;
      
      // Check content type - should be a financial document
      const isFinancialDocument = docInfo.content_type === 'financial_report' || 
                                 docInfo.content_type === 'balance_sheet' || 
                                 docInfo.content_type === 'income_statement' || 
                                 docInfo.content_type === 'cash_flow';
      
      // Log detailed information for debugging
      console.log('Financial data check details:', {
        processingStatus: docInfo.processing_status,
        hasRawText,
        financialDataExists,
        hasFinancialData,
        isFinancialDocument,
        contentType: docInfo.content_type
      });
      
      // Determine diagnosis based on the checks
      let diagnosis = "";
      
      if (!hasRawText) {
        diagnosis = "Document has no extracted text. This may indicate a processing issue or an unreadable PDF.";
      } else if (!financialDataExists) {
        diagnosis = "Document has no financial_data field. This may indicate the backend didn't recognize it as a financial document.";
      } else if (!hasFinancialData) {
        diagnosis = "Document has an empty financial data structure. This indicates the backend recognized it as a financial document but could not extract structured data from it.";
      } else if (!isFinancialDocument) {
        diagnosis = `Document was not classified as a financial document (content_type: ${docInfo.content_type}), but does have financial data.`;
      } else {
        diagnosis = "Document has valid financial data.";
      }
      
      return {
        hasFinancialData,
        diagnosis
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Error checking document financial data:', errorMessage);
      
      return {
        hasFinancialData: false,
        diagnosis: `Error retrieving document: ${errorMessage}`
      };
    }
  }

  /**
   * Verify a document's financial data and optionally trigger re-extraction
   * This method helps diagnose and fix document processing issues
   */
  async verifyDocumentFinancialData(documentId: string, retryExtraction: boolean = false): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`Verifying financial data for document: ${documentId}`);
      
      // First check if the document has financial data
      const checkResult = await this.checkDocumentFinancialData(documentId);
      
      if (checkResult.hasFinancialData) {
        return { success: true, message: "Document already has valid financial data" };
      }
      
      if (!retryExtraction) {
        return { success: false, message: checkResult.diagnosis };
      }
      
      // Trigger re-extraction by calling the process endpoint
      console.log(`Attempting to re-extract financial data for document ${documentId}`);
      
      // Use the process endpoint to trigger re-extraction - fixing the URL construction
      // The request method expects just the endpoint path, not the full URL
      const response = await this.request(
        `/documents/${documentId}/process`,
        'POST',
        {}
      );
      
      return {
        success: true,
        message: "Financial data re-extraction triggered. Please wait for processing to complete."
      };
    } catch (error) {
      console.error("Error verifying document financial data:", error);
      return {
        success: false,
        message: `Error during verification: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Uploads and verifies a document, ensuring it has valid financial data
   * @param file The file to upload
   * @param userId The ID of the user (defaults to 'default-user')
   * @param autoVerify Whether to automatically verify and fix financial data
   * @returns The processed document with financial data
   */
  async uploadAndVerifyDocument(
    file: File, 
    userId: string = 'default-user',
    autoVerify: boolean = true
  ): Promise<ProcessedDocument> {
    try {
      // First upload the document normally
      console.log(`Starting document upload: ${file.name} (${file.size} bytes)`);
      const uploadedDoc = await this.uploadDocument(file);
      console.log(`Document uploaded successfully with ID: ${uploadedDoc.metadata.id}`);
      
      // If auto-verify is disabled, return the document as-is
      if (!autoVerify) {
        console.log('Auto-verification disabled, returning document as-is');
        return uploadedDoc;
      }
      
      // Check if the document has financial data
      console.log(`Verifying financial data for document ${uploadedDoc.metadata.id}...`);
      const checkResult = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
      
      // If it already has financial data, we're done
      if (checkResult.hasFinancialData) {
        console.log(`✅ Document ${uploadedDoc.metadata.id} has valid financial data.`);
        return uploadedDoc;
      }
      
      // Otherwise, try to fix it
      console.log(`⚠️ Document ${uploadedDoc.metadata.id} lacks financial data: ${checkResult.diagnosis}`);
      console.log("Triggering financial data re-extraction...");
      
      try {
        const fixResult = await this.verifyDocumentFinancialData(uploadedDoc.metadata.id, true);
        
        if (fixResult.success) {
          console.log(`Re-extraction triggered successfully: ${fixResult.message}`);
          console.log("Waiting for processing to complete...");
          
          // Wait a moment for processing to take effect
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          try {
            // Get the updated document - using the request method instead of getDocument
            console.log(`Fetching updated document after re-extraction...`);
            const updatedDoc = await this.request<ProcessedDocument>(`/documents/${uploadedDoc.metadata.id}`, 'GET');
            
            // Check again if it has financial data
            console.log(`Verifying if financial data was correctly extracted...`);
            const finalCheck = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
            
            if (finalCheck.hasFinancialData) {
              console.log(`✅ Re-extraction successful! Document now has valid financial data.`);
            } else {
              console.warn(`⚠️ Document still lacks financial data after re-extraction: ${finalCheck.diagnosis}`);
              console.log(`You may need to try again or check the document format.`);
            }
            
            return updatedDoc;
          } catch (fetchError) {
            console.error(`Error fetching updated document:`, fetchError);
            console.log(`Returning original document as fallback.`);
            return uploadedDoc;
          }
        } else {
          console.error(`Failed to trigger re-extraction: ${fixResult.message}`);
          console.log(`Please try again manually or contact support if the issue persists.`);
          return uploadedDoc;
        }
      } catch (fixError) {
        console.error(`Error during verification attempt:`, fixError);
        console.log(`Returning original document as fallback.`);
        return uploadedDoc;
      }
    } catch (error) {
      console.error(`Error in uploadAndVerifyDocument:`, error);
      throw error; // Re-throw to allow the calling function to handle it
    }
  }
}

export const apiService = new ApiService();

// Expose API service to window object for debugging
if (typeof window !== 'undefined') {
  (window as any).api = apiService;
  
  // Add a helpful debug function to verify and fix document financial data
  (window as any).fixDocumentFinancialData = async (documentId: string, options?: any) => {
    console.log(
      '%c📊 Document Financial Data Verification',
      'background: #edf8ff; color: #0066cc; font-size: 14px; font-weight: bold; padding: 8px; border-radius: 4px; margin: 8px 0;'
    );
    console.log(`Starting financial data verification for document: ${documentId}`);
    try {
      const result = await apiService.ensureDocumentFinancialData(documentId, options);
      
      console.log(
        '%c=== Financial Data Verification Result ===',
        'color: #333; font-size: 12px; font-weight: bold; padding: 4px 0;'
      );
      
      console.log(
        `%cDocument ID: ${result.documentId}`,
        'color: #555; font-size: 12px;'
      );
      
      const initialStatusStyle = result.initialStatus.hasFinancialData 
        ? 'color: #22c55e; font-size: 12px;' 
        : 'color: #f43f5e; font-size: 12px;';
      
      console.log(
        `%cInitial Status: ${result.initialStatus.hasFinancialData ? '✅ Has financial data' : '❌ No financial data'}`,
        initialStatusStyle
      );
      
      if (!result.initialStatus.hasFinancialData) {
        console.log(
          `%cInitial Diagnosis: ${result.initialStatus.diagnosis}`,
          'color: #f43f5e; font-size: 12px; font-style: italic;'
        );
      }
      
      if (result.reprocessingAttempted) {
        const reprocessingStyle = result.reprocessingResult?.success 
          ? 'color: #22c55e; font-size: 12px;' 
          : 'color: #f43f5e; font-size: 12px;';
        
        console.log(
          `%cReprocessing: ${result.reprocessingResult?.success ? '✅ Success' : '❌ Failed'}`,
          reprocessingStyle
        );
        
        console.log(
          `%cReprocessing Message: ${result.reprocessingResult?.message}`,
          'color: #555; font-size: 12px;'
        );
        
        const finalStatusStyle = result.finalStatus.hasFinancialData 
          ? 'color: #22c55e; font-size: 12px;' 
          : 'color: #f43f5e; font-size: 12px;';
        
        console.log(
          `%cFinal Status: ${result.finalStatus.hasFinancialData ? '✅ Has financial data' : '❌ No financial data'}`,
          finalStatusStyle
        );
        
        if (!result.finalStatus.hasFinancialData) {
          console.log(
            `%cFinal Diagnosis: ${result.finalStatus.diagnosis}`,
            'color: #f43f5e; font-size: 12px; font-style: italic;'
          );
        }
      }
      
      const overallStyle = result.success 
        ? 'background: #dcfce7; color: #166534; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 4px; margin: 8px 0;' 
        : 'background: #fee2e2; color: #991b1b; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 4px; margin: 8px 0;';
      
      console.log(
        `%cOverall Result: ${result.success ? '✅ Success' : '❌ Failed'}`,
        overallStyle
      );
      
      if (result.document) {
        console.log('Document:', result.document);
      }
      
      return result;
    } catch (error) {
      console.error('%cError fixing document financial data:', 'color: #991b1b; font-weight: bold;', error);
      return { success: false, error };
    }
  };
  
  // Add instructions for console use
  console.log(
    '%c📊 Financial Data Verification Tools Available!',
    'background: #edf8ff; color: #0066cc; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px;'
  );
  console.log(
    '%cUse window.fixDocumentFinancialData(documentId) to verify and fix document financial data\nExample: fixDocumentFinancialData("1234-5678-90ab-cdef")',
    'color: #555; font-size: 11px;'
  );
}