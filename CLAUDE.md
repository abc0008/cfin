# FDAS (Financial Document Analysis System)

## Project Overview
FDAS is an AI-powered application that analyzes financial PDFs using an interactive chatbot and canvas visualization. The system leverages Claude API for PDF processing and citation extraction, with LangChain/LangGraph for AI orchestration.

## Architecture
- **Client**: UI, Chat Interface, Interactive Canvas
- **Backend**: FastAPI, AI Engine (LangChain, LangGraph, Agent Memory), PDF Processing
- **External Services**: Claude API
- **Database**: Document Store, Analysis Results, Conversation History

## Technologies
### Frontend
- React/NextJS with TypeScript
- Tailwind CSS and ShadcnUI components
- Recharts for data visualization
- react-pdf-highlighter for PDF viewing and annotation

### Backend
- FastAPI for API endpoints
- LangChain for AI workflow orchestration
- LangGraph for state management and pre-built agents
- Pydantic for data validation

### Infrastructure
- PostgreSQL database
- Redis for caching
- S3-compatible storage for documents
- Prometheus/Grafana for monitoring

## Build Commands
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint on all files

## Core API Endpoints
- `POST /api/documents/upload` - Upload financial document
- `GET /api/documents/{document_id}` - Retrieve document content
- `POST /api/conversation/message` - Send message to AI assistant
- `POST /api/analysis/run` - Initiate financial analysis
- `GET /api/analysis/{analysis_id}` - Retrieve analysis results

## Code Style

### TypeScript
- Use TypeScript for type safety with strict mode enabled
- Prefer interfaces over types for object definitions
- Use optional chaining and nullish coalescing when appropriate

### Components
- Use functional components with React hooks
- Maintain proper prop typing with explicit interfaces
- Follow component structure: imports, interface, component, exports
- Use component hierarchy specified in project requirements

### CSS/Styling
- Use Tailwind CSS for styling
- Follow mobile-first responsive design approach

### Naming Conventions
- PascalCase for components, interfaces, and types
- camelCase for variables, functions, and properties
- Use descriptive, intention-revealing names

### Error Handling
- Use try/catch blocks for async operations
- Provide meaningful error messages to users
- Implement fallback mechanisms for AI components

## Key Data Models
- **DocumentMetadata/ProcessedDocument** - Document information and processing status
- **FinancialRatio/FinancialMetric/AnalysisResult** - Analysis data structures
- **Message/ConversationState** - Chat interface and state management

## Testing
- **Unit Testing**: Jest (Frontend), pytest (Backend) with >80% coverage
- **Integration Testing**: FastAPI TestClient and React Testing Library
- **E2E Testing**: Cypress or Playwright for user journeys
- **Performance Testing**: Response time benchmarks with Locust

## Security
- OAuth 2.0 / OpenID Connect authentication
- Role-Based Access Control
- Data encryption for sensitive information
- Audit trails for document access

## Implementation Phases
1. **Foundation** (Weeks 1-4): Setup, basic PDF processing
2. **Core Features** (Weeks 5-8): Citation extraction, financial data extraction
3. **Advanced Features** (Weeks 9-12): Interactive canvas, citation linking
4. **Refinement** (Weeks 13-16): Optimization, security, monitoring