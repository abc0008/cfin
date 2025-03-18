Below is the revised product requirements document with the provided mermaid diagrams integrated. Adjustments have been made only where necessary—primarily to reflect the enhanced PDF processing that now includes citation extraction—while preserving all original content.

Financial Document Analysis System (FDAS) – Project Requirements Document

The FDAS is an AI-powered application that analyzes financial PDFs using an interactive chatbot and canvas display. Users can upload financial documents, perform structured analysis, and interact with data through a visually engaging and highly interactive interface. The system leverages state-of-the-art AI services such as Claude API’s advanced PDF support and citation extraction, as well as pre-built conversational agents from LangGraph, with orchestration provided by LangChain.

Executive Summary

FDAS is designed to revolutionize financial document analysis by combining robust PDF processing with a conversational AI interface and dynamic visualization. The system is built with a FastAPI backend and NextJS frontend and integrates cutting-edge services including:
	•	Claude API PDF support and citation features: for extracting and linking financial data, tables, and citations.
	•	Pre-built LangGraph agents: to streamline common financial analysis tasks.
	•	Frontend components inspired by Anthropic Quickstarts and react‐pdf‐highlighter: ensuring an intuitive user experience that includes interactive PDF viewing, highlighting, and citation linking.

System Architecture

FDAS is divided into several subsystems, each responsible for key functions such as document management, conversational AI, financial analysis, and visualization. Integration of external examples and APIs enriches the user experience with enhanced PDF annotation and precise citation management.

Below is the mermaid diagram representing the overall FDAS system architecture. Note that the arrow from the PDF Processing Service to Claude now reflects both PDF extraction and citation extraction.

flowchart TB
    subgraph Client
        UI[User Interface]
        Chat[Chat Interface]
        Canvas[Interactive Canvas]
    end
    
    subgraph Backend
        API[FastAPI Backend]
        subgraph AI_Engine
            LangChain[LangChain Components]
            LangGraph[LangGraph State Management]
            AgentMemory[Agent Memory Store]
        end
        PdfProcessor[PDF Processing Service]
        DataValidator[Pydantic Validators]
    end
    
    subgraph External_Services
        Claude[Claude API]
    end
    
    subgraph Database
        DocumentStore[Document Storage]
        AnalysisResults[Analysis Results]
        ConversationHistory[Conversation History]
    end
    
    UI --> |User Interactions| API
    Chat --> |Messages| API
    Canvas --> |Visualization Requests| API
    
    API --> |Document Processing| PdfProcessor
    API --> |AI Orchestration| LangChain
    API --> |Data Validation| DataValidator
    
    PdfProcessor --> |PDF Extraction & Citation Extraction| Claude
    
    LangChain --> |State Management| LangGraph
    LangChain --> |Memory Retrieval| AgentMemory
    LangGraph --> |State Updates| AgentMemory
    
    API --> |Store Documents| DocumentStore
    API --> |Store Results| AnalysisResults
    API --> |Store Conversations| ConversationHistory
    
    DocumentStore --> |Retrieve Documents| API
    AnalysisResults --> |Retrieve Results| API
    ConversationHistory --> |Context Retrieval| AgentMemory

Key Requirements

Functional Requirements
	1.	Document Processing
	•	PDF Upload and Processing
	•	Support secure PDF upload.
	•	Leverage Claude API’s PDF support to extract text, tables, and embedded citations.
	•	Process multiple documents per session.
	•	Store processed documents for future reference.
	•	Citation and Annotation Extraction
	•	Extract citation metadata from PDFs using Claude’s citation features.
	•	Provide links and contextual highlights that connect document content to analysis results.
	2.	Conversational Interface
	•	Interactive Chatbot
	•	Stateful chatbot interface with multi-turn conversation and context retention.
	•	Incorporate citation linking: enable users to reference highlighted PDF sections directly in the conversation.
	•	Provide guided financial analysis prompts inspired by Anthropic Quickstarts.
	•	Conversation History
	•	Maintain full conversation history with citation references for each analysis session.
	3.	Financial Analysis Capabilities
	•	Data Analysis
	•	Perform ratio and trend analysis on financial statements.
	•	Identify key performance indicators and industry benchmarks.
	•	Compare results to detect anomalies and significant data shifts.
	•	Pre-Built Agent Integration
	•	Integrate LangGraph pre-built agents for common financial analysis tasks to improve reliability and reduce development time.
	4.	Interactive Canvas and Visualization
	•	Dynamic Visualizations
	•	Display financial analysis results on an interactive canvas with Recharts.
	•	Support zooming, filtering, and exploration of data.
	•	Enable export of visualizations.
	•	Linked PDF Annotations
	•	Incorporate PDF viewer enhancements inspired by react‐pdf‐highlighter.
	•	Allow users to highlight document sections and link them to conversation and analysis outcomes.
	5.	Data Validation and Structure
	•	Structured Data Models
	•	Use Pydantic models for validating all input and output data.
	•	Provide structured output for visualizations and citations.
	•	Report validation errors gracefully.

Technical Requirements
	1.	Frontend
	•	Framework and Design
	•	Build with NextJS and mimic the design patterns of the Anthropic Quickstarts financial analyst example.
	•	Use Shadcn UI for a consistent component library.
	•	Visualization and Interactivity
	•	Integrate Recharts for responsive, real-time data visualization.
	•	Implement a PDF viewer with advanced highlighting and citation linking (react‐pdf‐highlighter).
	•	Ensure responsive design across desktop, tablet, and mobile devices.
	2.	Backend
	•	API and Service Architecture
	•	Develop with FastAPI to support high-performance API calls.
	•	Orchestrate AI workflows with LangChain and stateful agent interactions using LangGraph (including pre-built agents).
	•	PDF Processing and Citation Extraction
	•	Create a dedicated PDF processing service that leverages Claude API’s PDF support.
	•	Integrate citation extraction endpoints to capture and link document references.
	3.	AI Components
	•	Conversational Agents and Memory
	•	Implement agent memory for context retention.
	•	Design conversation flows that incorporate citation linking and highlighted document excerpts.
	•	Error Handling and Fallbacks
	•	Develop specialized tools for financial analysis with built-in fallback mechanisms.
	•	Utilize LangGraph’s stateful agents for common tasks to ensure robust operation.
	4.	Data Flow
	•	Secure and Efficient Processing
	•	Support secure document upload, caching, and efficient retrieval.
	•	Structure data outputs to include citation metadata and visualization-ready formats.
	•	Support export of both visual analysis and document annotations.

Detailed System Components

1. Document Management Subsystem

- PDF Upload Service
  - Validates PDF format and size.
  - Stores documents in secure storage.
  - Returns document identifiers with citation metadata if available.

- PDF Processing Service
  - Uses Claude API to extract text, tables, and citation information.
  - Identifies financial statement types and annotates key sections.
  - Normalizes extracted data, including highlighted citations, into a structured format.

- Document Storage Service
  - Manages document metadata and citation links.
  - Handles versioning and secure retrieval.
  - Implements robust access control.

2. Conversational AI Subsystem

- Conversation Manager
  - Routes user messages and maintains conversation context.
  - Incorporates citation links and document highlights into responses.
  - Stores conversation history with reference to highlighted content.

- LangGraph Integration
  - Implements pre-built financial analysis nodes from LangGraph.
  - Defines state transitions for conversation flows that include citation review.
  - Manages session persistence and branching based on user-selected document highlights.

- Agent Memory
  - Captures and retains key conversation turns and document citations.
  - Implements context retrieval with support for citation linking.
  - Manages memory pruning and priority-based retention.

3. Financial Analysis Subsystem

- Analysis Orchestrator
  - Coordinates analysis workflows and dispatches requests.
  - Aggregates results, including highlighted citation data.
  - Supports parallel processing of multiple analyses.

- Financial Ratio Calculator and Trend Engine
  - Computes standard ratios and trends.
  - Validates data and manages missing scenarios.
  - Generates narrative insights including links to document highlights.

- Benchmark Comparator
  - Compares financial metrics against industry benchmarks.
  - Integrates citation metadata to reference source documents.

4. Visualization Subsystem

- Canvas Controller
  - Manages visual updates and interactive controls.
  - Supports dynamic visualization linked to PDF highlights and citations.
  - Manages viewport adjustments and navigation.

- Chart Generator
  - Formats data for Recharts.
  - Creates responsive charts that integrate with highlighted document sections.
  - Updates dynamically as new analysis data (including citations) becomes available.

- Interactive Elements Manager
  - Implements tooltips, hover states, and clickable citation links.
  - Supports selection, filtering, and drill-down operations.
  - Coordinates linked visualizations with highlighted PDF data.

Data Models

Document Schema

class DocumentMetadata(BaseModel):
    id: UUID
    filename: str
    upload_timestamp: datetime
    file_size: int
    mime_type: str
    user_id: UUID
    citation_links: Optional[List[str]] = []  # New: Store citation references

class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    content_type: Literal["balance_sheet", "income_statement", "cash_flow", "notes", "other"]
    extraction_timestamp: datetime
    periods: List[str]
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_status: Literal["pending", "processing", "completed", "failed"]
    error_message: Optional[str] = None

Analysis Results Schema

class FinancialRatio(BaseModel):
    name: str
    value: float
    description: str
    benchmark: Optional[float] = None
    trend: Optional[float] = None
    
class FinancialMetric(BaseModel):
    category: str
    name: str
    period: str
    value: float
    unit: str
    is_estimated: bool = False
    
class AnalysisResult(BaseModel):
    id: UUID
    document_ids: List[UUID]
    analysis_type: str
    timestamp: datetime
    metrics: List[FinancialMetric]
    ratios: List[FinancialRatio]
    insights: List[str]
    visualization_data: Dict[str, Any]
    citation_references: Optional[Dict[str, str]] = {}  # New: Map document sections to citation sources

Conversation Schema

class Message(BaseModel):
    id: UUID
    session_id: UUID
    timestamp: datetime
    role: Literal["user", "assistant", "system"]
    content: str
    referenced_documents: List[UUID] = []
    referenced_analyses: List[UUID] = []
    citation_links: Optional[List[str]] = []  # New: Link to highlighted PDF sections
    
class ConversationState(BaseModel):
    session_id: UUID
    active_documents: List[UUID]
    active_analyses: List[UUID]
    current_focus: Optional[str] = None
    user_preferences: Dict[str, Any] = {}
    last_updated: datetime

API Specifications

Document Management APIs

Upload Document
	•	Endpoint: POST /api/documents/upload
	•	Description: Upload a financial document for processing, including citation metadata extraction.
	•	Request: Multipart form data with file.
	•	Response: Document metadata (with citation links, if extracted).
	•	Status Codes: 201 (success), 400 (invalid format), 413 (file too large).

Get Document
	•	Endpoint: GET /api/documents/{document_id}
	•	Description: Retrieve document metadata, processed content, and citation highlights.
	•	Parameters: document_id (UUID)
	•	Response: Complete ProcessedDocument object.
	•	Status Codes: 200 (success), 404 (not found).

List Documents
	•	Endpoint: GET /api/documents
	•	Description: List all documents for the current user.
	•	Parameters: page (int, optional), page_size (int, optional), filter (string, optional)
	•	Response: Paginated list of DocumentMetadata objects.
	•	Status Codes: 200 (success)

Conversation APIs

Send Message
	•	Endpoint: POST /api/conversation/message
	•	Description: Send a message to the AI assistant with citation reference support.
	•	Request Body:

{
  "session_id": "uuid",
  "content": "string",
  "referenced_documents": ["uuid1", "uuid2"],
  "citation_links": ["link1", "link2"]
}


	•	Response: AI reply including analysis results and linked citations.
	•	Status Codes: 200 (success), 400 (invalid format)

Get Conversation History
	•	Endpoint: GET /api/conversation/{session_id}/history
	•	Description: Retrieve conversation history including citation links.
	•	Parameters: session_id (UUID), limit (int, optional)
	•	Response: List of Message objects.
	•	Status Codes: 200 (success), 404 (not found)

Analysis APIs

Run Analysis
	•	Endpoint: POST /api/analysis/run
	•	Description: Initiate a financial analysis on selected documents, including citation extraction.
	•	Request Body:

{
  "analysis_type": "string",
  "document_ids": ["uuid1", "uuid2"],
  "parameters": {
    "key1": "value1",
    "key2": "value2"
  }
}


	•	Response: Analysis result or job ID (async processing).
	•	Status Codes: 202 (initiated), 400 (invalid parameters)

Get Analysis Results
	•	Endpoint: GET /api/analysis/{analysis_id}
	•	Description: Retrieve analysis results along with linked citation references.
	•	Parameters: analysis_id (UUID)
	•	Response: Complete AnalysisResult object.
	•	Status Codes: 200 (success), 202 (processing), 404 (not found)

Frontend Components

Page Structure
	1.	Dashboard Page
	•	Document library and recent analyses summary.
	•	Quick action buttons with citation and highlight indicators.
	•	Activity feed with links to highlighted document sections.
	2.	Analysis Workspace
	•	Chat interface panel with citation link support.
	•	Interactive canvas area displaying dynamic financial visualizations.
	•	Document selector sidebar showing annotated documents.
	•	Analysis controls toolbar.
	3.	Document Viewer
	•	PDF renderer with integrated highlighting and annotation (inspired by react‐pdf‐highlighter).
	•	Extraction highlights linked to citation data.
	•	Annotation and verification tools with citation linking capabilities.

Component Hierarchy

- Layout
  - Header
    - Navigation (with citation notifications)
    - User Profile
    - Notifications
  - Sidebar
    - Document Explorer (with document highlight previews)
    - Analysis Library
    - Settings
  - Main Content Area
    - Chat Interface
      - Message List (with citation links)
      - Input Area
      - Suggestion Chips
    - Canvas
      - Visualization Container
      - Interactive Controls (zoom, filter, citation highlights)
      - Legend (including citation markers)
      - Export Tools
    - Document Viewer
      - PDF Renderer (with dynamic highlighting and linking)
      - Page Navigator
      - Extraction Overlay (highlighted sections with citations)

UI/UX Requirements
	1.	Responsive Design
	•	Support desktop, tablet, and mobile views.
	•	Adapt layout to different screen sizes.
	•	Maintain functionality across devices.
	2.	Accessibility
	•	Adhere to WCAG 2.1 AA standards.
	•	Provide keyboard navigation and screen reader support.
	•	Ensure high contrast and clear visual cues for highlights and citations.
	3.	Performance
	•	Optimize initial load time (<2 seconds).
	•	Implement progressive loading for large documents and real-time chat updates.
	•	Use caching for frequently accessed documents and citation data.
	•	Optimize re-renders for interactive elements and highlighted annotations.

AI Agent Implementation

Agent Architecture

- Agent Coordinator
  - Manages overall behavior, routing intents, and citation linking.
  - Routes user queries to specialized financial analysis and citation extraction modules.
  - Implements fallback responses and handles errors.

- Financial Analysis Specialist
  - Processes complex financial queries.
  - Interprets financial statements and highlights citation-relevant sections.
  - Provides detailed insights, including calculations with citation support.

- Document Navigator
  - Assists users in locating relevant document sections.
  - Extracts and links information across documents with citation markers.
  - Highlights and compares key document sections.

LangGraph Implementation

# Pseudocode for LangGraph state definition including citation handling
financial_analysis_graph = StateGraph(name="FinancialAnalysisGraph")

# Define nodes with citation-aware functionality
financial_analysis_graph.add_node("document_selection", document_selection_node)
financial_analysis_graph.add_node("analyze_financials", analyze_financials_node)
financial_analysis_graph.add_node("generate_visualizations", generate_visualizations_node)
financial_analysis_graph.add_node("explain_results", explain_results_node)
financial_analysis_graph.add_node("route_intent", route_intent_node)

# Define edges including paths for citation review
financial_analysis_graph.add_edge("route_intent", "document_selection")
financial_analysis_graph.add_edge("route_intent", "analyze_financials")
financial_analysis_graph.add_edge("route_intent", "explain_results")
financial_analysis_graph.add_edge("document_selection", "analyze_financials")
financial_analysis_graph.add_edge("analyze_financials", "generate_visualizations")
financial_analysis_graph.add_edge("generate_visualizations", "explain_results")
financial_analysis_graph.add_edge("explain_results", "route_intent")

# Compile graph with citation context in mind
financial_analysis_graph.compile()

Agent Memory Implementation

# Pseudocode for memory implementation with citation linking
class AgentMemory:
    def __init__(self):
        self.short_term_memory = []  # Recent conversation turns with citation references
        self.working_memory = {}     # Active context including highlighted citations
        self.long_term_memory = []   # Vectorized storage for retrieval
    
    def add_interaction(self, message, response, context):
        # Update short-term memory
        self.short_term_memory.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now(),
            "citation_links": context.get("citation_links", [])
        })
        
        if len(self.short_term_memory) > MAX_SHORT_TERM_MEMORY:
            self.short_term_memory.pop(0)
        
        # Update working memory with active entities and citation markers
        for entity in context.get("entities", []):
            self.working_memory[entity["id"]] = entity
        
        # Store in long-term memory for future retrieval
        vector = embed_text(f"{message} {response}")
        self.long_term_memory.append({
            "vector": vector,
            "text": f"{message} {response}",
            "timestamp": datetime.now(),
            "citation_links": context.get("citation_links", [])
        })
    
    def get_relevant_context(self, query, k=5):
        query_vector = embed_text(query)
        scored_memories = [(cosine_similarity(query_vector, m["vector"]), m) 
                           for m in self.long_term_memory]
        scored_memories.sort(reverse=True)
        return [m["text"] for _, m in scored_memories[:k]]

Integration Points

Claude API Integration

# Pseudocode for Claude API integration with PDF and citation support
class ClaudeService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.client = httpx.AsyncClient()
    
    async def process_pdf(self, pdf_data):
        """
        Process a PDF using Claude's PDF support and citation extraction.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-latest",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all financial data and citation references from this document. Identify document type and output as JSON with citation links."
                        },
                        {
                            "type": "file",
                            "file_data": {
                                "type": "application/pdf",
                                "data": base64.b64encode(pdf_data).decode()
                            }
                        }
                    ]
                }
            ]
        }
        
        response = await self.client.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=data
        )
        
        result = response.json()
        extracted_content = self._parse_claude_response(result)
        return extracted_content
    
    def _parse_claude_response(self, response):
        """
        Parse the Claude API response and extract structured financial data and citation information.
        """
        # Implementation details for parsing response and extracting citations
        pass

LangChain Integration

# Pseudocode for LangChain integration with citation-aware conversation
from langchain.chat_models import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate

def setup_langchain_agent():
    # Initialize Claude model with citation support
    model = ChatAnthropic(
        model="claude-3-opus-20240229",
        temperature=0.2,
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"]
    )
    
    # Set up memory with citation retention
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Define a financial analysis prompt with instructions for citing document highlights
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a financial analysis assistant specializing in analyzing financial statements. 
                    Provide detailed calculations and link your analysis to highlighted document citations when available."""),
        ("human", "{input}"),
        ("ai", "{chat_history}")
    ])
    
    # Create conversation chain
    conversation = ConversationChain(
        llm=model,
        memory=memory,
        prompt=prompt,
        verbose=True
    )
    
    return conversation

Testing Strategy

Unit Testing
	•	Test individual components (including citation extraction and PDF highlighting).
	•	Use mocks for external services (Claude API, LangGraph pre-built agents).
	•	Target >80% code coverage with pytest (Python) and Jest (JavaScript).

Integration Testing
	•	Verify API contracts, data flows, and citation link propagation.
	•	Test database operations and state transitions including highlighted PDF sections.
	•	Use FastAPI TestClient and React Testing Library.

End-to-End Testing
	•	Simulate complete user journeys including PDF upload, conversation with citation references, and visualization updates.
	•	Validate PDF processing accuracy and linked annotation behavior.
	•	Automate browser tests with Cypress or Playwright.

Performance Testing
	•	Benchmark response times for PDF processing, citation extraction, and conversation updates.
	•	Conduct load testing with concurrent users using Locust.

Deployment Architecture

Below is the mermaid diagram for FDAS deployment architecture. The arrow from PDFService to ClaudeAPI has been adjusted to indicate that it now handles both PDF extraction and citation extraction.

flowchart TB
    subgraph User
        Browser[Web Browser]
    end
    
    subgraph CDN
        StaticAssets[Static Assets]
    end
    
    subgraph LoadBalancer
        NginxLB[Nginx Load Balancer]
    end
    
    subgraph WebTier
        NextJS1[NextJS Server 1]
        NextJS2[NextJS Server 2]
    end
    
    subgraph APITier
        API1[FastAPI Server 1]
        API2[FastAPI Server 2]
    end
    
    subgraph Services
        PDFService[PDF Processing Service]
        AIOrchestrator[AI Orchestration Service]
    end
    
    subgraph Database
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
    end
    
    subgraph Storage
        S3[(Document Storage)]
    end
    
    subgraph External
        ClaudeAPI[Claude API]
    end
    
    subgraph Monitoring
        Prometheus[Prometheus]
        Grafana[Grafana Dashboard]
        Loki[Loki Log Aggregation]
    end
    
    Browser --> NginxLB
    Browser --> CDN
    
    NginxLB --> NextJS1
    NginxLB --> NextJS2
    
    NextJS1 --> API1
    NextJS2 --> API2
    
    API1 --> PDFService
    API1 --> AIOrchestrator
    API2 --> PDFService
    API2 --> AIOrchestrator
    
    PDFService --> S3
    PDFService --> |PDF & Citation Extraction| ClaudeAPI
    
    AIOrchestrator --> ClaudeAPI
    
    API1 --> PostgreSQL
    API2 --> PostgreSQL
    
    API1 --> Redis
    API2 --> Redis
    AIOrchestrator --> Redis
    
    API1 --> Prometheus
    API2 --> Prometheus
    PDFService --> Prometheus
    AIOrchestrator --> Prometheus
    
    API1 --> Loki
    API2 --> Loki
    PDFService --> Loki
    AIOrchestrator --> Loki
    
    Prometheus --> Grafana
    Loki --> Grafana

Security Considerations
	•	Implement OAuth 2.0 / OpenID Connect, RBAC, and MFA.
	•	Encrypt sensitive data, including PDF content and citation links.
	•	Maintain data audit trails for both document access and annotation actions.

Development Process & Roadmap

Implementation Phases

Phase 1: Foundation (Weeks 1-4)
	•	Set up repositories, CI/CD pipeline, basic FastAPI backend, and NextJS frontend.
	•	Implement document upload, storage, and initial PDF processing with Claude API.

Phase 2: Core Features (Weeks 5-8)
	•	Develop citation extraction, PDF highlighting integration, and basic financial data extraction.
	•	Build a conversation API with LangChain and integrate LangGraph pre-built agents.
	•	Create initial dashboard and document viewer with annotation features.

Phase 3: Advanced Features (Weeks 9-12)
	•	Implement advanced financial analysis algorithms, interactive canvas, and linked citation displays.
	•	Enhance conversation capabilities with citation linking and improved agent memory.

Phase 4: Refinement (Weeks 13-16)
	•	Optimize performance, UI/UX, and advanced security.
	•	Add export/sharing functionality, comprehensive monitoring, and complete testing.

Conclusion

The Financial Document Analysis System (FDAS) leverages advanced PDF processing and citation extraction via Claude API, enriched frontend components modeled after Anthropic Quickstarts and react‐pdf‐highlighter, and robust pre-built agents from LangGraph. This integration ensures that users receive an intuitive, interactive, and highly reliable tool for financial analysis that directly links document content with actionable insights.