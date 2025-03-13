import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid
from typing import Dict, Any, List
from models.document import ProcessedDocument, DocumentMetadata, DocumentContentType, Citation
from models.citation import PageLocationCitation, CitationType

# Import the service to test
from pdf_processing.langgraph_service import LangGraphService, AgentState

class TestLangGraphService:
    """Unit tests for LangGraphService."""
    
    @pytest.fixture
    def mock_memory_saver(self):
        """Create a mock MemorySaver."""
        with patch('pdf_processing.langgraph_service.MemorySaver') as mock:
            memory = MagicMock()
            
            # Mock save method
            memory.save = AsyncMock()
            
            # Mock load method
            def mock_load(thread_id, config_name):
                if thread_id == "conversation_test-conversation-id":
                    return {
                        "conversation_id": "test-conversation-id",
                        "messages": [],
                        "documents": [],
                        "citations": [],
                        "active_documents": [],
                        "current_message": None,
                        "current_response": None,
                        "citations_used": [],
                        "context": {"user_id": "test-user-id"}
                    }
                return None
            
            memory.load = MagicMock(side_effect=mock_load)
            mock.return_value = memory
            yield memory
    
    @pytest.fixture
    def mock_anthropic(self):
        """Create a mock ChatAnthropic."""
        with patch('pdf_processing.langgraph_service.ChatAnthropic') as mock:
            client = MagicMock()
            client.invoke = MagicMock(return_value=MagicMock(content="test response"))
            mock.return_value = client
            yield client
    
    @pytest.fixture
    def service(self, mock_memory_saver, mock_anthropic):
        """Create an instance of LangGraphService with mocked dependencies."""
        # Mock environment variable for API key
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            # Mock the conversation graph
            with patch('pdf_processing.langgraph_service.StateGraph') as mock_graph:
                # Create a mock compiled graph
                compiled_graph = MagicMock()
                compiled_graph.stream = MagicMock(return_value=[{'type': 'event'}])
                compiled_graph.get_config = MagicMock(return_value=MagicMock(name="test-graph"))
                
                # Make the StateGraph return the compiled graph when compiled
                mock_instance = MagicMock()
                mock_instance.compile.return_value = compiled_graph
                mock_graph.return_value = mock_instance
                
                service = LangGraphService()
                service.memory = mock_memory_saver
                service.conversation_graph = compiled_graph
                yield service
    
    @pytest.mark.asyncio
    async def test_initialize_conversation(self, service):
        """Test initializing a new conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        user_id = "test-user-id"
        document_ids = ["doc1", "doc2"]
        conversation_title = "Test Conversation"
        
        # Act
        result = await service.initialize_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            document_ids=document_ids,
            conversation_title=conversation_title
        )
        
        # Assert
        assert result["conversation_id"] == conversation_id
        assert result["status"] == "initialized"
        assert "state" in result
        
        # Verify state properties
        state = result["state"]
        assert state["conversation_id"] == conversation_id
        assert state["active_documents"] == document_ids
        assert state["context"]["user_id"] == user_id
        assert state["context"]["title"] == conversation_title
        
        # Verify memory.save was called
        service.memory.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_documents_to_conversation(self, service):
        """Test adding documents to a conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        
        # Create test documents
        documents = []
        for i in range(2):
            doc_id = str(uuid.uuid4())  # Use valid UUID
            metadata = DocumentMetadata(
                id=doc_id,
                filename=f"test_doc_{i}.pdf",
                upload_timestamp="2023-01-01T00:00:00",
                file_size=1000,
                mime_type="application/pdf",  # Add required mime_type
                user_id="test-user-id"
            )
            
            # Create proper Citation objects from models.document
            citation = Citation(
                id=f"cite{i}",
                text=f"Citation {i}",
                page=1
            )
            
            document = ProcessedDocument(
                metadata=metadata,
                content_type=DocumentContentType.BALANCE_SHEET,
                extraction_timestamp="2023-01-01T00:00:01",
                extracted_data={"raw_text": f"Test content for document {i}"},
                citations=[citation]
            )
            documents.append(document)
        
        # Act
        result = await service.add_documents_to_conversation(
            conversation_id=conversation_id,
            documents=documents
        )
        
        # Assert
        assert result["conversation_id"] == conversation_id
        assert result["status"] == "documents_added"
        assert result["document_count"] == len(documents)
        assert "citation_count" in result
        
        # Verify memory.save was called
        service.memory.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_message(self, service):
        """Test processing a message in a conversation."""
        # Arrange
        conversation_id = "test-conversation-id"
        message_content = "What does this document say about financial ratios?"
        cited_document_ids = ["doc1"]
        
        # Act
        result = await service.process_message(
            conversation_id=conversation_id,
            message_content=message_content,
            cited_document_ids=cited_document_ids
        )
        
        # Assert
        assert result["conversation_id"] == conversation_id
        assert "message_id" in result
        assert "content" in result
        assert result["role"] == "assistant"
        
        # Verify the conversation_graph.stream was called
        service.conversation_graph.stream.assert_called_once()
        
        # Verify memory.save was called twice (before and after processing)
        assert service.memory.save.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, service):
        """Test retrieving conversation history."""
        # Arrange
        conversation_id = "test-conversation-id"
        limit = 10
        
        # Mock the memory to return a state with messages
        messages = [
            {
                "role": "user",
                "content": "What are the key financial metrics?",
                "timestamp": "2023-01-01T00:00:00",
                "citations": []
            },
            {
                "role": "assistant",
                "content": "The key financial metrics include...",
                "timestamp": "2023-01-01T00:00:01",
                "citations": [{"id": "cite1", "text": "Financial metrics citation"}]
            }
        ]
        
        service.memory.load = MagicMock(return_value={
            "conversation_id": conversation_id,
            "messages": messages,
            "documents": [],
            "citations": [],
            "active_documents": [],
            "context": {}
        })
        
        # Act
        result = await service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        
        # Assert
        assert len(result) == len(messages)
        assert result[0]["content"] == messages[0]["content"]
        assert result[1]["content"] == messages[1]["content"]
        assert "conversation_id" in result[0]
        assert "id" in result[0]
    
    @pytest.mark.asyncio
    async def test_conversation_not_found(self, service):
        """Test error handling when conversation is not found."""
        # Arrange
        conversation_id = "nonexistent-id"
        service.memory.load = MagicMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Conversation {conversation_id} not found"):
            await service.process_message(
                conversation_id=conversation_id,
                message_content="Hello"
            )
    
    @pytest.mark.asyncio
    async def test_extract_citations_from_text(self, service):
        """Test extracting citations from text."""
        # Arrange
        text = "This is a test text with a citation [Citation: cite1] and another [Citation: cite2]."
        available_citations = [
            {"id": "cite1", "text": "Citation 1 text"},
            {"id": "cite2", "text": "Citation 2 text"},
            {"id": "cite3", "text": "Citation 3 text"}
        ]
        
        # Act
        processed_text, used_citations = service._extract_citations_from_text(text, available_citations)
        
        # Assert
        assert processed_text == text
        assert len(used_citations) == 2
        assert used_citations[0]["id"] == "cite1"
        assert used_citations[1]["id"] == "cite2" 