#!/usr/bin/env python3
"""
Test runner for document visibility tests
Used to diagnose issues with the LLM not recognizing uploaded documents
"""

import os
import sys
import asyncio
import logging
import pytest
import uuid
from dotenv import load_dotenv
from datetime import datetime as dt

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("document_visibility")

async def run_tests():
    """Run the document visibility tests"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check that essential environment variables are set
        required_vars = ["ANTHROPIC_API_KEY", "CLAUDE_MODEL"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file")
            return 1
            
        logger.info(f"Using Claude model: {os.environ.get('CLAUDE_MODEL')}")
        
        # Run the pytest tests with verbose output
        logger.info("Running document visibility tests...")
        result = pytest.main(["-v", "tests/test_document_visibility.py"])
        
        if result == 0:
            logger.info("All tests passed!")
        else:
            logger.error(f"Tests failed with exit code {result}")
            
        return result
        
    except Exception as e:
        logger.exception(f"Error running tests: {e}")
        return 1

async def test_debug_endpoint():
    """Test a document visibility with LangGraph directly"""
    try:
        from pdf_processing.langgraph_service import LangGraphService
        from unittest.mock import MagicMock, patch
        
        # Create a test conversation ID
        conversation_id = str(uuid.uuid4())
        logger.info(f"Created test conversation with ID: {conversation_id}")
        
        # Create a test document
        from models.document import ProcessedDocument, DocumentMetadata, DocumentContentType
        
        document = ProcessedDocument(
            metadata=DocumentMetadata(
                id=uuid.uuid4(),
                user_id="test-user",
                filename="financial_report.txt",
                file_type="text/plain",
                title="Financial Report 2024",
                upload_timestamp=dt.now(),
                file_size=1024,
                mime_type="text/plain"
            ),
            content_type=DocumentContentType.INCOME_STATEMENT,
            extraction_timestamp=dt.now(),
            periods=["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"],
            extracted_data={
                "raw_text": """
                Financial Report 2024
                
                This report contains important data. Revenue: $1M, Profit: $200K
                
                Quarter 1:
                - Revenue: $250K
                - Expenses: $200K
                - Profit: $50K
                
                Quarter 2:
                - Revenue: $250K
                - Expenses: $200K
                - Profit: $50K
                
                Quarter 3:
                - Revenue: $250K
                - Expenses: $200K
                - Profit: $50K
                
                Quarter 4:
                - Revenue: $250K
                - Expenses: $200K
                - Profit: $50K
                """
            },
            citations=[],
            processing_status="completed"
        )
        
        # Create a mock response for the LLM
        mock_response = MagicMock()
        mock_response.content = [{"type": "text", "text": "Based on the financial report, the revenue is $1M and the profit is $200K."}]
        mock_response.model_dump.return_value = {
            "content": [{"type": "text", "text": "Based on the financial report, the revenue is $1M and the profit is $200K."}]
        }
        
        # Create a mock citation
        mock_citation = {
            "start": 10,
            "end": 50,
            "text": "financial report, the revenue is $1M and the profit is $200K",
            "document_id": str(document.metadata.id),
            "quote": "important data. Revenue: $1M, Profit: $200K"
        }
        
        # Create patch context managers
        llm_patch = patch('langchain_anthropic.ChatAnthropic.invoke', return_value=mock_response)
        citations_patch = patch('pdf_processing.langgraph_service.LangGraphService._extract_citations_from_response', 
                                return_value=[mock_citation])
        
        # Apply the patches
        llm_patch.start()
        citations_patch.start()
        
        try:
            # Get the LangGraph service
            try:
                from dependencies import get_langgraph_service
                langgraph_service = get_langgraph_service()
            except ImportError:
                langgraph_service = LangGraphService()
            
            # Mock the conversation_graph.stream method directly on the instance
            mock_stream = MagicMock()
            mock_stream.return_value = [{"type": "on_chain_end", "output": {}}]
            langgraph_service.conversation_graph.stream = mock_stream
            
            # Initialize a conversation
            await langgraph_service.initialize_conversation(
                conversation_id=conversation_id,
                user_id="test-user"
            )
            logger.info(f"Initialized conversation: {conversation_id}")
            
            # Add the document to the conversation
            result = await langgraph_service.add_documents_to_conversation(
                conversation_id=conversation_id,
                documents=[document]
            )
            logger.info(f"Added document to conversation: {result}")
            
            # Send a message to test document visibility
            response = await langgraph_service.process_message(
                conversation_id=conversation_id,
                message_content="What's the revenue and profit according to the financial report?"
            )
            logger.info(f"Chat response: {response}")
            
            # Debug information about the conversation states
            logger.info(f"Conversation service dict keys: {dir(langgraph_service)}")
            logger.info(f"Conversation states keys: {langgraph_service.conversation_states.keys()}")
            
            # Verify conversation state exists and contains document content
            if conversation_id in langgraph_service.conversation_states:
                state = langgraph_service.conversation_states[conversation_id]
                logger.info(f"Found state with conversation ID: {state}")
                if state and "documents" in state and len(state["documents"]) > 0:
                    doc_content = state["documents"][0].get("extracted_data", {}).get("raw_text", "")
                    if "Revenue: $1M, Profit: $200K" in doc_content:
                        logger.info("Document content found in conversation state!")
                        return True
                    else:
                        logger.error("Document content not found in conversation state")
                else:
                    logger.error("No documents found in conversation state: " + str(state))
            else:
                # Try to find if there's a thread ID mapping for this conversation ID
                for thread_id, state in langgraph_service.conversation_states.items():
                    logger.info(f"Checking thread ID: {thread_id}")
                    if isinstance(state, dict) and state.get("conversation_id") == conversation_id:
                        logger.info(f"Found conversation state with thread ID: {thread_id}")
                        if "documents" in state and len(state["documents"]) > 0:
                            doc_content = state["documents"][0].get("extracted_data", {}).get("raw_text", "")
                            if "Revenue: $1M, Profit: $200K" in doc_content:
                                logger.info("Document content found in conversation state!")
                                return True
                            else:
                                logger.error("Document content not found in thread state")
                                return False
                
                # If we reach here, we couldn't find the state
                logger.error("Conversation state not found")
            
            return False
        
        finally:
            # Stop all patches
            llm_patch.stop()
            citations_patch.stop()
            
    except Exception as e:
        logger.exception(f"Error testing document visibility: {e}")
        return False

async def main():
    """Main entry point"""
    logger.info("===== Document Visibility Test Suite =====")
    
    # Run the visibility tests
    test_result = await run_tests()
    
    # Test document visibility directly with LangGraph
    debug_result = await test_debug_endpoint()
    
    if test_result == 0 and debug_result:
        logger.info("All tests completed successfully!")
        return 0
    else:
        logger.error("Some tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
