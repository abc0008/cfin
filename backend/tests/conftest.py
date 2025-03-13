import pytest
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set up test environment variables
os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
os.environ["SQLITE_DB_URL"] = "sqlite:///test.db"
os.environ["STORAGE_TYPE"] = "local"
os.environ["LOCAL_STORAGE_PATH"] = "./test_uploads"

# Load test environment variables
# load_dotenv(".env.test")  # Uncomment and create this file when needed

# Test database configuration 
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# For pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db_engine():
    """Create a test database engine."""
    from database.session import Base  # Import here to avoid circular imports
    
    engine = create_async_engine(TEST_DB_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine):
    """Create a test database session."""
    TestSessionLocal = sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def mock_current_user_id():
    """Mock the current user ID."""
    return str(uuid.uuid4())

@pytest.fixture
def mock_claude_service():
    """Create a mock Claude service for testing."""
    with patch('pdf_processing.claude_service.ClaudeService') as mock:
        service = MagicMock()
        
        # Mock the process_pdf method
        service.process_pdf.return_value = (MagicMock(), [])
        
        # Mock the generate_response_with_citations method with a response
        # using the updated Claude model
        service.generate_response_with_citations.return_value = {
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
            "model": "claude-3-5-sonnet-latest",  # Updated model name
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 150,
                "output_tokens": 50
            }
        }
        
        mock.return_value = service
        yield service

@pytest.fixture
def mock_langgraph_service():
    """Create a mock LangGraph service for testing."""
    service = MagicMock()
    
    # Mock initialize_conversation with AsyncMock
    service.initialize_conversation = AsyncMock()
    service.initialize_conversation.return_value = {
        "conversation_id": "test-conversation-id",
        "status": "initialized",
        "state": {
            "conversation_id": "test-conversation-id",
            "messages": [],
            "documents": [],
            "citations": [],
            "active_documents": [],
            "context": {"created_at": "2023-01-01T00:00:00"}
        }
    }
    
    # Mock add_documents_to_conversation with AsyncMock
    service.add_documents_to_conversation = AsyncMock()
    service.add_documents_to_conversation.return_value = {
        "conversation_id": "test-conversation-id",
        "status": "documents_added",
        "document_count": 2,
        "citation_count": 5
    }
    
    # Mock process_message with AsyncMock
    service.process_message = AsyncMock()
    service.process_message.return_value = {
        "conversation_id": "test-conversation-id",
        "message_id": "test-message-id",
        "content": "This is a test response from the assistant.",
        "role": "assistant",
        "citations": [
            {
                "id": "citation-1",
                "text": "test data",
                "document_id": "test-document-id",
                "document_title": "Test Document",
                "page": 1
            }
        ]
    }
    
    # Mock get_conversation_history with AsyncMock
    service.get_conversation_history = AsyncMock()
    service.get_conversation_history.return_value = [
        {
            "id": "user-message-id",
            "conversation_id": "test-conversation-id",
            "content": "What does this document say about financial ratios?",
            "role": "user",
            "timestamp": "2023-01-01T00:00:00",
            "citations": []
        },
        {
            "id": "assistant-message-id",
            "conversation_id": "test-conversation-id",
            "content": "This is a test response from the assistant.",
            "role": "assistant",
            "timestamp": "2023-01-01T00:00:01",
            "citations": [
                {
                    "id": "citation-1",
                    "text": "test data",
                    "document_id": "test-document-id",
                    "document_title": "Test Document",
                    "page": 1
                }
            ]
        }
    ]
    
    return service

@pytest.fixture
def mock_document_service():
    """Create a mock Document service for testing."""
    service = MagicMock()
    
    # Mock get_document with AsyncMock
    service.get_document = AsyncMock()
    service.get_document.return_value = {
        "id": "test-document-id",
        "filename": "test_document.pdf",
        "upload_timestamp": "2023-01-01T00:00:00",
        "file_size": 1000,
        "content_type": "balance_sheet",
        "extraction_timestamp": "2023-01-01T00:00:01",
        "extracted_data": {"raw_text": "This is test financial data"}
    }
    
    return service

@pytest.fixture
def mock_session_service():
    """Create a mock Session service for testing."""
    service = MagicMock()
    
    # Mock get_sessions_for_user with AsyncMock
    service.get_sessions_for_user = AsyncMock()
    service.get_sessions_for_user.return_value = [
        type('obj', (object,), {
            'id': 'test-conversation-id', 
            'title': 'Test Conversation',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:01',
            'documents': []
        })
    ]
    
    # Mock delete_session with AsyncMock
    service.delete_session = AsyncMock()
    service.delete_session.return_value = True
    
    return service 