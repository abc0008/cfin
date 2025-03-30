# FDAS (Financial Document Analysis System) Backend

This is the backend server for the Financial Document Analysis System, providing API endpoints for document upload, processing, and analysis using Claude API's native PDF capabilities, LangChain, and LangGraph.

## Features

- Direct PDF document processing via Claude API (no preprocessing required)
- Native citation extraction and linking
- Automatic financial data recognition and extraction
- Support for complex financial document structures
- Fallback OCR processing (only if needed)
- Conversation management with document context
- Financial analysis and visualization

## Requirements

- Python 3.9+
- FastAPI
- SQLAlchemy
- Anthropic Claude API access (claude-3-sonnet-latest or higher)
- LangChain and LangGraph

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the backend directory with the following variables:

```
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-sonnet-latest

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

### 3. Run the server

```bash
python run.py
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### Documents

- `POST /api/documents/upload` - Upload a financial document
- `GET /api/documents/{document_id}` - Get document details
- `GET /api/documents` - List user documents
- `GET /api/documents/{document_id}/citations` - Get document citations
- `GET /api/documents/{document_id}/citations/{citation_id}` - Get citation details
- `DELETE /api/documents/{document_id}` - Delete a document

### Conversation

- `POST /api/conversation/message` - Send a message
- `GET /api/conversation/{conversation_id}` - Get conversation history
- `POST /api/conversation/create` - Create a new conversation
- `GET /api/conversation` - List user conversations

### Analysis

- `POST /api/analysis/run` - Run analysis on a document
- `GET /api/analysis/{analysis_id}` - Get analysis results

## Architecture

The backend is built with the following components:

1. **FastAPI Application** - Provides RESTful API endpoints and handles requests
2. **Document Service** - Manages document upload, storage, and processing
3. **Claude Service** - Interacts with Claude API for document analysis
4. **LangChain/LangGraph Service** - Orchestrates AI workflows and enhances document processing
5. **Database Models** - SQLAlchemy ORM models for persistent data storage
6. **Storage Service** - Manages file storage (local filesystem or S3)

## Development

### Database Migrations

The application uses SQLAlchemy for database management. If you need to make changes to the database schema:

1. Update the models in `models/database_models.py`
2. Run database initialization:

```bash
python -c "from utils.init_db import run_init_db; run_init_db()"
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Production Deployment

For production deployment:

1. Use a production-grade database (PostgreSQL recommended)
2. Set up proper authentication (OAuth, API keys)
3. Configure CORS for your specific frontend domain
4. Use HTTPS for secure communication
5. Consider Docker containerization for easier deployment