#!/usr/bin/env python
"""
A utility script to verify PDF document context preparation.

This script accesses an existing document and conversation, and checks if Claude can "see" the document content.
"""

import os
import logging
import sys
import asyncio
from pdf_processing.langgraph_service import LangGraphService
from pdf_processing.claude_service import ClaudeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def check_document_context(document_id=None, conversation_id=None):
    """
    Check if a document can be properly seen by Claude in a conversation context.
    
    Args:
        document_id: ID of an existing document to check (if none provided, use the first one found)
        conversation_id: ID of an existing conversation to check (if none provided, use the first one found)
    """
    try:
        # Initialize Claude Service (which initializes LangGraph)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY environment variable is not set")
            return False
            
        logger.info(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        claude_service = ClaudeService(api_key=api_key)
        langgraph_service = claude_service.langgraph_service
        
        # Mock document content
        mock_document = {
            "id": document_id or "test-doc-1",
            "title": "Test Financial Report",
            "raw_text": "This is a test financial document with important data. Revenue: $1M, Profit: $200K",
            "processed": True
        }
        
        # Test document content preparation
        logger.info(f"Testing document context preparation with document: {mock_document['id']}")
        
        # Create a mock state with the document
        mock_state = {
            "messages": [],
            "documents": [mock_document],
            "citations": [],
            "active_documents": [mock_document["id"]],
            "context": {
                "documents_loaded": True
            }
        }
        
        # Try to prepare document context
        document_context = langgraph_service._prepare_document_context(mock_state)
        
        # Check if document content is included in the context
        if document_context:
            logger.info(f"Document context created successfully! Length: {len(document_context)}")
            logger.info(f"Document context preview: {document_context[:200]}...")
            
            # Verify document content is in context
            if "Revenue: $1M" in document_context:
                logger.info("✅ Document content is properly included in context")
            else:
                logger.warning("❌ Document content not found in context")
                
            return True
        else:
            logger.error("Failed to create document context")
            return False
            
    except Exception as e:
        logger.error(f"Error checking document context: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get document ID from command line if provided
    document_id = sys.argv[1] if len(sys.argv) > 1 else None
    conversation_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = asyncio.run(check_document_context(document_id, conversation_id))
    
    if result:
        logger.info("Document context check completed successfully")
        sys.exit(0)
    else:
        logger.error("Document context check failed")
        sys.exit(1)