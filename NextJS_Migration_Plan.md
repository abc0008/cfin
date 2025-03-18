# FDAS Frontend Migration: Sprint Breakdown

This document breaks down the NextJS migration implementation plan into discrete, actionable stories for the development team.

## Critical PDF Upload and Viewing Functionality

After analyzing the existing Vite implementation and comparing it with the current NextJS codebase against the project requirements, we've identified these three stories as the most critical for ensuring PDF upload and viewing functionality works correctly:

### 1. Story 4.1: PDF Viewer Component with Citation Support

**Current Status:**
- The Vite implementation has a fully functional PDFViewer with react-pdf-highlighter integration
- Current NextJS implementation has a basic PDFViewer but lacks citation fetching and backend integration
- Citation highlighting is central to the project requirements but incomplete in NextJS version

**Detailed Tasks:**
- [x] Integrate react-pdf-highlighter with proper document loading in NextJS
- [x] Implement citation fetch service to retrieve and display AI-generated citations
- [x] Create highlight management system to track both user and AI highlights
- [x] Implement citation navigation with scrolling to specific highlights
- [x] Add visual differentiation between user highlights and AI citations
- [x] Create PDFViewService to handle URL retrieval and document loading
- [x] Add error handling with retry logic for PDF loading failures
- [x] Implement proper memory management for large PDFs

**Technical Implementation:**
```typescript
// src/lib/pdf/citationService.ts
export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  }>;
  messageId?: string;
  analysisId?: string;
}

export const convertCitationToHighlight = (citation: Citation): IHighlight => {
  return {
    id: citation.highlightId,
    content: {
      text: citation.text
    },
    position: {
      boundingRect: citation.rects[0] || {
        x1: 0, y1: 0, x2: 0, y2: 0, width: 0, height: 0
      },
      rects: citation.rects,
      pageNumber: citation.page
    },
    comment: {
      text: citation.text,
      emoji: "📝"
    }
  };
};

// In PDFViewer component:
useEffect(() => {
  if (document) {
    const fetchDocumentData = async () => {
      try {
        // Get document URL from API
        const url = await documentsApi.getDocumentUrl(document.metadata.id);
        setPdfUrl(url);
        
        // Fetch citations for the document
        const citations = await documentsApi.getDocumentCitations(document.metadata.id);
        
        // Convert citations to highlight format
        const highlightsFromCitations = citations.map(convertCitationToHighlight);
        
        if (onCitationsLoaded) {
          onCitationsLoaded(highlightsFromCitations);
        }
      } catch (error) {
        console.error("Error loading document:", error);
        setErrorState("Failed to load document. Please try again later.");
      }
    };
    
    fetchDocumentData();
  }
}, [document]);
```

**Integration Points:**
- Must connect with the DocumentAPI service for retrieving PDF URL and citations
- Should integrate with the SessionContext for tracking active document and highlights
- Needs to integrate with ChatInterface to highlight citations referenced in conversation
- Must work with the Analysis components to highlight data source citations

### 2. Story 1.2: Document API Service Integration

**Current Status:**
- Vite implementation has a comprehensive API service for document operations
- Current NextJS implementation has basic document API but lacks citation management and validation
- PDF upload verification and financial data extraction are missing in NextJS implementation

**Detailed Tasks:**
- [x] Implement robust document upload API with FormData and progress tracking
- [x] Create document URL retrieval service for secure PDF access
- [x] Add citation management APIs (creation, retrieval, linking)
- [x] Implement financial data verification service with diagnostics
- [x] Create document metadata service with citation linking support
- [x] Add comprehensive error handling for all document operations
- [x] Implement caching strategy for documents and citations
- [x] Add retry logic for intermittent API failures

**Technical Implementation:**
```typescript
// src/lib/api/documents.ts
export const documentsApi = {
  /**
   * Uploads a document and verifies it has valid financial data
   */
  async uploadAndVerifyDocument(file: File): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Step 1: Upload the document
      const uploadResponse = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }
      
      const uploadData: DocumentUploadResponse = await uploadResponse.json();
      console.log('Document uploaded:', uploadData);
      
      // Step 2: Poll for document processing completion
      const documentId = uploadData.document_id;
      let processingComplete = false;
      let document: ProcessedDocument | null = null;
      let attempts = 0;
      const maxAttempts = 20;
      
      while (!processingComplete && attempts < maxAttempts) {
        attempts++;
        
        // Wait before polling again
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Check document status
        const statusResponse = await fetch(`${API_BASE_URL}/documents/${documentId}`);
        
        if (!statusResponse.ok) {
          if (statusResponse.status === 404) {
            console.log(`Document ${documentId} not found yet, retrying...`);
            continue;
          }
          
          const errorData = await statusResponse.json();
          throw new Error(errorData.detail || 'Failed to check document status');
        }
        
        const statusData = await statusResponse.json();
        
        // If document processing is complete or failed, exit the loop
        if (statusData.processing_status === 'completed' || statusData.processing_status === 'failed') {
          processingComplete = true;
          
          document = {
            metadata: {
              id: statusData.document_id || documentId,
              filename: statusData.metadata?.filename || file.name,
              uploadTimestamp: statusData.metadata?.upload_timestamp || new Date().toISOString(),
              fileSize: statusData.metadata?.file_size || file.size,
              mimeType: statusData.metadata?.mime_type || file.type,
              userId: statusData.metadata?.user_id || 'current-user',
              citationLinks: statusData.citation_links || []
            },
            contentType: statusData.content_type || 'other',
            extractionTimestamp: statusData.extraction_timestamp || new Date().toISOString(),
            periods: statusData.periods || [],
            extractedData: statusData.extracted_data || {},
            confidenceScore: statusData.confidence_score || 0,
            processingStatus: statusData.processing_status,
            errorMessage: statusData.error_message
          };
        }
      }
      
      if (!document) {
        throw new Error('Document processing timed out');
      }
      
      // Step 3: Verify financial data
      const verificationResult = await this.checkDocumentFinancialData(documentId);
      console.log('Financial data verification:', verificationResult);
      
      // Include verification result in the document
      document.extractedData.financialVerification = verificationResult;
      
      return document;
    } catch (error) {
      console.error('Error uploading and verifying document:', error);
      throw error;
    }
  },
  
  /**
   * Gets the URL for viewing a document
   */
  async getDocumentUrl(documentId: string): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}/url`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get document URL');
      }
      
      const data = await response.json();
      return data.url;
    } catch (error) {
      console.error('Error getting document URL:', error);
      throw error;
    }
  },
  
  /**
   * Gets citations for a document
   */
  async getDocumentCitations(documentId: string): Promise<Citation[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}/citations`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get document citations');
      }
      
      const data = await response.json();
      return data.citations;
    } catch (error) {
      console.error('Error getting document citations:', error);
      throw error;
    }
  }
  
  // ... other methods as needed
};
```

**Integration Points:**
- Must handle complex document upload with polling for processing status
- Should integrate with SessionContext to update application state
- Needs to maintain citation relationships between documents and messages
- Must work with financial data verification
- Should have retry and error recovery mechanisms

### 3. Story 2.1: Enhanced Upload Form with Verification

**Current Status:**
- Vite implementation has a comprehensive upload form with financial data verification
- Current NextJS implementation has basic form but lacks proper verification integration
- Progress tracking and error handling need enhancement in NextJS version

**Detailed Tasks:**
- [x] Enhance UploadForm component with real progress tracking
- [x] Implement client-side file validation (size, type, content)
- [x] Add financial data verification state and feedback
- [x] Create proper error handling with user-friendly messages
- [x] Implement drag-and-drop file selection with preview
- [x] Add upload cancellation support
- [x] Create upload success/failure notifications
- [x] Implement upload retry logic for failed uploads

**Technical Implementation:**
```typescript
// Enhance UploadForm.tsx with real upload progress and verification
const handleUpload = async () => {
  if (!file) return;
  
  try {
    setIsUploading(true);
    setError(null);
    
    // Track upload progress
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);
    
    // Set up progress tracking
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        // Only go to 75% for upload - reserve 75-100% for processing & verification
        const uploadProgress = (event.loaded / event.total) * 75;
        setProgress(uploadProgress);
      }
    };
    
    // Create a promise to handle XHR response
    const uploadPromise = new Promise<DocumentUploadResponse>((resolve, reject) => {
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      };
      
      xhr.onerror = () => reject(new Error('Network error during upload'));
      xhr.onabort = () => reject(new Error('Upload was aborted'));
    });
    
    // Open and send the request
    xhr.open('POST', `${API_BASE_URL}/documents/upload`);
    xhr.send(formData);
    
    // Wait for upload to complete
    const uploadResponse = await uploadPromise;
    console.log('Upload complete, starting verification:', uploadResponse);
    
    // Update progress to indicate verification has started
    setProgress(80);
    
    // Use the document API to verify the upload and wait for processing
    console.log("Starting document processing and financial data verification...");
    const document = await documentsApi.uploadAndVerifyDocument(file);
    
    // Document processing and verification complete
    setProgress(100);
    console.log("Document verification completed:", document);
    
    // Check if the document has financial data
    const hasFinancialData = document.extractedData.financialVerification?.hasFinancialData;
    const diagnosis = document.extractedData.financialVerification?.diagnosis;
    
    if (!hasFinancialData) {
      // Document doesn't have financial data - show warning but still allow
      console.warn("Document doesn't have valid financial data:", diagnosis);
      setWarning(`The document was processed but may not contain valid financial data: ${diagnosis}`);
    } else {
      setWarning(null);
    }
    
    // Notify parent component of successful upload
    onUploadSuccess?.(document);
    
    // Reset form after short delay to show 100% completion
    setTimeout(() => {
      setFile(null);
      setProgress(0);
      setIsUploading(false);
    }, 1000);
    
  } catch (err) {
    console.error("Document upload failed:", err);
    setError((err as Error).message || 'Failed to upload document');
    setIsUploading(false);
    setProgress(0);
    onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
  }
};
```

**Integration Points:**
- Must integrate with DocumentAPI service for upload and verification
- Should update UI based on backend processing status
- Needs to handle large file uploads efficiently
- Must provide clear feedback on financial data extraction
- Should integrate with notification system for success/failure alerts

## Sprint 1: Core API & Document Handling

### Epic 1: API Service Infrastructure

#### Story 1.1: API Service Base Implementation
- [x] Setup API service base configuration and error handling
- [x] Implement API request utility with proper validation
- [x] Create environment variable configuration for API endpoints
- [x] Add comprehensive error handling with consistent error messages

<IMPORTANT_NOTES>
- Current NextJS implementation has separate API modules in `/lib/api/` folder (documents.ts, conversation.ts)
- These need to be consolidated into a more robust approach similar to the Vite implementation
- The API base URL is set using NEXT_PUBLIC_API_URL environment variable, defaulting to http://localhost:8000/api
- Need to preserve the existing error handling strategy but make it more consistent
- Should include Zod validation like in the Vite implementation
- API service should handle authentication tokens and headers automatically when they're implemented
</IMPORTANT_NOTES>

#### Story 1.2: Document API Service Integration
- [x] Implement document upload API with progress tracking
- [x] Add document listing and filtering functionality
- [x] Create document detail fetching service
- [x] Implement document deletion service with confirmation
- [x] Add financial data verification service

<IMPORTANT_NOTES>
- Current implementation has documentsApi.uploadAndVerifyDocument which must be preserved
- Need to support file upload with FormData and multipart/form-data content type
- Progress tracking is currently simulated but should be enhanced for real tracking
- Document financial data verification is critical and must be preserved
- API endpoints to implement: 
  - POST /api/documents/upload
  - GET /api/documents
  - GET /api/documents/{document_id}
  - DELETE /api/documents/{document_id}
  - GET /api/documents/count
</IMPORTANT_NOTES>

#### Story 1.3: Conversation API Service Integration
- [x] Implement conversation creation service
- [x] Add message sending API with citation support
- [x] Create conversation history retrieval service
- [x] Implement session management helpers

<IMPORTANT_NOTES>
- Conversation API needs to handle citations in message responses
- Session management is critical as it ties conversations to documents
- API endpoints to implement:
  - POST /api/conversation/create
  - POST /api/conversation/{session_id}/message
  - GET /api/conversation/{session_id}/history
</IMPORTANT_NOTES>

#### Story 1.4: Analysis API Service Integration
- [x] Implement analysis request service
- [x] Add analysis results retrieval service
- [x] Create analysis export functionality
- [x] Implement analysis sharing capabilities

<IMPORTANT_NOTES>
- Analysis service must handle potentially long-running operations
- Need to support polling for analysis status until completion
- Results may include structured data for visualizations
- API endpoints to implement:
  - POST /api/analysis/run
  - GET /api/analysis/{analysis_id}
</IMPORTANT_NOTES>

### Epic 2: Document Management

#### Story 2.1: Enhanced Upload Form
- [x] Migrate UploadForm component with progress indication
- [x] Add file validation and size restrictions
- [x] Implement error handling and user feedback
- [x] Add drag-and-drop file selection

<IMPORTANT_NOTES>
- Current UploadForm.tsx already has most functionality but needs refinement
- Form should validate PDF files only with 10MB size limit
- Progress indicator is currently simulated (0-75% upload, 75-90% verification)
- Should utilize the documentsApi.uploadAndVerifyDocument method
- Need to preserve the financial data verification step
</IMPORTANT_NOTES>

#### Story 2.2: Document List Component
- [ ] Create DocumentList component with sorting and filtering
- [ ] Implement document selection functionality
- [ ] Add document metadata display
- [ ] Create document action menu (delete, share, etc.)

<IMPORTANT_NOTES>
- DocumentList.tsx exists but needs to be enhanced
- Selection functionality should update application state in SessionContext
- Should support sorting by upload date, name, size
- Metadata display should include file type, size, upload date
</IMPORTANT_NOTES>

### Epic 3: Application State Management

#### Story 3.1: Session Context Provider
- [ ] Create SessionContext with document, conversation, and analysis state
- [ ] Implement state persistence between page navigation
- [ ] Add user preference management
- [ ] Create loading and error state management

<IMPORTANT_NOTES>
- SessionContext should be applied at the layout level to persist across routes
- State should include active document(s), current conversation session, user preferences
- Need to handle loading states for async operations
- Consider using React Context API with useReducer for complex state
</IMPORTANT_NOTES>

## Sprint 2: Document Viewer & Citation Integration

### Epic 4: PDF Viewing Capabilities

#### Story 4.1: PDF Viewer Component
- [x] Implement PDF rendering with react-pdf-highlighter
- [x] Add pagination and zoom controls
- [x] Create citation highlight overlay system
- [x] Implement search within document functionality

<IMPORTANT_NOTES>
- Current PDFViewer.tsx needs to be integrated with react-pdf-highlighter
- Highlighter needs to support different colors for different citation sources
- Should handle PDF loading states and errors gracefully
- Need to manage highlights state within component and in SessionContext
</IMPORTANT_NOTES>

#### Story 4.2: Citation Management System
- [x] Create citation data structure and types
- [x] Implement citation extraction from API responses
- [x] Add citation navigation system within documents
- [x] Create citation highlight rendering with tooltips

<IMPORTANT_NOTES>
- Citations should follow Anthropic's citation format
- Each citation needs unique ID, page number, text snippet, and bounding box
- Navigation system should allow jumping to citation location in document
- Tooltips should show source information and context
</IMPORTANT_NOTES>

## Sprint 3: Conversation Interface

### Epic 5: Chat Functionality

#### Story 5.1: Chat Interface Enhancement
- [x] Implement ChatInterface with API integration
- [x] Add citation display in messages
- [x] Create typing indicators and loading states
- [x] Implement error handling and retry mechanisms

<IMPORTANT_NOTES>
- Current ChatInterface.tsx needs to be connected to the API
- Messages should maintain history and display citations as linked references
- Need to handle different message types (user, assistant, system)
- Typing indicators should provide feedback during AI response generation
</IMPORTANT_NOTES>

#### Story 5.2: Message Formatting & Citations
- [x] Create rich text rendering for messages
- [x] Implement citation linking to document locations
- [x] Add support for code blocks and formatting
- [x] Create expandable/collapsible sections for long responses
- [x] Add automated financial term recognition with explanations
- [x] Implement copy functionality for message content
- [x] Create message reference linking between related responses

<IMPORTANT_NOTES>
- Messages may contain markdown or HTML that needs proper rendering
- Citations should be clickable and highlight corresponding document sections
- Code blocks should have syntax highlighting
- Interactive elements might include buttons, forms, or expandable sections
</IMPORTANT_NOTES>

## Sprint 4: Analysis & Visualization

### Epic 6: Financial Analysis

#### Story 6.1: Analysis Block Component
- [ ] Implement AnalysisBlock with API integration
- [ ] Add visualization rendering with Recharts
- [ ] Create citation linking in analysis results
- [ ] Implement interactive data exploration

<IMPORTANT_NOTES>
- Analysis results need to be rendered with appropriate charts based on data type
- Charts should be interactive and responsive
- Citations in analysis should link back to source material
- Need to handle different analysis types (ratios, trends, comparisons)
</IMPORTANT_NOTES>

#### Story 6.2: Canvas Integration
- [ ] Create Canvas component for visualization layout
- [ ] Implement responsive layout management
- [ ] Add visualization export functionality
- [ ] Create customization options for visualizations

<IMPORTANT_NOTES>
- Canvas should support different layout modes and responsive design
- Export options should include PNG, PDF, and possibly CSV data
- Customization should allow changing chart types, colors, and data filters
- Should integrate with the SessionContext for state management
</IMPORTANT_NOTES>

## Sprint 5: Integration & Polish

### Epic 7: Workspace Integration

#### Story 7.1: Workspace Layout
- [ ] Implement tab-based workspace navigation
- [ ] Create document, chat, and analysis panels
- [ ] Add responsive layout for different screen sizes
- [ ] Implement state preservation between tabs

<IMPORTANT_NOTES>
- Workspace layout should follow the design in the project requirements
- Tab navigation should maintain component state when switching
- Responsive design should adapt to desktop, tablet, and mobile
- State should be preserved in SessionContext when navigating
</IMPORTANT_NOTES>

#### Story 7.2: Error Handling & Performance
- [ ] Implement comprehensive error boundaries
- [ ] Add performance optimizations for large documents
- [ ] Create client-side caching mechanisms
- [ ] Implement analytics and error logging

<IMPORTANT_NOTES>
- Error boundaries should catch and display user-friendly error messages
- Performance optimizations should focus on PDF rendering and large datasets
- Caching should reduce API calls for frequently accessed data
- Analytics should track user interactions and feature usage
</IMPORTANT_NOTES>

#### Story 7.3: Final Integration & Testing
- [ ] Complete end-to-end testing of all workflows
- [ ] Perform cross-browser compatibility testing
- [ ] Conduct performance benchmarking
- [ ] Create documentation for the migrated application

<IMPORTANT_NOTES>
- Test all critical user flows: upload → view → chat → analyze
- Ensure compatibility with Chrome, Firefox, Safari, and Edge
- Performance benchmarks should focus on document loading and analysis generation
- Documentation should include setup instructions and architecture overview
</IMPORTANT_NOTES>

## Critical Conversation Service and LLM Functionality

After analyzing the existing Vite implementation and comparing it with the current NextJS codebase against the project requirements, I've identified these three critical stories for ensuring the conversation service and LLM functionality work correctly:

### 1. Story 5.1: Enhanced Chat Interface with Citation Integration

**Current Status:**
- The Vite implementation has a comprehensive ChatInterface with citation display and document referencing
- Current NextJS implementation has basic messaging but lacks citation linking and document integration
- Real-time response handling and financial data verification are missing in NextJS version

**Detailed Tasks:**
- [x] Implement robust message state management with proper history retrieval
- [x] Create citation display system with highlight linking
- [x] Integrate document reference tracking for contextual responses
- [x] Add message streaming capability with typing indicators
- [x] Implement error handling specific to LLM context limitations
- [x] Add citation navigation between messages and documents
- [x] Implement conversation persistence across page navigation
- [x] Implement financial data verification during conversation

**Technical Implementation:**
```typescript
// Enhanced Chat Interface with document integration and citation handling
const ChatInterface = ({ messages, setMessages, onCitationClick }: ChatInterfaceProps) => {
  const { sessionId, documents = [] } = useSession();
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Load conversation history when session changes
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!sessionId) return;
      
      setIsLoadingHistory(true);
      
      try {
        // Clear current messages
        setMessages([]);
        
        // Add a loading message
        const loadingMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: sessionId,
          timestamp: new Date().toISOString(),
          role: 'system',
          content: "Loading conversation history...",
          referencedDocuments: [],
          referencedAnalyses: []
        };
        
        setMessages([loadingMessage]);
        
        // Get conversation history
        const history = await conversationApi.getConversationHistory(sessionId);
        
        // If we have history, set it
        if (history && history.length > 0) {
          setMessages(history);
        } else {
          // Otherwise clear the loading message
          setMessages([]);
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
        toast.error('Failed to load conversation history');
        setMessages([{
          id: crypto.randomUUID(),
          sessionId,
          timestamp: new Date().toISOString(),
          role: 'system',
          content: "Failed to load conversation history. You can start a new conversation.",
          referencedDocuments: [],
          referencedAnalyses: []
        }]);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    
    loadConversationHistory();
  }, [sessionId, setMessages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing || isLoadingHistory) return;

    // Get referenced document IDs from the session context
    const documentIds = documents.map(doc => doc.metadata.id);
    
    // User message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      sessionId: sessionId,
      timestamp: new Date().toISOString(),
      role: 'user',
      content: input,
      referencedDocuments: documentIds,
      referencedAnalyses: []
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    // Add typing indicator
    const typingIndicatorId = crypto.randomUUID();
    const typingMessage: Message = {
      id: typingIndicatorId,
      sessionId: sessionId,
      timestamp: new Date().toISOString(),
      role: 'system',
      content: "AI is thinking...",
      isTypingIndicator: true,
      referencedDocuments: [],
      referencedAnalyses: []
    };
    
    setMessages(prev => [...prev, typingMessage]);
    
    try {
      // Get AI response from the API service
      const response = await conversationApi.sendMessage(
        input,
        sessionId,
        documentIds
      );
      
      // Remove typing indicator and add the response
      setMessages(prev => [
        ...prev.filter(m => m.id !== typingIndicatorId),
        response
      ]);
      
      // Handle citations if present
      if (response.citations && response.citations.length > 0) {
        console.log('Message contains citations:', response.citations);
        // Notify parent component about citations for highlighting
        if (onCitationClick && response.citations[0].highlightId) {
          onCitationClick(response.citations[0].highlightId);
        }
      }
    } catch (error) {
      // Remove typing indicator
      setMessages(prev => prev.filter(m => m.id !== typingIndicatorId));
      
      // Add error message
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
        role: 'assistant',
        content: error instanceof Error 
          ? `I'm sorry, I encountered an error: ${error.message}`
          : "I'm sorry, I encountered an error while processing your request. Please try again.",
        referencedDocuments: [],
        referencedAnalyses: []
      };
      
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Error sending message');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Message component with citation display
  const MessageComponent = ({ message }: { message: Message }) => {
    // Render message with citations...
    return (
      <div className={`message ${message.role}`}>
        <div className="content">
          {renderMessageWithCitations(message.content, message.citations)}
        </div>
        {message.citations && message.citations.length > 0 && (
          <div className="citations">
            <h4>Citations</h4>
            {message.citations.map(citation => (
              <div 
                key={citation.id} 
                className="citation"
                onClick={() => onCitationClick && onCitationClick(citation.highlightId)}
              >
                {citation.text.substring(0, 100)}...
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };
};
```

**Integration Points:**
- Must connect with the ConversationAPI for message sending and history retrieval
- Should integrate with SessionContext for document referencing
- Needs to work with PDFViewer for citation highlighting
- Must handle message streaming and typing indicators
- Should include proper error handling and recovery

### 2. Story 1.3: Conversation API Service Implementation

**Current Status:**
- Vite implementation has robust conversation API with session management and citation handling
- Current NextJS implementation has basic messaging but lacks proper session management
- Vite version handles document references and financial data verification that NextJS lacks

**Detailed Tasks:**
- [x] Implement conversation creation with proper session management
- [x] Create message sending API with document referencing
- [x] Implement conversation history retrieval with pagination
- [x] Add citations extraction and management
- [x] Create document reference tracking between conversations
- [x] Implement financial data verification during conversations
- [x] Add error handling for LLM context limitations
- [x] Create conversation export and sharing functionality

**Technical Implementation:**
```typescript
// src/lib/api/conversation.ts
export const conversationApi = {
  /**
   * Create a new conversation session
   */
  async createConversation(title: string, documentIds: string[] = []): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversation/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          document_ids: documentIds
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create conversation');
      }

      const data = await response.json();
      return data.session_id;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  /**
   * Send a message to the AI assistant
   */
  async sendMessage(
    message: string, 
    sessionId: string, 
    documentIds: string[] = []
  ): Promise<Message> {
    try {
      // Check if documents have valid financial data
      let documentDataMissing = false;
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docResponse = await fetch(`${API_BASE_URL}/documents/${docId}`);
            if (!docResponse.ok) continue;
            
            const docInfo = await docResponse.json();
            
            // Check if the document has actual financial data
            if (!docInfo.extracted_data || 
                !docInfo.extracted_data.financial_data || 
                Object.keys(docInfo.extracted_data.financial_data).length === 0) {
              documentDataMissing = true;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Send the message
      const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: message,
          referenced_documents: documentIds
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();
      
      // Format the response as a Message object
      const formattedMessage: Message = {
        id: data.id,
        sessionId: data.conversation_id || sessionId,
        timestamp: data.created_at || new Date().toISOString(),
        role: data.role,
        content: data.content,
        referencedDocuments: data.referenced_documents || documentIds,
        referencedAnalyses: data.referenced_analyses || [],
        citations: data.citations || []
      };
      
      // Add warning if document data missing
      if (documentDataMissing && 
          !formattedMessage.content.includes("don't see any") && 
          !formattedMessage.content.toLowerCase().includes("missing") &&
          !formattedMessage.content.toLowerCase().includes("no financial data")) {
        formattedMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data.";
      }
      
      return formattedMessage;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Get conversation history
   */
  async getConversationHistory(sessionId: string, limit: number = 50): Promise<Message[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}/history?limit=${limit}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get conversation history');
      }

      const data = await response.json();
      
      // Convert API response to Message objects
      return data.map((msg: any) => ({
        id: msg.id,
        sessionId: msg.session_id || msg.conversation_id || sessionId,
        timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
        role: msg.role,
        content: msg.content,
        referencedDocuments: msg.referenced_documents || [],
        referencedAnalyses: msg.referenced_analyses || [],
        citations: msg.citations || []
      }));
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  }
};
```

**Integration Points:**
- Must handle complex session management with document references
- Should verify financial data in referenced documents
- Needs to extract and format citations from AI responses
- Must handle LLM context limitations and errors
- Should integrate with SessionContext to maintain state

### 3. Story 5.2: Message Formatting with Citation Linking

**Current Status:**
- Vite implementation has markdown rendering with citation highlighting and document references
- Current NextJS implementation lacks proper message formatting and citation linking
- Citation navigation between messages and document viewer is missing in NextJS version

**Detailed Tasks:**
- [x] Implement rich text rendering for messages with markdown support
- [x] Create citation highlighting in message content
- [x] Add interactive citation linking to document highlights
- [x] Implement code block formatting with syntax highlighting
- [x] Create expandable/collapsible sections for long responses
- [x] Add automated financial term recognition with explanations
- [x] Implement copy functionality for message content
- [x] Create message reference linking between related responses

**Technical Implementation:**
```typescript
// src/components/MessageFormatter.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { Citation } from '../types/citations';

interface MessageFormatterProps {
  content: string;
  citations?: Citation[];
  onCitationClick?: (highlightId: string) => void;
}

export const MessageFormatter: React.FC<MessageFormatterProps> = ({
  content,
  citations = [],
  onCitationClick
}) => {
  // Create a map of citation IDs to the actual citation objects
  const citationMap = React.useMemo(() => {
    return citations.reduce((map, citation) => {
      map[citation.id] = citation;
      return map;
    }, {} as Record<string, Citation>);
  }, [citations]);
  
  // Process the content to highlight citations
  const processedContent = React.useMemo(() => {
    if (!citations.length) return content;
    
    let result = content;
    
    // Replace citation markers with clickable spans
    // Format: {{citation:1234}} where 1234 is the citation ID
    const citationRegex = /\{\{citation:([a-zA-Z0-9-]+)\}\}/g;
    result = result.replace(citationRegex, (match, citationId) => {
      const citation = citationMap[citationId];
      if (!citation) return match;
      
      // Replace with a special marker that React can parse
      return `[CITATION_${citationId}]`;
    });
    
    return result;
  }, [content, citations, citationMap]);
  
  // Render the markdown content
  return (
    <div className="message-content">
      <ReactMarkdown
        components={{
          // Handle code blocks with syntax highlighting
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                language={match[1]}
                style={syntaxTheme}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          // Process paragraphs to handle citation markers
          p({ node, children, ...props }) {
            // Convert children to array if it's not already
            const childrenArray = React.Children.toArray(children);
            
            // Process each child
            const processedChildren = childrenArray.flatMap(child => {
              if (typeof child !== 'string') return child;
              
              // Split by citation markers
              const parts = child.split(/\[CITATION_([a-zA-Z0-9-]+)\]/g);
              
              // If no split occurred, return the original child
              if (parts.length === 1) return child;
              
              // Otherwise, process the parts
              const result: React.ReactNode[] = [];
              
              for (let i = 0; i < parts.length; i++) {
                // Add the text part
                if (parts[i]) result.push(parts[i]);
                
                // If there's a citation ID after this part, add the citation
                if (i < parts.length - 1 && i % 2 === 0) {
                  const citationId = parts[i + 1];
                  const citation = citationMap[citationId];
                  
                  if (citation) {
                    result.push(
                      <span
                        key={`citation-${citationId}`}
                        className="citation-reference"
                        onClick={() => onCitationClick?.(citation.highlightId)}
                        title={`Citation from document: ${citation.text.substring(0, 100)}...`}
                      >
                        [📝]
                      </span>
                    );
                  }
                }
              }
              
              return result;
            });
            
            return <p {...props}>{processedChildren}</p>;
          }
        }}
      >
        {processedContent}
      </ReactMarkdown>
      
      {citations.length > 0 && (
        <div className="citations-container">
          <h4>Citations</h4>
          <div className="citations-list">
            {citations.map(citation => (
              <div 
                key={citation.id}
                className="citation-item"
                onClick={() => onCitationClick?.(citation.highlightId)}
              >
                <div className="citation-marker">[📝]</div>
                <div className="citation-text">
                  {citation.text.length > 150
                    ? `${citation.text.substring(0, 150)}...`
                    : citation.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

**Integration Points:**
- Must connect with ChatInterface for message display
- Should integrate with citation handling from API responses
- Needs to coordinate with PDFViewer for highlight navigation
- Must handle markdown, code blocks, and other formatting
- Should support citation references and document highlight linking

```

```
