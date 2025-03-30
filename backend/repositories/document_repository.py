import logging
import uuid
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
import json
import os

from models.database_models import Document, Citation, User, DocumentType, ProcessingStatusEnum
from models.document import ProcessedDocument, DocumentMetadata, DocumentUploadResponse, Citation as CitationSchema
from utils.storage import StorageService

logger = logging.getLogger(__name__)

class DocumentRepository:
    """Repository for document operations."""
    
    def __init__(self, db: AsyncSession, storage_service: Optional[StorageService] = None):
        """
        Initialize the document repository.
        
        Args:
            db: Database session
            storage_service: Optional storage service for file operations
        """
        self.db = db
        self.storage_service = storage_service or StorageService.get_storage_service()
    
    async def create_document(self, file_data: bytes, filename: str, user_id: str, mime_type: str) -> Document:
        """
        Create a new document record.
        
        Args:
            file_data: Raw bytes of the file
            filename: Name of the file
            user_id: ID of the user uploading the document
            mime_type: MIME type of the file
            
        Returns:
            Created document record
        """
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # Store the file
        file_path = await self.storage_service.save_file(
            file_data=file_data,
            file_id=f"{document_id}.pdf",
            content_type=mime_type
        )
        
        # Create document record
        document = Document(
            id=document_id,
            filename=filename,
            file_path=file_path,
            file_size=len(file_data),
            mime_type=mime_type,
            user_id=user_id,
            upload_timestamp=datetime.utcnow(),
            processing_status=ProcessingStatusEnum.PENDING
        )
        
        # Save to database
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document if found, None otherwise
        """
        # Ensure document_id is a string, not a list
        if isinstance(document_id, list):
            # If it's a list with items, use the first one
            if document_id:
                document_id = document_id[0]
            else:
                logger.error("Empty document_id list provided to get_document")
                return None
                
        try:
            result = await self.db.execute(
                select(Document).where(Document.id == document_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None
    
    async def get_document_content(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the content of a document by ID.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document content dictionary with raw text and file content if found, None otherwise
        """
        document = await self.get_document(document_id)
        if not document:
            logger.warning(f"Document {document_id} not found in database")
            return None
            
        try:
            # Get the file path
            file_path = f"{document_id}.pdf"
            logger.info(f"Retrieving document content using file path: {file_path}")
            
            # Get the raw PDF content from storage
            logger.info(f"Requesting file from storage service for document {document_id}")
            pdf_content = await self.storage_service.get_file(file_path)
            
            # Log PDF content retrieval success
            if pdf_content:
                pdf_size = len(pdf_content) if pdf_content else 0
                logger.info(f"Retrieved PDF content for document {document_id}: {pdf_size} bytes")
            
            # Prepare the response data
            content_data = {
                "content": pdf_content,
                "id": document_id,
                "filename": document.filename
            }
            
            # Add raw text if available - first try document.raw_text, then extracted_data
            logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} raw_text check: present={document.raw_text is not None}")
            logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} extracted_data check: present={document.extracted_data is not None}, type={type(document.extracted_data).__name__ if document.extracted_data else 'None'}")
            
            if document.extracted_data:
                if isinstance(document.extracted_data, dict):
                    logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} extracted_data keys: {list(document.extracted_data.keys())}")
                    if "raw_text" in document.extracted_data:
                        logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} has raw_text in extracted_data ({len(str(document.extracted_data['raw_text']))} chars)")
                    else:
                        logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} missing raw_text in extracted_data")
                else:
                    logger.info(f"[PDF-VISIBILITY-FIX] Document {document_id} extracted_data is not a dictionary")
            
            if document.raw_text:
                content_data["raw_text"] = document.raw_text
                logger.info(f"[PDF-VISIBILITY-FIX] Using document.raw_text for document {document_id}: {len(document.raw_text)} characters")
            elif document.extracted_data and isinstance(document.extracted_data, dict) and "raw_text" in document.extracted_data:
                # Extract raw text from extracted_data as fallback
                content_data["raw_text"] = document.extracted_data["raw_text"]
                logger.info(f"[PDF-VISIBILITY-FIX] Using extracted_data.raw_text for document {document_id}: {len(str(document.extracted_data['raw_text']))} characters")
            else:
                logger.warning(f"[PDF-VISIBILITY-FIX] No raw text available for document {document_id} - all extraction attempts failed")
                content_data["raw_text"] = "Document text not yet extracted"
            
            # Add extracted data if available
            if document.extracted_data:
                content_data["extracted_data"] = document.extracted_data
                logger.info(f"Extracted data available for document {document_id}: {list(document.extracted_data.keys()) if isinstance(document.extracted_data, dict) else 'not a dict'}")
            else:
                logger.warning(f"No extracted data available for document {document_id}")
                content_data["extracted_data"] = {}
            
            # Log content retrieval success
            logger.info(f"Successfully retrieved content for document {document_id}")
            
            return content_data
        except Exception as e:
            logger.error(f"Error retrieving document content for {document_id}: {str(e)}")
            
            # Try to return just the document fields even if file retrieval failed
            if document:
                logger.info(f"Returning partial content for document {document_id} (file retrieval failed)")
                return {
                    "id": document_id,
                    "filename": document.filename,
                    "raw_text": document.raw_text or "Document text not available",
                    "extracted_data": document.extracted_data or {}
                }
            
            return None
    
    async def list_documents(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Document]:
        """
        List documents for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of documents to return
            offset: Starting index
            
        Returns:
            List of documents
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.upload_timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def count_documents(self, user_id: str) -> int:
        """
        Count the number of documents for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of documents
        """
        result = await self.db.execute(
            select(func.count()).select_from(Document).where(Document.user_id == user_id)
        )
        return result.scalar()
    
    async def update_document(self, document_id: str, update_data: Dict[str, Any]) -> Optional[Document]:
        """
        Update a document.
        
        Args:
            document_id: ID of the document
            update_data: Dictionary of fields to update
            
        Returns:
            Updated document if found, None otherwise
        """
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_document(document_id)
    
    async def update_document_status(
        self, document_id: str, status: ProcessingStatusEnum, error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        Update a document's processing status.
        
        Args:
            document_id: ID of the document
            status: New processing status
            error_message: Optional error message if status is FAILED
            
        Returns:
            Updated document if found, None otherwise
        """
        update_data = {
            "processing_status": status,
            "processing_timestamp": datetime.utcnow()
        }
        
        if error_message:
            update_data["error_message"] = error_message
        
        return await self.update_document(document_id, update_data)
    
    async def update_document_content(
        self, 
        document_id: str, 
        document_type: Optional[DocumentType] = None, 
        periods: Optional[List[str]] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        raw_text: Optional[str] = None,
        confidence_score: Optional[float] = None,
        update_existing: bool = False
    ) -> Optional[Document]:
        """
        Update a document's content after processing.
        
        Args:
            document_id: ID of the document
            document_type: Type of financial document
            periods: List of time periods in the document
            extracted_data: Extracted structured data
            raw_text: Optional raw text of the document
            confidence_score: Confidence score of the extraction
            update_existing: If True, merge with existing extracted_data instead of replacing
            
        Returns:
            Updated document if found, None otherwise
        """
        # Build the update data with only provided fields
        update_data = {"extraction_timestamp": datetime.utcnow()}
        
        if document_type is not None:
            update_data["document_type"] = document_type
            
        if periods is not None:
            update_data["periods"] = periods
            
        if confidence_score is not None:
            update_data["confidence_score"] = confidence_score
            
        if raw_text is not None:
            update_data["raw_text"] = raw_text
        
        # Handle extracted_data separately if update_existing is True
        if extracted_data is not None:
            if update_existing:
                # Get current document to merge extracted_data
                current_doc = await self.get_document(document_id)
                if current_doc and current_doc.extracted_data:
                    # Deep merge the extracted data
                    merged_data = self._merge_dicts(current_doc.extracted_data, extracted_data)
                    update_data["extracted_data"] = merged_data
                else:
                    update_data["extracted_data"] = extracted_data
            else:
                update_data["extracted_data"] = extracted_data
        
        return await self.update_document(document_id, update_data)
    
    def _merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        Values from dict2 will override values in dict1 unless both are dictionaries,
        in which case they will be merged recursively.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary (takes precedence)
            
        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._merge_dicts(result[key], value)
            else:
                # Override or add the value
                result[key] = value
                
        return result
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            True if document was deleted, False otherwise
        """
        # Get document to get the file path
        document = await self.get_document(document_id)
        if not document:
            return False
        
        # Delete the file
        file_id = f"{document_id}.pdf"
        await self.storage_service.delete_file(file_id)
        
        # Delete from database
        await self.db.execute(
            delete(Document).where(Document.id == document_id)
        )
        await self.db.commit()
        
        return True
    
    async def add_citation(
        self, document_id: str, page: int, text: str, section: Optional[str] = None, bounding_box: Optional[Dict[str, Any]] = None
    ) -> Optional[Citation]:
        """
        Add a citation to a document.
        
        Args:
            document_id: ID of the document
            page: Page number
            text: Citation text
            section: Optional section name
            bounding_box: Optional bounding box coordinates
            
        Returns:
            Created citation if document found, None otherwise
        """
        # Check if document exists
        document = await self.get_document(document_id)
        if not document:
            return None
        
        # Create citation
        citation = Citation(
            id=str(uuid.uuid4()),
            document_id=document_id,
            page=page,
            text=text,
            section=section,
            bounding_box=bounding_box
        )
        
        # Save to database
        self.db.add(citation)
        await self.db.commit()
        await self.db.refresh(citation)
        
        return citation
    
    async def get_citation(self, citation_id: str) -> Optional[Citation]:
        """
        Get a citation by ID.
        
        Args:
            citation_id: ID of the citation
            
        Returns:
            Citation if found, None otherwise
        """
        result = await self.db.execute(
            select(Citation).where(Citation.id == citation_id)
        )
        return result.scalars().first()
    
    async def update_citation(self, citation_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a citation's metadata.
        
        Args:
            citation_id: ID of the citation
            metadata: New metadata dictionary
            
        Returns:
            True if updated, False otherwise
        """
        # Get the citation
        citation = await self.get_citation(citation_id)
        if not citation:
            return False
        
        # Update metadata if provided
        if metadata is not None:
            citation.metadata = metadata
        
        # Save changes
        await self.db.commit()
        
        return True
    
    async def get_document_citations(self, document_id: str) -> List[Citation]:
        """
        Get citations for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of citations
        """
        result = await self.db.execute(
            select(Citation).where(Citation.document_id == document_id)
        )
        return result.scalars().all()
    
    # Methods to convert between database models and API schemas
    
    def document_to_api_schema(self, document: Document) -> ProcessedDocument:
        """Convert a database document model to an API schema."""
        # Avoid lazy loading by not accessing citations directly
        
        # Create metadata
        metadata = DocumentMetadata(
            id=document.id,
            filename=document.filename,
            upload_timestamp=document.upload_timestamp,
            file_size=document.file_size,
            mime_type=document.mime_type,
            user_id=document.user_id,
            citation_links=[]  # Initialize with empty list to avoid lazy loading
        )
        
        # Create processed document
        processed_document = ProcessedDocument(
            metadata=metadata,
            content_type=document.document_type.value if document.document_type else "other",
            extraction_timestamp=document.extraction_timestamp or document.upload_timestamp,
            periods=document.periods or [],
            extracted_data=document.extracted_data or {},
            citations=[],  # Initialize with empty list to avoid lazy loading
            confidence_score=document.confidence_score or 0.0,
            processing_status=document.processing_status.value if document.processing_status else "pending",
            error_message=document.error_message
        )
        
        return processed_document
    
    def document_to_metadata_schema(self, document: Document) -> DocumentMetadata:
        """Convert a database document model to a metadata schema."""
        # Avoid lazy loading by not accessing citations directly
        metadata = DocumentMetadata(
            id=document.id,
            filename=document.filename,
            upload_timestamp=document.upload_timestamp,
            file_size=document.file_size,
            mime_type=document.mime_type,
            user_id=document.user_id,
            citation_links=[]  # Initialize with empty list to avoid lazy loading
        )
        
        return metadata
    
    def document_to_upload_response(self, document: Document) -> DocumentUploadResponse:
        """Convert a database document model to an upload response schema."""
        return DocumentUploadResponse(
            document_id=document.id,
            filename=document.filename,
            status=document.processing_status.value if document.processing_status else "pending",
            message=f"Document uploaded and processing has {'started' if document.processing_status == ProcessingStatusEnum.PENDING else 'completed'}"
        )
    
    def citation_to_api_schema(self, citation: Citation) -> CitationSchema:
        """Convert a database Citation to an API CitationSchema."""
        return CitationSchema(
            id=str(citation.id),
            text=citation.text,
            documentId=str(citation.document_id),
            page=citation.page,
            highlightId=citation.highlight_id,
            rects=citation.bounding_box if citation.bounding_box else [],
            messageId=str(citation.message_id) if citation.message_id else None,
            analysisId=str(citation.analysis_id) if citation.analysis_id else None,
        )
        
    def get_document_file_path(self, document_id: str) -> str:
        """
        Get the physical file path for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Absolute path to the document file
        """
        # The storage service uses the document ID with a .pdf extension as the file ID
        file_id = f"{document_id}.pdf"
        return self.storage_service.get_file_path(file_id)
    
    async def get_document_binary(self, document_id: str) -> Optional[bytes]:
        """
        Get the binary data for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Binary data of the document file if available, None otherwise
        """
        try:
            # First check if we have the document in the database
            document = await self.get_document(document_id)
            if not document:
                return None
            
            # If we have binary_data stored in the database, return it
            if hasattr(document, 'binary_data') and document.binary_data:
                return document.binary_data
            
            # If we don't have binary data in the DB, try to read from file
            file_path = self.get_document_file_path(document_id)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            
            # No binary data found
            return None
        except Exception as e:
            logging.error(f"Error getting document binary data: {str(e)}", exc_info=True)
            return None