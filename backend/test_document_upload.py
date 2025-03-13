#!/usr/bin/env python3
"""
Simple test script to test uploading a document.
"""

import asyncio
import logging
import os
from models.document import DocumentUploadResponse
from repositories.document_repository import DocumentRepository
from pdf_processing.document_service import DocumentService
from utils.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_document_upload():
    """Test uploading a document."""
    # Check if test PDF exists
    test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "sample.pdf")
    if not os.path.exists(test_pdf_path):
        logger.error(f"Test PDF not found at {test_pdf_path}")
        # Create test_data directory if it doesn't exist
        os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)
        # Create a simple test PDF
        with open(test_pdf_path, "wb") as f:
            # Write a simple PDF header
            f.write(b"%PDF-1.4\n")
            f.write(b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n")
            f.write(b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n")
            f.write(b"3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\n")
            f.write(b"xref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n")
            f.write(b"trailer\n<</Size 4/Root 1 0 R>>\nstartxref\n183\n%%EOF\n")
        logger.info(f"Created test PDF at {test_pdf_path}")
    
    # Read the test PDF
    with open(test_pdf_path, "rb") as f:
        pdf_data = f.read()
    
    async with SessionLocal() as session:
        # Create a document repository
        document_repository = DocumentRepository(session)
        
        # Create a document service
        document_service = DocumentService(document_repository)
        
        # Upload the document
        filename = "sample.pdf"
        user_id = "default-user"
        response = await document_service.upload_document(pdf_data, filename, user_id)
        
        logger.info(f"Document uploaded with ID: {response.document_id}")
        logger.info(f"Status: {response.status}")
        
        # Wait for processing to complete
        logger.info("Waiting for document processing to complete...")
        await asyncio.sleep(2)
        
        # Get the document
        document = await document_repository.get_document(str(response.document_id))
        if document:
            logger.info(f"Document status: {document.processing_status}")
            logger.info(f"Document type: {document.document_type}")
        else:
            logger.error("Document not found")

def main():
    """Run the test."""
    asyncio.run(test_document_upload())

if __name__ == "__main__":
    main() 