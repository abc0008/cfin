#!/usr/bin/env python3
"""
Simple test script to verify the document API endpoints.
"""

import asyncio
import logging
from models.document import DocumentUploadResponse, ProcessedDocument, DocumentMetadata
from repositories.document_repository import DocumentRepository
from utils.database import SessionLocal
from models.database_models import User, Document, ProcessingStatusEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_document_repository():
    """Test the document repository."""
    async with SessionLocal() as session:
        # Create a document repository
        document_repository = DocumentRepository(session)
        
        # List documents
        user_id = "default-user"
        documents = await document_repository.list_documents(user_id)
        logger.info(f"Found {len(documents)} documents for user {user_id}")
        
        # Print document details
        for doc in documents:
            logger.info(f"Document ID: {doc.id}")
            logger.info(f"Filename: {doc.filename}")
            logger.info(f"Status: {doc.processing_status}")
            logger.info(f"Type: {doc.document_type}")
            logger.info("---")

def main():
    """Run the test."""
    asyncio.run(test_document_repository())

if __name__ == "__main__":
    main() 