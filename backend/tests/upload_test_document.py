import asyncio
import logging
import sys
import os
import dotenv
import uuid
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
logger = logging.getLogger("upload_test_document")

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.document_repository import DocumentRepository
from utils.database import SessionLocal

async def upload_test_document(file_path: str, user_id: str = "test_user"):
    """
    Upload a test document to the database for testing purposes.
    
    Args:
        file_path: Path to the PDF file to upload
        user_id: User ID to associate with the document
    
    Returns:
        Document ID if successful, None otherwise
    """
    logger.info(f"Uploading test document from {file_path}")
    
    try:
        # Read file data
        with open(file_path, "rb") as file:
            file_data = file.read()
            
        # Get filename
        filename = os.path.basename(file_path)
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Create document repository
            document_repo = DocumentRepository(db)
            
            # Create document
            document = await document_repo.create_document(
                file_data=file_data,
                filename=filename,
                user_id=user_id,
                mime_type="application/pdf"
            )
            
            document_id = str(document.id)
            logger.info(f"Successfully uploaded document with ID: {document_id}")
            
            return document_id
        finally:
            # Close the database session
            await db.close()
    except Exception as e:
        logger.error(f"Error uploading test document: {str(e)}", exc_info=True)
        return None

async def main():
    """
    Main entry point for uploading test documents.
    """
    # Look for PDF files in the 'samples' directory
    samples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
    
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir)
        logger.warning(f"Created samples directory at {samples_dir}")
        logger.info("Please place some PDF files in this directory and run this script again.")
        return
    
    # Find PDF files in the samples directory
    pdf_files = [f for f in os.listdir(samples_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning("No PDF files found in the samples directory.")
        logger.info("Please place some PDF files in the samples directory and run this script again.")
        return
    
    # Upload each PDF file
    document_ids = []
    for pdf_file in pdf_files:
        file_path = os.path.join(samples_dir, pdf_file)
        document_id = await upload_test_document(file_path)
        if document_id:
            document_ids.append(document_id)
    
    logger.info(f"Uploaded {len(document_ids)} test documents: {document_ids}")

if __name__ == "__main__":
    asyncio.run(main())
