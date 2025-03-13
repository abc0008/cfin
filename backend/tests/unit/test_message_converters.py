import pytest
from datetime import datetime
import uuid
from dateutil.parser import parse

from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation, ContentBlock
from models.message import Message, MessageRole
from utils.message_converters import (
    claude_message_to_internal,
    internal_message_to_claude,
    frontend_message_to_internal,
    internal_message_to_frontend,
    _convert_claude_citation,
    _convert_internal_citation_to_claude,
    _convert_frontend_citation,
    _convert_internal_citation_to_frontend
)

class TestMessageConverters:
    """Unit tests for message format converters."""
    
    def test_claude_message_to_internal(self):
        """Test converting a Claude API message to internal model."""
        # Arrange
        claude_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is a response with a citation.",
                    "citations": [
                        {
                            "type": "char_location",
                            "id": "citation-1",
                            "start_char_offset": 10,
                            "end_char_offset": 20,
                            "content": {"quote": "sample text"},
                            "document": {"title": "Test Doc", "url": ""}
                        }
                    ]
                }
            ],
            "model": "claude-3-5-sonnet-latest"
        }
        
        # Act
        message = claude_message_to_internal(claude_message)
        
        # Assert
        assert message.role == MessageRole.ASSISTANT
        assert "This is a response with a citation." in message.content
        assert len(message.citations) > 0
        assert message.citations[0].type == CitationType.CHAR_LOCATION
        assert message.citations[0].cited_text == "sample text"
        assert len(message.content_blocks) > 0 if message.content_blocks else True
    
    def test_claude_message_to_internal_with_string_content(self):
        """Test converting a Claude API message with string content to internal model."""
        # Arrange
        claude_message = {
            "role": "user",
            "content": "This is a simple text message without citations.",
            "session_id": "test-session"
        }
        
        # Act
        message = claude_message_to_internal(claude_message)
        
        # Assert
        assert message.role == MessageRole.USER
        assert message.content == "This is a simple text message without citations."
        assert message.session_id == "test-session"
        assert not message.citations
    
    def test_internal_message_to_claude(self):
        """Test converting an internal message model to Claude API format."""
        # Arrange
        citation = CharLocationCitation(
            type=CitationType.CHAR_LOCATION,
            cited_text="sample text",
            document_index=0,
            document_title="Test Doc",
            start_char_index=10,
            end_char_index=20
        )
        
        content_block = ContentBlock(
            text="This is a test message with citation",
            citations=[citation]
        )
        
        message = Message(
            id=str(uuid.uuid4()),
            session_id="session-1",
            timestamp=datetime.now().isoformat(),
            role=MessageRole.ASSISTANT,
            content="This is a test message with citation",
            content_blocks=[content_block],
            citations=[citation]
        )
        
        # Act
        claude_message = internal_message_to_claude(message)
        
        # Assert
        assert claude_message["role"] == "assistant"
        assert isinstance(claude_message["content"], list)
        assert len(claude_message["content"]) > 0
        
        first_block = claude_message["content"][0]
        assert first_block["type"] == "text"
        assert "This is a test message with citation" in first_block["text"]
        
        if "citations" in first_block:
            citations = first_block["citations"]
            assert len(citations) > 0
            assert citations[0]["type"] == "char_location"
            assert citations[0]["content"]["quote"] == "sample text"
    
    def test_internal_message_to_claude_without_content_blocks(self):
        """Test converting an internal message without content blocks to Claude API format."""
        # Arrange
        message = Message(
            id=str(uuid.uuid4()),
            session_id="session-1",
            timestamp=datetime.now().isoformat(),
            role=MessageRole.USER,
            content="This is a simple message without citations"
        )
        
        # Act
        claude_message = internal_message_to_claude(message)
        
        # Assert
        assert claude_message["role"] == "user"
        assert isinstance(claude_message["content"], list)
        assert len(claude_message["content"]) == 1
        assert claude_message["content"][0]["type"] == "text"
        assert claude_message["content"][0]["text"] == "This is a simple message without citations"
    
    def test_frontend_message_to_internal(self):
        """Test converting a frontend message to internal model."""
        # Arrange
        frontend_message = {
            "id": str(uuid.uuid4()),  # Use UUID string instead of "msg-1"
            "sessionId": "session-1",
            "timestamp": "2023-01-01T00:00:00Z",
            "role": "user",
            "content": "What are the key financial metrics?",
            "referencedDocuments": ["doc-1", "doc-2"],
            "referencedAnalyses": ["analysis-1"],
            "citationLinks": [
                {
                    "id": "citation-1",
                    "text": "Financial metrics definition",
                    "page": 5,
                    "boundingBox": {"x": 100, "y": 200, "width": 300, "height": 50},
                    "documentId": "doc-1",
                    "title": "Annual Report"
                }
            ]
        }
        
        # Act
        message = frontend_message_to_internal(frontend_message)
        
        # Assert
        assert message.session_id == "session-1"
        assert message.timestamp.isoformat().startswith("2023-01-01T00:00:00")  # Check just the date part
        assert message.role == MessageRole.USER
        assert message.content == "What are the key financial metrics?"
        assert message.referenced_documents == ["doc-1", "doc-2"]
        assert message.referenced_analyses == ["analysis-1"]
        
        assert len(message.citations) > 0
        assert message.citations[0].type == CitationType.PAGE_LOCATION
        assert message.citations[0].cited_text == "Financial metrics definition"
        assert message.citations[0].start_page_number == 5
    
    def test_internal_message_to_frontend(self):
        """Test converting an internal message to frontend format."""
        # Arrange
        citation = PageLocationCitation(
            type=CitationType.PAGE_LOCATION,
            cited_text="Financial data from page 5",
            document_index=0,
            document_title="Annual Report",
            start_page_number=5,
            end_page_number=5
        )
        
        test_timestamp = parse("2023-01-01T00:00:00Z")
        message = Message(
            id=str(uuid.uuid4()),  # Use UUID string instead of "msg-1"
            session_id="session-1",
            timestamp=test_timestamp,
            role=MessageRole.ASSISTANT,
            content="Here's the analysis of financial metrics...",
            citations=[citation],
            referenced_documents=["doc-1"],
            referenced_analyses=["analysis-1"]
        )
        
        # Act
        frontend_message = internal_message_to_frontend(message)
        
        # Assert
        assert frontend_message["sessionId"] == "session-1"
        # Check that the timestamp is the same datetime object
        assert frontend_message["timestamp"] == test_timestamp
        assert frontend_message["role"] == "assistant"
        assert frontend_message["content"] == "Here's the analysis of financial metrics..."
        assert frontend_message["referencedDocuments"] == ["doc-1"]
        assert frontend_message["referencedAnalyses"] == ["analysis-1"]
        
        assert "citationLinks" in frontend_message
        assert len(frontend_message["citationLinks"]) > 0
        assert frontend_message["citationLinks"][0]["text"] == "Financial data from page 5"
        assert frontend_message["citationLinks"][0]["page"] == 5
    
    def test_convert_claude_citation(self):
        """Test converting a Claude API citation to internal citation model."""
        # Arrange - Char location citation
        char_location_citation = {
            "type": "char_location",
            "id": "char-citation",
            "start_char_offset": 10,
            "end_char_offset": 20,
            "content": {"quote": "text citation"},
            "document": {"title": "Text Document", "url": "http://example.com/text"}
        }
        
        # Arrange - Page location citation
        page_location_citation = {
            "type": "page_location",
            "id": "page-citation",
            "page": 5,
            "bounding_box": {"x": 100, "y": 200, "width": 300, "height": 50},
            "content": {"quote": "page citation"},
            "document": {"title": "PDF Document", "url": "http://example.com/pdf"}
        }
        
        # Act
        char_citation = _convert_claude_citation(char_location_citation)
        page_citation = _convert_claude_citation(page_location_citation)
        
        # Assert - Char location citation
        assert char_citation is not None
        assert char_citation.type == CitationType.CHAR_LOCATION
        assert char_citation.cited_text == "text citation"
        assert char_citation.start_char_index == 10
        assert char_citation.end_char_index == 20
        assert char_citation.document_title == "Text Document"
        
        # Assert - Page location citation
        assert page_citation is not None
        assert page_citation.type == CitationType.PAGE_LOCATION
        assert page_citation.cited_text == "page citation"
        assert page_citation.start_page_number == 5
        assert page_citation.end_page_number == 5
        assert page_citation.document_title == "PDF Document"
    
    def test_convert_internal_citation_to_claude(self):
        """Test converting an internal citation to Claude API format."""
        # Arrange - Char location citation
        char_citation = CharLocationCitation(
            type=CitationType.CHAR_LOCATION,
            cited_text="text citation",
            document_index=0,
            document_title="Text Document",
            start_char_index=10,
            end_char_index=20
        )
        
        # Arrange - Page location citation
        page_citation = PageLocationCitation(
            type=CitationType.PAGE_LOCATION,
            cited_text="page citation",
            document_index=1,
            document_title="PDF Document",
            start_page_number=5,
            end_page_number=5
        )
        
        # Act
        claude_char_citation = _convert_internal_citation_to_claude(char_citation)
        claude_page_citation = _convert_internal_citation_to_claude(page_citation)
        
        # Assert - Char location citation
        assert claude_char_citation["type"] == "char_location"
        assert claude_char_citation["content"]["quote"] == "text citation"
        assert claude_char_citation["start_char_offset"] == 10
        assert claude_char_citation["end_char_offset"] == 20
        assert claude_char_citation["document"]["title"] == "Text Document"
        
        # Assert - Page location citation
        assert claude_page_citation["type"] == "page_location"
        assert claude_page_citation["content"]["quote"] == "page citation"
        assert claude_page_citation["page"] == 5
        assert claude_page_citation["document"]["title"] == "PDF Document" 