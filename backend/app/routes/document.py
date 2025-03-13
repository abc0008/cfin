from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
import logging

from models.document import DocumentUploadResponse, ProcessedDocument, DocumentMetadata, Citation
from models.api_models import RetryExtractionRequest
from repositories.document_repository import DocumentRepository
from pdf_processing.document_service import DocumentService
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import get_document_service, get_document_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Dependency to get the document repository
async def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepository(db)

# Dependency to get the document service
async def get_document_service(db: AsyncSession = Depends(get_db)):
    document_repository = DocumentRepository(db)
    return DocumentService(document_repository)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form("default-user"),  # In a real app, this would come from auth
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Upload a financial document for processing, including citation metadata extraction.
    """
    # Validate file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Validate file size (10MB max)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size must be less than 10MB")
    
    try:
        # Read the file
        file_data = await file.read()
        
        # Upload and process the document
        response = await document_service.upload_document(file_data, file.filename, user_id)
        
        return response
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/count")
async def count_documents(
    user_id: str = "default-user",  # In a real app, this would come from auth
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Count the number of documents for the current user.
    """
    count = await document_repository.count_documents(user_id)
    return {"count": count}

@router.get("", response_model=List[DocumentMetadata])
async def list_documents(
    user_id: str = "default-user",  # In a real app, this would come from auth
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    List all documents for the current user.
    """
    offset = (page - 1) * page_size
    documents = await document_repository.list_documents(user_id, page_size, offset)
    
    # Convert to API schema
    return [document_repository.document_to_metadata_schema(doc) for doc in documents]

@router.get("/{document_id}", response_model=ProcessedDocument)
async def get_document(
    document_id: str,
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Retrieve document metadata, processed content, and citation highlights.
    """
    document = await document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document_repository.document_to_api_schema(document)

@router.get("/{document_id}/citations", response_model=List[Citation])
async def get_document_citations(
    document_id: str,
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Get all citations for a document.
    """
    document = await document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    citations = await document_repository.get_document_citations(document_id)
    
    # Convert to API schema
    return [document_repository.citation_to_api_schema(citation) for citation in citations]

@router.get("/{document_id}/citations/{citation_id}", response_model=Citation)
async def get_citation(
    document_id: str,
    citation_id: str,
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Get a specific citation.
    """
    # Check if document exists
    document = await document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get the citation
    citation = await document_repository.get_citation(citation_id)
    if not citation or citation.document_id != document_id:
        raise HTTPException(status_code=404, detail="Citation not found")
    
    return document_repository.citation_to_api_schema(citation)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Delete a document.
    """
    document = await document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    success = await document_repository.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    return {"message": f"Document {document_id} deleted successfully"}

@router.post("/{document_id}/retry-extraction", response_model=Dict[str, Any])
async def retry_extraction(
    document_id: str = Path(..., description="Document ID to retry extraction for"),
    request: RetryExtractionRequest = Body(..., description="Extraction parameters"),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Retry extraction of structured data from a document.
    
    Args:
        document_id: ID of the document to process
        request: Parameters for extraction
        document_service: Document service dependency
        
    Returns:
        Status of the extraction
    """
    try:
        logger.info(f"Retrying extraction for document {document_id}, type: {request.extraction_type}")
        
        # Verify the document exists
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        # Get raw text from document
        raw_text = None
        if document.extracted_data and "raw_text" in document.extracted_data:
            raw_text = document.extracted_data["raw_text"]
        
        if not raw_text:
            return {"success": False, "error": "Document has no extracted text to process"}
        
        # Call the specific extraction method based on extraction_type
        if request.extraction_type == "structured_financial_data":
            # Call the structured financial data extraction
            result = await document_service.extract_structured_financial_data(document_id, raw_text)
            return {"success": True, "extraction_type": request.extraction_type, "result": result}
        else:
            return {"success": False, "error": f"Unsupported extraction type: {request.extraction_type}"}
    
    except Exception as e:
        logger.exception(f"Error in retry extraction: {e}")
        return {"success": False, "error": str(e)}