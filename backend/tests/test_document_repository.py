import asyncio
import pytest
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.database_models import Document, ProcessingStatusEnum
from repositories.document_repository import DocumentRepository
from utils.database import get_db
from utils.storage import StorageService

# Test data
TEST_FILE_DATA = b'%PDF-1.5\n%Test PDF file for unit testing'
TEST_FILENAME = 'test_document.pdf'
TEST_USER_ID = 'default-user'
TEST_MIME_TYPE = 'application/pdf'

class TestDocumentRepository:
    """Test cases for DocumentRepository."""
    
    @pytest.mark.asyncio
    async def test_create_document(self):
        """Test creating a document."""
        # Get a database session
        session_generator = get_db()
        db = await session_generator.__anext__()
        
        try:
            # Create repository
            repository = DocumentRepository(db)
            
            # Create document
            document = await repository.create_document(
                file_data=TEST_FILE_DATA,
                filename=TEST_FILENAME,
                user_id=TEST_USER_ID,
                mime_type=TEST_MIME_TYPE
            )
            
            # Verify document was created
            assert document is not None
            assert document.id is not None
            assert document.filename == TEST_FILENAME
            assert document.user_id == TEST_USER_ID
            assert document.processing_status == ProcessingStatusEnum.PENDING
            
            # Cleanup - delete the document and file
            await repository.delete_document(document.id)
            
        finally:
            # Close the session
            await db.close()
    
    @pytest.mark.asyncio
    async def test_get_document(self):
        """Test retrieving a document."""
        # Get a database session
        session_generator = get_db()
        db = await session_generator.__anext__()
        
        try:
            # Create repository
            repository = DocumentRepository(db)
            
            # Create document
            document = await repository.create_document(
                file_data=TEST_FILE_DATA,
                filename=TEST_FILENAME,
                user_id=TEST_USER_ID,
                mime_type=TEST_MIME_TYPE
            )
            
            # Get the document
            retrieved_document = await repository.get_document(document.id)
            
            # Verify document was retrieved
            assert retrieved_document is not None
            assert retrieved_document.id == document.id
            assert retrieved_document.filename == TEST_FILENAME
            
            # Cleanup - delete the document and file
            await repository.delete_document(document.id)
            
        finally:
            # Close the session
            await db.close()
    
    @pytest.mark.asyncio
    async def test_list_documents(self):
        """Test listing documents for a user."""
        # Get a database session
        session_generator = get_db()
        db = await session_generator.__anext__()
        
        try:
            # Create repository
            repository = DocumentRepository(db)
            
            # Create document
            document = await repository.create_document(
                file_data=TEST_FILE_DATA,
                filename=TEST_FILENAME,
                user_id=TEST_USER_ID,
                mime_type=TEST_MIME_TYPE
            )
            
            # List documents
            documents = await repository.list_documents(TEST_USER_ID, 10, 0)
            
            # Verify documents were listed
            assert len(documents) > 0
            assert any(d.id == document.id for d in documents)
            
            # Cleanup - delete the document and file
            await repository.delete_document(document.id)
            
        finally:
            # Close the session
            await db.close()
    
    @pytest.mark.asyncio
    async def test_update_document(self):
        """Test updating a document."""
        # Get a database session
        session_generator = get_db()
        db = await session_generator.__anext__()
        
        try:
            # Create repository
            repository = DocumentRepository(db)
            
            # Create document
            document = await repository.create_document(
                file_data=TEST_FILE_DATA,
                filename=TEST_FILENAME,
                user_id=TEST_USER_ID,
                mime_type=TEST_MIME_TYPE
            )
            
            # Update document
            updated_document = await repository.update_document(
                document_id=document.id,
                update_data={"filename": "updated_filename.pdf"}
            )
            
            # Verify document was updated
            assert updated_document is not None
            assert updated_document.id == document.id
            assert updated_document.filename == "updated_filename.pdf"
            
            # Cleanup - delete the document and file
            await repository.delete_document(document.id)
            
        finally:
            # Close the session
            await db.close()
    
    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test deleting a document."""
        # Get a database session
        session_generator = get_db()
        db = await session_generator.__anext__()
        
        try:
            # Create repository
            repository = DocumentRepository(db)
            
            # Create document
            document = await repository.create_document(
                file_data=TEST_FILE_DATA,
                filename=TEST_FILENAME,
                user_id=TEST_USER_ID,
                mime_type=TEST_MIME_TYPE
            )
            
            # Delete document
            success = await repository.delete_document(document.id)
            
            # Verify document was deleted
            assert success is True
            
            # Verify document no longer exists
            deleted_document = await repository.get_document(document.id)
            assert deleted_document is None
            
        finally:
            # Close the session
            await db.close() 