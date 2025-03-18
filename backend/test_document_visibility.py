#!/usr/bin/env python
"""
Test script to verify document upload and visibility to the LLM.
This script tests the full flow from uploading a document to a conversation
and verifying that Claude can see and reference the document content.
"""

import os
import asyncio
import logging
import uuid
import time
from dotenv import load_dotenv
from repositories.document_repository import DocumentRepository
from repositories.conversation_repository import ConversationRepository
from pdf_processing.langgraph_service import LangGraphService
from pdf_processing.document_service import DocumentService
from services.conversation_service import ConversationService
from utils.database import SessionLocal
from models.database_models import ProcessingStatusEnum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Verify API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logger.error("ANTHROPIC_API_KEY not found in environment variables!")
    exit(1)

claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
logger.info(f"Using Claude model: {claude_model}")

# Sample PDF path - using an existing financial report
PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "ExampleDocs", 
    "Mueller Industries Earnings Release.pdf"
)

async def wait_for_document_processing(document_repository, document_id, timeout=120):
    """Wait for document processing to complete, with a timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        doc = await document_repository.get_document(document_id)
        logger.info(f"Document status: {doc.processing_status}")
        
        if doc.processing_status == ProcessingStatusEnum.COMPLETED:
            logger.info(f"Document processing completed in {time.time() - start_time:.2f} seconds")
            return True
        elif doc.processing_status == ProcessingStatusEnum.FAILED:
            logger.error(f"Document processing failed after {time.time() - start_time:.2f} seconds")
            return False
        
        # Wait a bit before checking again
        await asyncio.sleep(5)
    
    logger.error(f"Document processing timed out after {timeout} seconds")
    return False

async def test_document_visibility():
    """
    Test the complete flow:
    1. Create a conversation
    2. Upload a document
    3. Add document to conversation
    4. Send a message asking about the document
    5. Check if Claude responds with document citations
    """
    logger.info("=== Starting Document Visibility Test ===")
    
    # Check if test PDF exists
    if not os.path.exists(PDF_PATH):
        logger.error(f"Test PDF not found at {PDF_PATH}")
        return
    
    # Generate a unique test user ID for this test run
    test_user_id = f"test-user-{uuid.uuid4()}"
    
    # Read the test PDF
    with open(PDF_PATH, "rb") as f:
        pdf_data = f.read()
    
    async with SessionLocal() as session:
        # Initialize repositories and services
        document_repository = DocumentRepository(session)
        conversation_repository = ConversationRepository(session)
        
        document_service = DocumentService(document_repository)
        conversation_service = ConversationService(conversation_repository, document_repository)
        
        try:
            langgraph_service = LangGraphService()
            logger.info("Successfully initialized LangGraphService")
        except Exception as e:
            logger.error(f"Failed to initialize LangGraphService: {str(e)}")
            return None
        
        try:
            # Step 1: Create a conversation
            logger.info("Step 1: Creating a conversation")
            conversation = await conversation_service.create_conversation(
                user_id=test_user_id,
                title="Document Visibility Test"
            )
            conversation_id = str(conversation.id)
            logger.info(f"Created conversation with ID: {conversation_id}")
            
            # Step 2: Upload the document
            logger.info("Step 2: Uploading document")
            filename = os.path.basename(PDF_PATH)
            upload_response = await document_service.upload_document(
                file_data=pdf_data,
                filename=filename,
                user_id=test_user_id
            )
            document_id = str(upload_response.document_id)
            logger.info(f"Document uploaded with ID: {document_id}")
            
            # Wait for document processing to complete
            logger.info("Waiting for document processing to complete...")
            processing_completed = await wait_for_document_processing(document_repository, document_id)
            
            if not processing_completed:
                logger.error("Document processing did not complete successfully, aborting test")
                return None
            
            # Step 3: Add document to conversation
            logger.info("Step 3: Adding document to conversation")
            try:
                await langgraph_service.add_document_to_conversation(
                    conversation_id=conversation_id,
                    document_id=document_id
                )
                logger.info(f"Added document {document_id} to conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Error adding document to conversation: {str(e)}", exc_info=True)
                return None
            
            # Step 4: Send a message asking about the document
            logger.info("Step 4: Sending a message to query the document")
            query_message = "What were Mueller Industries' net sales in the first quarter? Please cite the document."
            
            # Add some explicit logging to debug the conversation state before processing
            logger.info(f"Sending query about document: {query_message}")
            
            # Process the message through LangGraph
            try:
                response = await langgraph_service.process_message(
                    conversation_id=conversation_id,
                    message_content=query_message
                )
                
                # Step 5: Check the response
                logger.info("\n=== Query Results ===")
                logger.info(f"Query: {query_message}")
                logger.info(f"Response: {response.get('message_content', 'No response')}")
                
                # Check if the response contains citations or references to the document
                response_text = response.get('message_content', '').lower()
                has_citations = any(marker in response_text for marker in 
                                ['according to the document', 'the document states', 
                                    'based on the document', 'mueller industries', 
                                    'earnings release', 'first quarter'])
                
                if has_citations:
                    logger.info("✅ SUCCESS: Response contains references to the document content")
                else:
                    logger.error("❌ FAILURE: Response does not contain references to the document")
                
                # Check if citations were generated
                citations = response.get('citations', [])
                if citations:
                    logger.info(f"✅ SUCCESS: Response includes {len(citations)} citations")
                    # Log the first few citations
                    for i, citation in enumerate(citations[:3]):
                        logger.info(f"Citation {i+1}: {citation}")
                else:
                    logger.warning("⚠️ No structured citations found in the response")
                
                return response
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                return None
            
        except Exception as e:
            logger.error(f"Error during test: {str(e)}", exc_info=True)
            return None

def main():
    """Run the test."""
    response = asyncio.run(test_document_visibility())
    
    # Final summary
    if response:
        logger.info("\n=== Test Summary ===")
        if response.get('message_content'):
            logger.info("Test completed - check logs for details")
            print("\nFinal Response from Claude:")
            print("-" * 50)
            print(response.get('message_content'))
            print("-" * 50)
        else:
            logger.error("Test completed but no response content was received")
    else:
        logger.error("Test failed - see error logs for details")

if __name__ == "__main__":
    main()
