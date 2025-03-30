import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, BinaryIO, Any
from pathlib import Path
import asyncio

from models.document import (
    ProcessedDocument, 
    DocumentMetadata, 
    ProcessingStatus,
    DocumentContentType,
    Citation as CitationSchema,
    DocumentUploadResponse
)
from models.database_models import DocumentType, ProcessingStatusEnum, Document, Citation
from pdf_processing.claude_service import ClaudeService
from pdf_processing.enhanced_pdf_service import EnhancedPDFService
from repositories.document_repository import DocumentRepository


logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        """
        Initialize the document service.
        
        Args:
            document_repository: Repository for document operations
        """
        self.document_repository = document_repository
        self.claude_service = ClaudeService()
        self.enhanced_pdf_service = EnhancedPDFService()
        
    async def upload_document(self, file_data: bytes, filename: str, user_id: str) -> DocumentUploadResponse:
        """
        Upload and process a document.
        
        Args:
            file_data: Raw bytes of the PDF file
            filename: Name of the file
            user_id: ID of the user uploading the document
            
        Returns:
            Document upload response with status and document ID
        """
        try:
            # Create the document record
            document = await self.document_repository.create_document(
                file_data=file_data,
                filename=filename,
                user_id=user_id,
                mime_type="application/pdf"
            )
            
            # Start background processing
            asyncio.create_task(self._process_document(document.id, file_data, filename))
            
            # Return upload response
            return self.document_repository.document_to_upload_response(document)
        
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}", exc_info=True)
            raise
    
    async def _process_document(self, document_id: str, pdf_data: bytes, filename: str):
        """
        Process a document with Claude API for PDF processing and citation extraction.
        
        Args:
            document_id: ID of the document
            pdf_data: Raw bytes of the PDF file
            filename: Name of the file
        """
        try:
            # Update status to processing
            await self.document_repository.update_document_status(document_id, ProcessingStatusEnum.PROCESSING)
            logger.info(f"Starting processing of document {document_id} ({filename}) with Claude API")
            
            # Process with Claude service directly for PDF processing and citation extraction
            try:
                logger.info(f"Processing document {document_id} with Claude service")
                processed_document, citations = await self.claude_service.process_pdf(pdf_data, filename)
                logger.info(f"Successfully processed document {document_id} with Claude service")
                logger.info(f"Extracted {len(citations)} citations from document")
            except Exception as e:
                logger.error(f"Error using Claude service: {str(e)}", exc_info=True)
                
                # Attempt to extract raw text even if Claude processing fails
                raw_text = ""
                try:
                    import io
                    from PyPDF2 import PdfReader
                    
                    pdf_file = io.BytesIO(pdf_data)
                    pdf_reader = PdfReader(pdf_file)
                    
                    # Extract text from each page
                    page_texts = []
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(f"--- Page {page_num+1} ---\n{page_text}")
                    
                    raw_text = "\n\n".join(page_texts)
                    logger.info(f"Extracted {len(raw_text)} characters of raw text as fallback for document {document_id}")
                    
                    # Store the extracted text in database even if processing failed
                    await self.document_repository.update_document_content(
                        document_id=document_id,
                        document_type=DocumentType.OTHER,
                        extracted_data={"raw_text": raw_text},
                        raw_text=raw_text,
                        confidence_score=0.0
                    )
                    
                except Exception as extract_error:
                    logger.error(f"Failed to extract fallback text: {extract_error}", exc_info=True)
                
                # Update status to failed with error message
                await self.document_repository.update_document_status(
                    document_id=document_id,
                    status=ProcessingStatusEnum.FAILED,
                    error_message=f"Claude API processing error: {str(e)}"
                )
                return
            
            # Update document content
            document_type = DocumentType[processed_document.content_type.upper()] if processed_document.content_type else DocumentType.OTHER
            
            # Extract raw text from processed document
            raw_text = ""
            if processed_document.extracted_data and "raw_text" in processed_document.extracted_data:
                raw_text = processed_document.extracted_data["raw_text"]
                logger.info(f"Found {len(raw_text)} characters of raw text in processed document")
                logger.info(f"Sample text: {raw_text[:200]}...")
            
            # Ensure we have some raw text
            if not raw_text or len(raw_text.strip()) == 0:
                logger.warning(f"No raw text found in processed document for {document_id} - attempting extraction")
                try:
                    import io
                    from PyPDF2 import PdfReader
                    
                    pdf_file = io.BytesIO(pdf_data)
                    pdf_reader = PdfReader(pdf_file)
                    
                    # Extract text from each page
                    page_texts = []
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(f"--- Page {page_num+1} ---\n{page_text}")
                    
                    raw_text = "\n\n".join(page_texts)
                    logger.info(f"Successfully extracted {len(raw_text)} characters as fallback raw text")
                    
                    # Update the extracted data with the raw text
                    if not processed_document.extracted_data:
                        processed_document.extracted_data = {}
                    processed_document.extracted_data["raw_text"] = raw_text
                    
                except Exception as extract_error:
                    logger.error(f"Failed to extract fallback text: {extract_error}", exc_info=True)
                    raw_text = f"Failed to extract text content from {filename}. PDF may contain images or be protected."
            
            # Update document with extracted content
            logger.info(f"Updating document {document_id} content in database")
            await self.document_repository.update_document_content(
                document_id=document_id,
                document_type=document_type,
                periods=processed_document.periods,
                extracted_data=processed_document.extracted_data,
                raw_text=raw_text,
                confidence_score=processed_document.confidence_score
            )
            
            # Log document processing details for debugging
            logger.info(f"Document {document_id} processed. Status: COMPLETED, Has raw_text: {bool(raw_text)}, Raw text length: {len(raw_text)}, Extracted data keys: {list(processed_document.extracted_data.keys()) if processed_document.extracted_data else 'None'}")
            
            # Add citations to the database
            added_citations = []
            logger.info(f"Storing {len(citations)} citations for document {document_id}")
            for citation in citations:
                # Create bounding box data if not present
                bounding_box = citation.bounding_box or {
                    "top": 0,
                    "left": 0,
                    "width": 0,
                    "height": 0
                }
                
                db_citation = await self.document_repository.add_citation(
                    document_id=document_id,
                    page=citation.page,
                    text=citation.text,
                    section=citation.section,
                    bounding_box=bounding_box
                )
                if db_citation:
                    added_citations.append(db_citation)
            
            # Link citations to financial insights if available
            if "financial_data" in processed_document.extracted_data and "insights" in processed_document.extracted_data["financial_data"]:
                insights = processed_document.extracted_data["financial_data"]["insights"]
                
                # Create a map of citation IDs to database citation IDs
                citation_id_map = {}
                for i, citation in enumerate(citations):
                    citation_id = f"citation_{i}"
                    if i < len(added_citations):
                        citation_id_map[citation_id] = str(added_citations[i].id)
                
                # Update the extracted data with database citation IDs
                for insight_id, insight_data in insights.items():
                    if "citations" in insight_data:
                        for i, citation_ref in enumerate(insight_data["citations"]):
                            if "citation_id" in citation_ref and citation_ref["citation_id"] in citation_id_map:
                                insight_data["citations"][i]["db_citation_id"] = citation_id_map[citation_ref["citation_id"]]
                
                # Update the document with the updated insights
                await self.document_repository.update_document_content(
                    document_id=document_id,
                    extracted_data=processed_document.extracted_data,
                    update_existing=True
                )
            
            # Update status to completed
            await self.document_repository.update_document_status(document_id, ProcessingStatusEnum.COMPLETED)
            
            logger.info(f"Document {document_id} processing completed with {len(added_citations)} citations extracted")
                
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
            
            # Update status to failed
            await self.document_repository.update_document_status(
                document_id=document_id,
                status=ProcessingStatusEnum.FAILED,
                error_message=str(e)
            )
    
    async def get_document_financial_data(self, document_id: str) -> Dict[str, Any]:
        """
        Get content from a document that can be used for financial analysis.
        Now more flexible - returns any available content rather than requiring 
        specific financial_data structure.
        
        Args:
            document_id: ID of the document
                
        Returns:
            Dictionary containing document content suitable for analysis
        """
        document = await self.document_repository.get_document(document_id)
        
        if not document:
            logger.warning(f"Document {document_id} not found")
            return {"error": "Document not found"}
        
        result = {}
        
        # Add financial_data if it exists
        if document.extracted_data and isinstance(document.extracted_data, dict) and "financial_data" in document.extracted_data:
            result["financial_data"] = document.extracted_data["financial_data"]
        
        # Add raw_text if available
        if document.raw_text:
            result["raw_text"] = document.raw_text
            logger.info(f"Found {len(document.raw_text)} characters of raw text in document {document_id}")
        elif document.extracted_data and isinstance(document.extracted_data, dict) and "raw_text" in document.extracted_data:
            result["raw_text"] = document.extracted_data["raw_text"]
            logger.info(f"Found {len(document.extracted_data['raw_text'])} characters of raw text in extracted_data")
        
        # If we have any content, consider it valid
        if result:
            result["has_content"] = True
            return result
        
        # Return empty structure if no content found
        logger.warning(f"No analyzable content found in document {document_id}")
        return {
            "has_content": False,
            "raw_text": f"No content extracted from document {document_id}. The document may be empty or contain only images.",
            "revenue": {},
            "expenses": {},
            "profit": {},
            "assets": {},
            "liabilities": {},
            "equity": {}
        }
    
    async def get_document_content(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the full content of a document including extracted data.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary containing document content if found, None otherwise
        """
        document = await self.document_repository.get_document(document_id)
        
        if not document:
            return None
        
        # Get citations
        citations = await self.document_repository.get_document_citations(document_id)
        citation_schemas = [self.document_repository.citation_to_api_schema(citation) for citation in citations]
        
        return {
            "metadata": self.document_repository.document_to_metadata_schema(document).model_dump(),
            "content_type": document.document_type.value if document.document_type else "other",
            "periods": document.periods or [],
            "extracted_data": document.extracted_data or {},
            "citations": [citation.model_dump() for citation in citation_schemas],
            "confidence_score": document.confidence_score or 0.0
        }
        
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID. This is an alias for get_document_content for backwards compatibility.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary containing document content if found, None otherwise
        """
        # This method should match what's being expected by the calling code
        return await self.get_document_content(document_id)

    async def extract_structured_financial_data(self, document_id: str, text: str = None) -> Dict[str, Any]:
        """
        Extract structured financial data from document text using Claude and update the document.
        
        Args:
            document_id: ID of the document to update
            text: Raw document text to analyze. If None, will be retrieved from the document.
            
        Returns:
            Dictionary with extraction results
        """
        try:
            logger.info(f"Extracting structured financial data for document {document_id}")
            
            # Get document from database to retrieve raw PDF data if available
            document = await self.document_repository.get_document(document_id)
            if not document:
                return {"error": f"Document {document_id} not found"}
            
            # If text not provided, use the one from the document
            if text is None and document.raw_text:
                text = document.raw_text
                logger.info(f"Using document's raw text ({len(text)} chars) for financial data extraction")
            elif text is None:
                return {"error": "No text available for document analysis"}
            
            # Get raw PDF data from storage if available
            pdf_data = None
            filename = document.filename if document else f"document_{document_id}.pdf"
            
            try:
                # Try to get the raw PDF data from storage
                pdf_data = await self.document_repository.get_document_binary(document_id)
                if pdf_data:
                    logger.info(f"Retrieved raw PDF data ({len(pdf_data)} bytes) for financial data extraction")
            except Exception as e:
                logger.warning(f"Could not retrieve PDF binary data: {str(e)}")
                # Continue with text-only extraction if PDF data is not available
            
            # Call Claude service to extract structured data - passing both text and PDF data
            structured_data = await self.claude_service.extract_structured_financial_data(
                text=text,
                pdf_data=pdf_data,
                filename=filename
            )
            
            # If error in extraction, return it
            if structured_data.get("error"):
                logger.error(f"Error extracting structured data: {structured_data['error']}")
                return structured_data
            
            # Prepare financial data structure
            financial_data = {}
            
            # Copy metrics if available
            if "metrics" in structured_data and structured_data["metrics"]:
                financial_data["metrics"] = structured_data["metrics"]
                
            # Copy ratios if available
            if "ratios" in structured_data and structured_data["ratios"]:
                financial_data["ratios"] = structured_data["ratios"]
                
            # Copy insights if available
            if "key_insights" in structured_data and structured_data["key_insights"]:
                financial_data["insights"] = structured_data["key_insights"]
            
            # Get periods from structured data
            periods = structured_data.get("periods", [])
            
            # Update the document with new financial data
            logger.info(f"Updating document {document_id} with structured financial data")
            
            # Create a merged extracted_data object that keeps existing data
            extracted_data = {
                "financial_data": financial_data
            }
            
            # Update document content
            await self.document_repository.update_document_content(
                document_id=document_id,
                document_type=DocumentType.FINANCIAL_REPORT,  # Force update to financial report type
                periods=periods if periods else None,
                extracted_data=extracted_data,
                update_existing=True  # Merge with existing data rather than replacing
            )
            
            # Return success with extracted data
            return {
                "document_id": document_id,
                "metrics_count": len(financial_data.get("metrics", [])),
                "ratios_count": len(financial_data.get("ratios", [])),
                "insights_count": len(financial_data.get("insights", [])),
                "periods": periods
            }
            
        except Exception as e:
            logger.exception(f"Error in structured financial data extraction: {e}")
            return {"error": str(e)}