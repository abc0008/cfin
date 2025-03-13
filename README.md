# Financial Document Analysis System (FDAS)

FDAS is an AI-powered application that analyzes financial PDFs using an interactive chatbot and canvas visualization. The system leverages Claude API for PDF processing and citation extraction, with LangChain/LangGraph for AI orchestration.

## Project Structure

The project consists of two main parts:

1. **Frontend**: React/TypeScript application with interactive chat, document viewer, and visualization components
2. **Backend**: FastAPI server with PDF processing, AI orchestration, and database integration

## Application Flow
Okay, I understand. You're looking for a Mermaid diagram that illustrates the *application flow* during user interaction, showing how the frontend and backend work together. Here's a Mermaid diagram focusing on the user's journey:

```mermaid
graph LR
    A[User (Frontend - Browser)] --> B{Uploads Document}
    B -- API Request (POST /api/documents/upload) --> C[FastAPI Backend API]
    C --> D{Document Service}
    D --> E{Storage Service}
    E --> F[File Storage (e.g., Local/S3)]
    D --> G{Document Repository}
    G --> H[Database (fdas.db)]
    C -- Document Upload Response --> A

    A --> I{Sends Message in Chat}
    I -- API Request (POST /api/conversation/{session_id}/message) --> C
    C --> J{Conversation Service}
    J --> K{Claude Service}
    K --> L[Claude API]
    L -- AI Response & Citations --> K
    K --> M{Conversation Repository}
    M --> H
    J -- AI Response --> C
    C -- AI Response Message --> A

    A --> N{Requests Analysis}
    N -- API Request (POST /api/analysis/run) --> C
    C --> O{Analysis Service}
    O --> P{Financial Agent (LangGraph)}
    P --> L
    O --> Q{Analysis Repository}
    Q --> H
    O -- Analysis Results --> C
    C -- Analysis Results --> A

    style A fill:#afa,stroke:#333,stroke-width:2px
    style C fill:#aaf,stroke:#333,stroke-width:2px
    style F fill:#eee,stroke:#333,stroke-width:1px,style:dashed
    style L fill:#eee,stroke:#333,stroke-width:1px,style:dashed
    style H fill:#eee,stroke:#333,stroke-width:1px,style:dashed

    subgraph Frontend
        A
    end

    subgraph Backend
        C
        D
        E
        G
        J
        K
        O
        P
        Q
    end

    subgraph Storage
        F
        H
    end

    subgraph External AI Service
        L
    end
```

**Explanation of the Flow:**

1.  **User Interaction (Frontend - Browser) [A]:**  This is where the user interacts with the Next.js frontend in their web browser.
2.  **Uploads Document [B]:** When a user uploads a document via the frontend:
    *   **API Request (POST /api/documents/upload) [B --> C]:** The frontend sends a `POST` request to the backend's `/api/documents/upload` endpoint.
    *   **FastAPI Backend API [C]:** The FastAPI backend receives the request.
    *   **Document Service [D]:** The `DocumentService` handles the document upload logic.
    *   **Storage Service [E]:** The `StorageService` (e.g., `LocalStorageService` or `S3StorageService`) saves the uploaded file to storage.
    *   **File Storage (e.g., Local/S3) [F]:** The document is physically stored.
    *   **Document Repository [G]:** The `DocumentRepository` creates a record of the document in the database.
    *   **Database (fdas.db) [H]:** Document metadata is stored in the database.
    *   **Document Upload Response [C --> A]:** The backend sends a response back to the frontend indicating the success or failure of the upload.

3.  **Sends Message in Chat [I]:** When a user sends a message in the chat interface:
    *   **API Request (POST /api/conversation/{session_id}/message) [I --> C]:** The frontend sends a `POST` request to the backend's `/api/conversation/{session_id}/message` endpoint.
    *   **FastAPI Backend API [C]:** The FastAPI backend receives the message request.
    *   **Conversation Service [J]:** The `ConversationService` processes the user message.
    *   **Claude Service [K]:** The `ConversationService` uses the `ClaudeService` to interact with the Claude API for generating AI responses.
    *   **Claude API [L]:** Claude API processes the message and generates a response, potentially including citations.
    *   **AI Response & Citations [L --> K]:** Claude API returns the AI response and any citations.
    *   **Conversation Repository [M]:** The `ConversationRepository` stores the user message and the AI response in the database.
    *   **Database (fdas.db) [H]:** Conversation history is updated in the database.
    *   **AI Response Message [J --> C]:** The `ConversationService` sends the AI response back to the FastAPI backend.
    *   **AI Response Message [C --> A]:** The FastAPI backend sends the AI response message back to the frontend.

4.  **Requests Analysis [N]:** When a user requests financial analysis (e.g., by clicking an "Analyze" button or sending a specific chat command):
    *   **API Request (POST /api/analysis/run) [N --> C]:** The frontend sends a `POST` request to the backend's `/api/analysis/run` endpoint.
    *   **FastAPI Backend API [C]:** The FastAPI backend receives the analysis request.
    *   **Analysis Service [O]:** The `AnalysisService` orchestrates the financial analysis.
    *   **Financial Agent (LangGraph) [P]:** The `AnalysisService` utilizes the `FinancialAgent` (built with LangGraph) to perform the analysis.
    *   **Claude API [L]:** The `FinancialAgent` may interact with the Claude API during analysis (e.g., for enhanced data extraction or insights).
    *   **Analysis Repository [Q]:** The `AnalysisRepository` stores the analysis results in the database.
    *   **Database (fdas.db) [H]:** Analysis results are persisted in the database.
    *   **Analysis Results [O --> C]:** The `AnalysisService` sends the analysis results back to the FastAPI backend.
    *   **Analysis Results [C --> A]:** The FastAPI backend sends the analysis results back to the frontend.

**Key Components Highlighted:**

*   **Frontend:** User interface in the browser.
*   **FastAPI Backend API:** Entry point for frontend requests, routing and coordination.
*   **Services:** Business logic components (`DocumentService`, `ConversationService`, `AnalysisService`, `ClaudeService`, `StorageService`).
*   **Repositories:** Data access layer (`DocumentRepository`, `ConversationRepository`, `AnalysisRepository`).
*   **Database:** Data persistence.
*   **Claude API:** External AI service for PDF processing and AI responses.
*   **File Storage:**  Storage for uploaded PDF documents.
*   **LangGraph Financial Agent:**  AI agent orchestrating complex analysis workflows.

This diagram should provide a clearer picture of the application flow and the interaction between the frontend and backend components in FDAS. Let me know if you would like any specific parts of this flow to be elaborated further.

## Quick Start

### Setting up the Backend

1. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory with your API keys:

```
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229

# Database Configuration
DATABASE_URL=sqlite:///./fdas.db  # For development; use PostgreSQL in production

# Storage Configuration
UPLOAD_DIR=./uploads
STORAGE_TYPE=local  # Options: local, s3

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

3. Initialize the database:

```bash
python create_db.py
```

4. Start the backend server:

```bash
python run.py
```

The backend server will start on http://localhost:8000.

### Setting up the Frontend

1. Install dependencies:

```bash
cd ..  # Return to project root
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend application will start on http://localhost:5173.

## Testing the API

To test the backend API, you can use the provided test script:

```bash
cd backend
./test_api.sh
```

This script tests various API endpoints including:
- Health check
- Conversation creation
- Sending messages
- Document uploading (commented out - uncomment if you have test PDFs)
- Running analysis (commented out - uncomment if you have test documents)

## Main Features

- PDF document upload and processing
- Financial data extraction with Claude API
- Conversation with citation linking
- Financial analysis with visualizations
- Interactive canvas for exploring financial data

## System Architecture

### Frontend Components

- **Layout**: Main application structure
- **ChatInterface**: Conversation with AI assistant
- **Canvas**: Interactive visualization of financial data
- **DocumentViewer**: PDF viewer with citation highlighting

### Backend Components

- **FastAPI Server**: Main web server and API endpoints
- **Document Service**: PDF processing and extraction
- **Claude Service**: Integration with Claude API
- **Database**: Document and analysis storage
- **Analysis Service**: Financial analysis and insights

## Technology Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **AI**: Claude API, LangChain, LangGraph
- **Infrastructure**: SQLite (development), S3 (optional)

## Security and Privacy

- Documents are stored securely with access controls
- API communication uses HTTPS
- Authentication is managed through token-based auth
- Environment variables protect API keys

## Development Status

The project is currently in active development with the following phases:

1. ✅ Foundation: Setup, basic PDF processing
2. ✅ Core Features: Citation extraction, financial data extraction
3. 🔄 Advanced Features: Interactive canvas, citation linking
4. 🔄 Refinement: Optimization, security, monitoring

## Contributing

Contributions are welcome! Please open an issue or pull request for any improvements or bug fixes.