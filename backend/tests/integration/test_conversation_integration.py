import pytest
import os
import uuid
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import the main FastAPI app and the necessary components
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app
from database.session import Base, get_db
from models.document import DocumentContentType
from models.message import MessageRole
from api.conversation import get_langgraph_service, get_document_service
from services.authentication import get_current_user_id
from services.session_service import get_session_service

# Create test database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DB_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    TestSessionLocal = sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def override_get_db(test_db_session):
    """Override the get_db dependency."""
    async def _override_get_db():
        yield test_db_session
        
    return _override_get_db

@pytest.fixture
def test_user_id():
    """Create a test user ID."""
    return str(uuid.uuid4())

@pytest.fixture
def test_document_id():
    """Create a test document ID."""
    return str(uuid.uuid4())

@pytest.fixture
def mock_claude_api():
    """Mock the Claude API."""
    with patch('pdf_processing.claude_service.ClaudeService._call_claude_api') as mock:
        mock.return_value = {
            "id": "msg_01XxYDJEG8jAJBcCUy538mUL",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is a test response from Claude with a citation.",
                    "citations": [
                        {
                            "type": "char_location",
                            "id": "citation-1",
                            "start_char_offset": 10,
                            "end_char_offset": 20,
                            "content": {"quote": "test data"},
                            "document": {"title": "Test Document", "url": ""}
                        }
                    ]
                }
            ],
            "model": "claude-3-5-sonnet-latest",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 150,
                "output_tokens": 50
            }
        }
        yield mock

@pytest.fixture
def client(override_get_db, test_user_id, mock_claude_api):
    """Create a test client with dependencies overridden."""
    # Override get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Override authentication dependency
    app.dependency_overrides[get_current_user_id] = lambda: test_user_id
    
    # Create a test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Clean up
    app.dependency_overrides = {}

@pytest.fixture
async def document_in_db(client, test_document_id, test_user_id):
    """Create a test document in the database."""
    # Mock the document service to return our test document
    mock_doc = {
        "id": test_document_id,
        "metadata": {
            "id": test_document_id,
            "filename": "test_document.pdf",
            "upload_timestamp": "2023-01-01T00:00:00",
            "file_size": 1000,
            "user_id": test_user_id
        },
        "content_type": DocumentContentType.BALANCE_SHEET,
        "extracted_data": {"raw_text": "This is test financial data"},
        "citations": [],
        "processing_status": "completed"
    }
    
    with patch('services.document_service.DocumentService.get_document', return_value=mock_doc):
        yield test_document_id

class TestConversationIntegration:
    """Integration tests for the conversation endpoints."""
    
    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self, client, document_in_db):
        """Test the complete conversation flow."""
        # 1. Create a new conversation
        create_response = client.post(
            "/api/conversations/conversation",
            json={
                "title": "Test Integration Conversation",
                "document_ids": []
            }
        )
        assert create_response.status_code == 200
        create_data = create_response.json()
        conversation_id = create_data["conversation_id"]
        assert create_data["title"] == "Test Integration Conversation"
        assert create_data["status"] == "created"
        
        # 2. Add a document to the conversation
        add_document_response = client.post(
            f"/api/conversations/conversation/{conversation_id}/documents",
            json=[document_in_db]
        )
        assert add_document_response.status_code == 200
        add_document_data = add_document_response.json()
        assert add_document_data["conversation_id"] == conversation_id
        assert add_document_data["status"] == "documents_added"
        assert add_document_data["documents_added"] == 1
        
        # 3. Send a message
        message_response = client.post(
            f"/api/conversations/conversation/{conversation_id}/message",
            json={
                "session_id": conversation_id,
                "content": "What financial metrics are in this document?",
                "referenced_documents": [document_in_db]
            }
        )
        assert message_response.status_code == 200
        message_data = message_response.json()
        assert message_data["session_id"] == conversation_id
        assert message_data["role"] == MessageRole.ASSISTANT
        assert "This is a test response from Claude" in message_data["content"]
        
        # 4. Get conversation history
        history_response = client.get(
            f"/api/conversations/conversation/{conversation_id}/history"
        )
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["session_id"] == conversation_id
        
        # Check that history contains our message and response
        messages = history_data["messages"]
        assert len(messages) >= 2  # User message + AI response
        
        # Find user and assistant messages
        user_messages = [m for m in messages if m["role"] == MessageRole.USER]
        assistant_messages = [m for m in messages if m["role"] == MessageRole.ASSISTANT]
        
        assert len(user_messages) >= 1
        assert len(assistant_messages) >= 1
        assert "financial metrics" in user_messages[0]["content"].lower()
        assert "claude" in assistant_messages[0]["content"].lower()
        
        # 5. List conversations
        list_response = client.get("/api/conversations/conversations")
        assert list_response.status_code == 200
        conversations = list_response.json()
        assert len(conversations) >= 1
        
        # Find our conversation in the list
        our_conversation = next(
            (c for c in conversations if c["conversation_id"] == conversation_id),
            None
        )
        assert our_conversation is not None
        assert our_conversation["title"] == "Test Integration Conversation"
        
        # 6. Delete the conversation
        delete_response = client.delete(
            f"/api/conversations/conversation/{conversation_id}"
        )
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["conversation_id"] == conversation_id
        assert delete_data["status"] == "deleted" 