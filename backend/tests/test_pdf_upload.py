import asyncio
import logging
import sys
import os
import uuid
import dotenv
from typing import Optional

# Load environment variables from .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_pdf_upload")

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if required environment variables are set
required_vars = ['ANTHROPIC_API_KEY', 'CLAUDE_MODEL']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.info(f"Please ensure the following variables are set in your .env file: {', '.join(required_vars)}")
    sys.exit(1)

# Import after environment variables are loaded
from pdf_processing.langgraph_service import LangGraphService
from repositories.document_repository import DocumentRepository
from repositories.conversation_repository import ConversationRepository
from utils.database import SessionLocal

async def test_document_upload_and_processing():
    """
    Test document upload, chunking, and processing with citation handling.
    This tests the memory management for large PDFs.
    """
    logger.info("Starting document upload and processing test")
    
    # Initialize LangGraph service
    service = LangGraphService()
    
    # Create a test conversation ID
    conversation_id = str(uuid.uuid4())
    user_id = "test_user"
    
    logger.info(f"Testing with conversation ID: {conversation_id}")
    
    try:
        # Get some document IDs from the database to test with
        doc_ids = []
        
        # Create database session directly
        db = SessionLocal()
        
        try:
            document_repo = DocumentRepository(db)
            conversation_repo = ConversationRepository(db)
            
            # Get a few documents to test with (ideally at least one large one)
            documents = await document_repo.list_documents(user_id=user_id, limit=5)
            if documents:
                doc_ids = [str(doc.id) for doc in documents]
                logger.info(f"Retrieved {len(doc_ids)} documents for testing: {doc_ids}")
            else:
                logger.warning("No documents found in the database for testing")
                return
                
            # Create a test conversation
            conversation = await conversation_repo.create_conversation(
                title="Test Memory Management Conversation",
                user_id=user_id
            )
            conversation_id = str(conversation.id)
            logger.info(f"Created test conversation: {conversation_id}")
            
            # Add documents to the conversation in the database
            for doc_id in doc_ids:
                await conversation_repo.add_document_to_conversation(
                    conversation_id=conversation_id, 
                    document_id=doc_id
                )
            logger.info(f"Added {len(doc_ids)} documents to conversation in database")
        finally:
            # Close the database session
            await db.close()
        
        # Initialize the conversation in the LangGraphService
        result = await service.initialize_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            document_ids=doc_ids,
            conversation_title="Test Memory Management"
        )
        
        if result and result.get("status") == "initialized":
            logger.info(f"Successfully initialized conversation: {result}")
        else:
            logger.error(f"Failed to initialize conversation: {result}")
            return
            
        # Test adding each document using the enhanced memory management
        for doc_id in doc_ids:
            logger.info(f"Testing memory managed upload for document: {doc_id}")
            
            # Add document with enhanced chunking
            result = await service.add_document_to_conversation(
                conversation_id=conversation_id,
                document_id=doc_id,
                user_id=user_id
            )
            
            if result.get("status") == "success":
                logger.info(f"Successfully added document with chunking: {doc_id}")
            else:
                logger.error(f"Failed to add document: {result}")
        
        # Test processing a message with the loaded documents
        logger.info("Testing message processing with loaded documents")
        message_result = await service.process_message(
            conversation_id=conversation_id,
            message_text="Can you analyze the financial data in these documents and highlight key insights?"
        )
        
        if message_result.get("status") == "success":
            logger.info("Message processed successfully!")
            response = message_result.get("response", "")
            citations = message_result.get("citations", [])
            logger.info(f"Response received: {response[:100]}... (truncated)")
            logger.info(f"Citations received: {len(citations)} citations")
        else:
            logger.error(f"Failed to process message: {message_result}")
            
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_document_upload_and_processing())
