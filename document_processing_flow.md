# Document Processing Flow for CFIN

Based on analysis of the codebase, here's the complete document processing flow from upload to LLM integration in the CFIN system:

```mermaid
flowchart TD
    subgraph "Frontend (Next.js)"
        A[User Interface] --> B[documents.ts]
        B -->|"uploadDocument()"| C[API Client]
    end

    subgraph "Backend API Routes"
        C -->|POST /api/documents/upload| D[document.py]
        D -->|create_document()| E[document_repository.py]
        D -->|start background task| F[document_service.py]
    end

    subgraph "Document Processing"
        F -->|_process_document()| G[claude_service.py]
        G -->|process_pdf()| H[PDF Processing]
        G -->|extract_citations()| I[Citation Extraction]
        F -->|update_document_content()| E
        F -->|add_citation()| E
    end

    subgraph "Document Storage"
        E -->|store_file()| J[Storage Service]
        E -->|save to database| K[Database]
    end

    subgraph "Conversation Integration"
        L[conversation.py] -->|add_document_to_conversation()| M[langgraph_service.py]
        M -->|get_document()| E
        M -->|get_document_content()| E
        M -->|prepare document context| N[Document Context]
        N -->|add to conversation state| O[Conversation State]
    end

    subgraph "LLM Integration"
        P[chat UI] -->|send message with doc reference| L
        L -->|send_message()| M
        M -->|simple_document_qa()| Q[Claude API]
        Q -->|generate response with citations| R[Response with Citations]
    end
```

## Detailed File Purposes and Flow

### Frontend Components
- **nextjs-fdas/src/lib/api/documents.ts**
  - Purpose: Client-side API wrapper for document operations
  - Key functions: `uploadDocument()`, `uploadAndVerifyDocument()`, `getDocumentCitations()`

### Backend API Routes
- **backend/app/routes/document.py**
  - Purpose: FastAPI endpoints for document operations
  - Key endpoints: `/upload`, `/api/documents/{document_id}`, `/api/documents/{document_id}/citations`

### Document Processing
- **backend/pdf_processing/document_service.py**
  - Purpose: Orchestrates document processing workflow
  - Key functions: `upload_document()`, `_process_document()`, `extract_structured_financial_data()`

- **backend/pdf_processing/claude_service.py**
  - Purpose: Interfaces with Claude API for PDF analysis and citation extraction
  - Key functions: `process_pdf()`, `extract_citations()`, `analyze_financial_document()`

### Document Storage
- **backend/repositories/document_repository.py**
  - Purpose: Handles database operations for documents and citations
  - Key functions: `create_document()`, `update_document_content()`, `add_citation()`, `get_document_content()`

### Conversation & LLM Integration
- **backend/api/conversation.py**
  - Purpose: API endpoints for conversation management
  - Key endpoints: `/conversation/{conversation_id}/document/{document_id}`, `/conversation/{conversation_id}/message`

- **backend/pdf_processing/langgraph_service.py**
  - Purpose: Manages conversation state and LLM interactions
  - Key functions: `add_document_to_conversation()`, `simple_document_qa()`, `_prepare_document_context()`

## Document Flow Process

1. **Document Upload**:
   - User selects a PDF file in the frontend
   - `documents.ts` calls `uploadDocument()` which POSTs to `/api/documents/upload`
   - `document.py` receives the file and calls `document_repository.create_document()`
   - Document metadata is saved to database and file is stored on disk
   - A background task `_process_document()` is started for document processing

2. **Document Processing**:
   - `document_service.py` manages the processing workflow
   - `claude_service.py` is called to analyze the PDF
   - Claude API extracts text, financial data, and citations
   - Document content and citations are saved to database

3. **Document Retrieval & Conversation Integration**:
   - User adds document to conversation in UI
   - `/conversation/{conversation_id}/document/{document_id}` endpoint is called
   - `langgraph_service.add_document_to_conversation()` is invoked
   - Document content is retrieved using `document_repository.get_document_content()`
   - Document is added to conversation state

4. **LLM Integration & Citations**:
   - User sends a message referencing the document
   - `langgraph_service.simple_document_qa()` is called
   - Document context is prepared with `_prepare_document_context()`
   - Claude 3.5 Sonnet API is called with document context
   - Response is generated with citations to specific sections of the document
   - Citations are matched to the document and returned to frontend

5. **Citation Display**:
   - Frontend displays response with citations
   - Citations are linked to specific sections in the PDF
   - PDF Viewer component highlights referenced sections

The critical component that was fixed was in the `langgraph_service.add_document_to_conversation()` method, which was using a mock document instead of retrieving the actual one from the repository. This broke the link between uploaded documents and the conversation context presented to Claude.
