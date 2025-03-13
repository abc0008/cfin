import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import Depends, FastAPI

# Import the API router directly instead of the main app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.router import api_router
from models.message import ConversationCreateRequest, MessageRequest
from api.conversation import get_langgraph_service, get_document_service

# Create a test app with just the API router
test_app = FastAPI()
test_app.include_router(api_router, prefix="/api")

# Create a test client
client = TestClient(test_app)

class TestConversationAPI:
    """Unit tests for conversation API endpoints."""
    
    @pytest.fixture
    def override_dependencies(self, mock_langgraph_service, mock_document_service, mock_session_service, mock_current_user_id):
        """Override the API dependencies with mocks."""
        # Override the API dependencies with mocks
        test_app.dependency_overrides[get_langgraph_service] = lambda: mock_langgraph_service
        test_app.dependency_overrides[get_document_service] = lambda: mock_document_service
        
        # Create a mock for get_session_service
        test_app.dependency_overrides["api.conversation.get_session_service"] = lambda: mock_session_service
        
        # Create a mock for get_current_user_id
        test_app.dependency_overrides["api.conversation.get_current_user_id"] = lambda: mock_current_user_id
        
        yield
        
        # Clean up
        test_app.dependency_overrides = {}
    
    def test_create_conversation(self, override_dependencies):
        """Test creating a new conversation."""
        # Arrange
        request_data = {
            "title": "Test Conversation",
            "user_id": "test-user",
            "document_ids": ["doc1", "doc2"],
            "metadata": {"test_key": "test_value"}
        }
        
        # Act
        response = client.post("/api/conversations/conversation", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["title"] == "Test Conversation"
        assert data["status"] == "created"
    
    def test_add_documents_to_conversation(self, override_dependencies):
        """Test adding documents to a conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        document_ids = ["doc1", "doc2"]
        
        # Act
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/documents",
            json=document_ids
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["documents_added"] == len(document_ids)
        assert data["document_ids"] == document_ids
        assert data["status"] == "documents_added"
    
    def test_send_message(self, override_dependencies):
        """Test sending a message in a conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        request_data = {
            "session_id": conversation_id,
            "content": "What financial ratios are important for analyzing this company?",
            "referenced_documents": ["doc1"],
            "citation_links": ["cite1"]
        }
        
        # Act
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/message",
            json=request_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == conversation_id
        assert data["role"] == "assistant"
        assert "content" in data
        assert "citations" in data
    
    def test_get_conversation_history(self, override_dependencies):
        """Test retrieving conversation history."""
        # Arrange
        conversation_id = "test-conversation-id"
        
        # Act
        response = client.get(f"/api/conversations/conversation/{conversation_id}/history")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == conversation_id
        assert "messages" in data
        assert len(data["messages"]) > 0
        assert "content" in data["messages"][0]
        assert "role" in data["messages"][0]
    
    def test_list_conversations(self, override_dependencies):
        """Test listing all conversations."""
        # Act
        response = client.get("/api/conversations/conversations")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "conversation_id" in data[0]
        assert "title" in data[0]
    
    def test_delete_conversation(self, override_dependencies):
        """Test deleting a conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        
        # Act
        response = client.delete(f"/api/conversations/conversation/{conversation_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["status"] == "deleted"
    
    def test_error_handling_conversation_not_found(self, override_dependencies, mock_langgraph_service):
        """Test error handling when conversation is not found."""
        # Arrange
        conversation_id = "nonexistent-id"
        mock_langgraph_service.process_message.side_effect = ValueError("Conversation not found")
        
        request_data = {
            "session_id": conversation_id,
            "content": "Hello"
        }
        
        # Act
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/message",
            json=request_data
        )
        
        # Assert
        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]
    
    def test_error_handling_document_not_found(self, override_dependencies, mock_document_service):
        """Test error handling when documents are not found."""
        # Arrange
        conversation_id = "test-conversation-id"
        # Configure the mock to return None for get_document
        mock_document_service.get_document.return_value = None
        
        # Act
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/documents",
            json=["nonexistent-doc"]
        )
        
        # Assert
        assert response.status_code == 404
        assert "No valid documents found" in response.json()["detail"]
    
    def test_pdf_citation_handling(self, override_dependencies, mock_langgraph_service):
        """Test that PDF citations are handled correctly."""
        # Arrange
        conversation_id = "test-conversation-id"
        
        # Setup mock response with multi-page citations
        mock_langgraph_service.process_message.return_value = {
            "conversation_id": "test-conversation-id",
            "message_id": "test-message-id",
            "content": "This is a test response with citations.",
            "role": "assistant",
            "citations": [
                {
                    "id": "citation-1",
                    "text": "first citation text",
                    "document_id": "test-document-id",
                    "document_title": "Test Document",
                    "document_index": 0,
                    "page": 2,  # Single page citation
                },
                {
                    "id": "citation-2",
                    "text": "second citation spanning multiple pages",
                    "document_id": "test-document-id-2",
                    "document_title": "Another Document",
                    "document_index": 1,
                    "page": 5,
                    "end_page": 7  # Multi-page citation (pages 5-6)
                }
            ]
        }
        
        request_data = {
            "session_id": conversation_id,
            "content": "Tell me about this document with citations",
            "referenced_documents": ["doc1"],
        }
        
        # Act
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/message",
            json=request_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check citations are included
        assert "citations" in data
        assert len(data["citations"]) == 2
        
        # Check first citation (single page)
        first_citation = data["citations"][0]
        assert first_citation["type"] == "page_location"
        assert first_citation["cited_text"] == "first citation text"
        assert first_citation["document_index"] == 0
        assert first_citation["document_title"] == "Test Document"
        assert first_citation["start_page_number"] == 2
        assert first_citation["end_page_number"] == 3  # Exclusive range for single page
        
        # Check second citation (multi-page)
        second_citation = data["citations"][1]
        assert second_citation["type"] == "page_location"
        assert second_citation["cited_text"] == "second citation spanning multiple pages"
        assert second_citation["document_index"] == 1
        assert second_citation["document_title"] == "Another Document"
        assert second_citation["start_page_number"] == 5
        assert second_citation["end_page_number"] == 7  # Preserves the exclusive range 