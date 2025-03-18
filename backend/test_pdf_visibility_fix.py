#!/usr/bin/env python
"""
A test script to verify PDF visibility fixes.

This script:
1. Creates a new conversation
2. Uploads a sample PDF file
3. Adds the PDF to the conversation
4. Sends a message asking about the PDF content
5. Verifies that Claude can "see" the PDF content in its response
"""

import os
import json
import asyncio
import logging
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import app and modules
from app.main import app
from services.conversation_service import ConversationService
from repositories.conversation_repository import ConversationRepository
from repositories.document_repository import DocumentRepository
from pdf_processing.claude_service import ClaudeService
from sqlalchemy.ext.asyncio import AsyncSession


# Create test client
client = TestClient(app)

async def test_pdf_visibility():
    """Test that Claude can "see" the content of an uploaded PDF"""
    try:
        # We'll use the FastAPI test client instead of direct service calls
        # to avoid database session management complexities
        
        # Step 1: Create a new conversation
        logger.info("Creating a new conversation...")
        user_id = str(uuid.uuid4())
        conversation_response = client.post(
            "/api/conversation",
            json={"title": "PDF Visibility Test", "user_id": user_id}
        )
        assert conversation_response.status_code in [200, 201], f"Failed to create conversation: {conversation_response.text}"
        conversation_data = conversation_response.json()
        # API might return id or session_id 
        conversation_id = conversation_data.get("id", conversation_data.get("session_id"))
        logger.info(f"Created conversation with ID: {conversation_id}")
        
        # Step 2: Upload a test PDF
        logger.info("Uploading test PDF...")
        test_pdf_path = "test_data/sample_financial_report.pdf"
        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found at {test_pdf_path}, using sample.pdf instead")
            test_pdf_path = "test_data/sample.pdf"
        
        with open(test_pdf_path, "rb") as pdf_file:
            response = client.post(
                "/api/documents/upload",
                files={"file": ("test_financial_report.pdf", pdf_file, "application/pdf")},
                data={"user_id": user_id}
            )
        
        assert response.status_code == 200, f"Failed to upload PDF: {response.text}"
        upload_data = response.json()
        document_id = upload_data["document_id"]
        logger.info(f"Uploaded document with ID: {document_id}")
        
        # Wait for document processing to complete
        logger.info("Waiting for document processing to complete...")
        retries = 30  # Increased from 10 to 30
        processing_completed = False
        
        for i in range(retries):
            doc_response = client.get(f"/api/documents/{document_id}")
            assert doc_response.status_code == 200, f"Failed to get document: {doc_response.text}"
            doc_data = doc_response.json()
            
            if doc_data["processing_status"] == "completed":
                processing_completed = True
                logger.info("Document processing completed successfully!")
                break
                
            if doc_data["processing_status"] == "failed":
                assert False, f"Document processing failed: {doc_data.get('error_message', 'Unknown error')}"
                
            logger.info(f"Document status: {doc_data['processing_status']} (attempt {i+1}/{retries})")
            await asyncio.sleep(3)  # Increased from 2 to 3 seconds
        
        assert processing_completed, "Document processing did not complete in time"
        
        # Step 3: Add PDF to conversation
        logger.info("Adding document to conversation...")
        add_doc_response = client.post(
            f"/api/conversation/{conversation_id}/document/{document_id}"
        )
        assert add_doc_response.status_code == 200, f"Failed to add document to conversation: {add_doc_response.text}"
        logger.info("Document added to conversation successfully")
        
        # Step 4: Send a message asking about the PDF
        logger.info("Sending message to conversation...")
        message = "What information do you see in the PDF I uploaded? Please provide specific details from the document."
        
        message_response = client.post(
            f"/api/conversation/{conversation_id}/message",
            json={"content": message}
        )
        assert message_response.status_code == 200, f"Failed to send message: {message_response.text}"
        response_data = message_response.json()
        
        # Step 5: Verify Claude's response mentions PDF content
        logger.info("Checking Claude's response...")
        messages_response = client.get(f"/api/conversation/{conversation_id}/messages")
        assert messages_response.status_code == 200, f"Failed to get messages: {messages_response.text}"
        
        messages = messages_response.json()
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        # Get the latest assistant message
        if assistant_messages:
            latest_message = assistant_messages[-1]
            response_text = latest_message["content"]
            
            logger.info(f"Claude's response: {response_text[:200]}...")
            
            # Check if the response contains actual content from the PDF
            # This depends on the test PDF content, so we check for general indicators
            # that Claude can see the document
            assert "I can see" in response_text or "document shows" in response_text or "according to" in response_text, \
                "Claude's response doesn't indicate it can see the document content"
            
            # Check for citations
            if "citations" in latest_message and latest_message["citations"]:
                logger.info(f"Found {len(latest_message['citations'])} citations in response")
                for citation in latest_message["citations"]:
                    logger.info(f"Citation: {citation}")
            else:
                logger.info("No citations found in response")
            
            logger.info("✅ Test passed! Claude can see the PDF content")
            
        else:
            logger.error("No assistant messages found in the conversation")
            assert False, "No assistant messages found"
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_pdf_visibility())