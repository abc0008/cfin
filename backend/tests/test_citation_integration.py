import unittest
import asyncio
import os
import sys
import json
import base64
from unittest.mock import patch, MagicMock
import pytest
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import pathlib

# Import required modules
from pdf_processing.langgraph_service import LangGraphService
from pdf_processing.claude_service import ClaudeService
from services.conversation_service import ConversationService
from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation

# Load environment variables from parent directory
parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

class TestCitationIntegration(unittest.TestCase):
    """Tests for citation integration with Claude API and LangGraph."""
    
    def setUp(self):
        """Initialize services for testing."""
        try:
            # Ensure we have the API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self.skipTest("Skipping test due to missing ANTHROPIC_API_KEY")
            
            # Initialize services
            self.claude_service = ClaudeService(api_key=api_key)
            self.langgraph_service = self.claude_service.langgraph_service
            
            # Create mock repositories for ConversationService
            self.mock_conversation_repo = MagicMock()
            self.mock_document_repo = MagicMock()
            self.mock_analysis_repo = MagicMock()
            
            # Initialize ConversationService with mocked repositories
            self.conversation_service = ConversationService(
                conversation_repository=self.mock_conversation_repo,
                document_repository=self.mock_document_repo,
                analysis_repository=self.mock_analysis_repo
            )
            
            # Set up reference to claude_service in conversation_service
            self.conversation_service.claude_service = self.claude_service
            
        except Exception as e:
            self.skipTest(f"Skipping citation tests due to initialization error: {e}")
    
    def create_mock_text_document(self) -> Dict[str, Any]:
        """Create a mock text document for testing."""
        return {
            "id": "doc1",
            "title": "Financial Report 2023",
            "mime_type": "text/plain",
            "content": "The company reported revenue of $10.5 million in 2023, which represents a 15% increase from 2022 when revenue was $9.1 million. Operating expenses were $7.2 million, resulting in a profit of $3.3 million.",
            "text": "The company reported revenue of $10.5 million in 2023, which represents a 15% increase from 2022 when revenue was $9.1 million. Operating expenses were $7.2 million, resulting in a profit of $3.3 million."
        }
    
    def create_mock_pdf_document(self) -> Dict[str, Any]:
        """Create a mock PDF document for testing."""
        # In a real test, this would be a real PDF file
        # For this test, we'll use a simple text file with a .pdf mime type
        return {
            "id": "doc2",
            "title": "Annual Report 2023",
            "mime_type": "application/pdf",
            "content": "The company reported revenue of $10.5 million in 2023, which represents a 15% increase from 2022 when revenue was $9.1 million. Operating expenses were $7.2 million, resulting in a profit of $3.3 million.".encode('utf-8'),
            "text": "The company reported revenue of $10.5 million in 2023, which represents a 15% increase from 2022 when revenue was $9.1 million. Operating expenses were $7.2 million, resulting in a profit of $3.3 million."
        }
    
    def test_citation_model_correctness(self):
        """Test that citation models are correctly defined."""
        # Create a character location citation
        char_citation = CharLocationCitation(
            type=CitationType.CHAR_LOCATION,
            cited_text="revenue of $10.5 million",
            document_index=0,
            document_title="Financial Report 2023",
            start_char_index=24,
            end_char_index=47
        )
        
        # Create a page location citation
        page_citation = PageLocationCitation(
            type=CitationType.PAGE_LOCATION,
            cited_text="revenue of $10.5 million",
            document_index=0,
            document_title="Annual Report 2023",
            start_page_number=1,
            end_page_number=2
        )
        
        # Verify citation types
        self.assertEqual(char_citation.type, CitationType.CHAR_LOCATION)
        self.assertEqual(page_citation.type, CitationType.PAGE_LOCATION)
        
        # Verify citation text
        self.assertEqual(char_citation.cited_text, "revenue of $10.5 million")
        self.assertEqual(page_citation.cited_text, "revenue of $10.5 million")
        
        # Verify location information
        self.assertEqual(char_citation.start_char_index, 24)
        self.assertEqual(char_citation.end_char_index, 47)
        self.assertEqual(page_citation.start_page_number, 1)
        self.assertEqual(page_citation.end_page_number, 2)
    
    def test_convert_citation_to_dict(self):
        """Test converting citation objects to dictionaries."""
        # Create a mock citation object with attributes
        mock_citation = MagicMock()
        mock_citation.type = "char_location"
        mock_citation.cited_text = "revenue of $10.5 million"
        mock_citation.document_index = 0
        mock_citation.document_title = "Financial Report 2023"
        mock_citation.start_char_index = 24
        mock_citation.end_char_index = 47
        
        # Convert the citation to a dictionary
        result = self.langgraph_service._convert_citation_to_dict(mock_citation)
        
        # Verify the dictionary has the right fields
        self.assertEqual(result["type"], "char_location")
        self.assertEqual(result["cited_text"], "revenue of $10.5 million")
        self.assertEqual(result["document_title"], "Financial Report 2023")
        self.assertEqual(result["document_index"], 0)
        self.assertEqual(result["start_char_index"], 24)
        self.assertEqual(result["end_char_index"], 47)
    
    @patch('pdf_processing.langgraph_service.ChatAnthropic')
    def test_simple_document_qa_with_citations(self, mock_anthropic):
        """Test the simple_document_qa method with citation-enabled documents."""
        # Create a mock response with citations
        mock_content = MagicMock()
        mock_content.text = "Based on the document, the company reported revenue of $10.5 million in 2023."
        mock_content.citations = [
            MagicMock(
                type="char_location",
                cited_text="revenue of $10.5 million in 2023",
                document_index=0,
                document_title="Financial Report 2023",
                start_char_index=24,
                end_char_index=55
            )
        ]
        
        # Set up the mock Anthropic client response
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_anthropic.return_value.invoke.return_value = mock_response
        
        # Create the document for testing
        document = self.create_mock_text_document()
        
        # Run the test
        response = asyncio.run(self.langgraph_service.simple_document_qa(
            question="What was the company's revenue in 2023?",
            documents=[document]
        ))
        
        # Verify the response
        self.assertIsInstance(response, dict)
        self.assertIn("content", response)
        self.assertIn("citations", response)
        self.assertEqual(response["content"], "Based on the document, the company reported revenue of $10.5 million in 2023.")
        self.assertEqual(len(response["citations"]), 1)
        self.assertEqual(response["citations"][0]["type"], "char_location")
        self.assertEqual(response["citations"][0]["cited_text"], "revenue of $10.5 million in 2023")
    
    @patch('services.conversation_service.ConversationService.add_message')
    @patch('pdf_processing.claude_service.ClaudeService.generate_response_with_langgraph')
    def test_process_with_langgraph_citations(self, mock_generate, mock_add_message):
        """Test the _process_with_langgraph method in ConversationService."""
        # Set up mock response from generate_response_with_langgraph
        mock_generate.return_value = {
            "content": "Based on the document, the company reported revenue of $10.5 million in 2023.",
            "citations": [
                {
                    "type": "char_location",
                    "cited_text": "revenue of $10.5 million in 2023",
                    "document_index": 0,
                    "document_title": "Financial Report 2023",
                    "start_char_index": 24,
                    "end_char_index": 55
                }
            ]
        }
        
        # Set up mock add_message response
        mock_message = MagicMock()
        mock_message.id = "msg1"
        mock_message.content = "Based on the document, the company reported revenue of $10.5 million in 2023."
        mock_add_message.return_value = mock_message
        
        # Set up document texts
        document_texts = [self.create_mock_text_document()]
        
        # Run the test
        result = asyncio.run(self.conversation_service._process_with_langgraph(
            conversation_id="conv1",
            content="What was the company's revenue in 2023?",
            document_texts=document_texts,
            messages=[]
        ))
        
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], mock_message)
        
        # Verify that add_message was called with citation IDs
        mock_add_message.assert_called_once()
        call_args = mock_add_message.call_args[1]
        self.assertEqual(call_args["conversation_id"], "conv1")
        self.assertEqual(call_args["content"], "Based on the document, the company reported revenue of $10.5 million in 2023.")
        self.assertEqual(call_args["role"], "assistant")
        self.assertIsNotNone(call_args["citation_ids"])
        
    @patch('pdf_processing.langgraph_service.ChatAnthropic')
    def test_pdf_document_citation_format(self, mock_anthropic):
        """Test that PDF documents are correctly formatted for citation."""
        # Mock the LLM response
        mock_anthropic.return_value.invoke.return_value = MagicMock(
            content=[
                MagicMock(
                    text="Based on the document, the company reported revenue of $10.5 million in 2023.",
                    citations=[
                        MagicMock(
                            type="page_location",
                            cited_text="revenue of $10.5 million in 2023",
                            document_index=0,
                            document_title="Annual Report 2023",
                            start_page_number=1,
                            end_page_number=2
                        )
                    ]
                )
            ]
        )
        
        # Create a PDF document
        document = self.create_mock_pdf_document()
        
        # Run the test with tracing to check document preparation
        with patch.object(self.langgraph_service, '_convert_citation_to_dict', wraps=self.langgraph_service._convert_citation_to_dict) as mock_convert:
            response = asyncio.run(self.langgraph_service.simple_document_qa(
                question="What was the company's revenue in 2023?",
                documents=[document]
            ))
            
            # Verify conversion was called with page_location citation
            mock_convert.assert_called()
            citation_arg = mock_convert.call_args[0][0]
            self.assertEqual(citation_arg.type, "page_location")
            
        # Verify the response has the right citation type
        self.assertEqual(response["citations"][0]["type"], "page_location")
        self.assertEqual(response["citations"][0]["start_page_number"], 1)
        self.assertEqual(response["citations"][0]["end_page_number"], 2)

if __name__ == "__main__":
    unittest.main() 