import os
import base64
import asyncio
import json
import re
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage
import string
from datetime import datetime
import contextlib

from models.document import ProcessedDocument, Citation as DocumentCitation, DocumentContentType, DocumentMetadata, ProcessingStatus
from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation, ContentBlockLocationCitation
from pdf_processing.langchain_service import LangChainService

# Set up logger
logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def get_anthropic_client():
    """
    Context manager to get an Anthropic client.
    This function helps avoid circular imports between modules.
    
    Yields:
        AsyncAnthropic: An Anthropic API client
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    client = AsyncAnthropic(api_key=api_key)
    try:
        yield client
    finally:
        # No need to close the client explicitly as AsyncAnthropic handles this
        pass

# Conditionally import LangGraphService
try:
    from pdf_processing.langgraph_service import LangGraphService
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph import failed: {e}. LangGraph features will be disabled.")
except Exception as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph unexpected error: {e}. LangGraph features will be disabled.")


class ClaudeService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API service with API key from parameter or environment variable.
        Configures AsyncAnthropic client with the API key.
        
        Args:
            api_key: Optional API key to use instead of environment variable
        """
        # Try to get API key from parameter first, then environment
        self.api_key = api_key
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            logger.info("Using ANTHROPIC_API_KEY from environment variables")
        
        if not self.api_key:
            logger.warning("Missing ANTHROPIC_API_KEY environment variable or API key parameter")
            self.client = None
            return
        
        # Mask API key for logging (show first 8 chars and last 4)
        if len(self.api_key) > 12:
            masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"
        else:
            masked_key = "***masked***"
        
        logger.info(f"Initializing Claude API with key prefix: {masked_key}")
        
        # Using Claude 3.5 Sonnet for enhanced PDF support and citations
        self.model = "claude-3-5-sonnet-latest"  # Use the latest model version that supports citations
        try:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                # No longer need to specify the PDF beta feature - it's built into the API now
            )
            logger.info(f"ClaudeService initialized with model: {self.model} and PDF support")
        except Exception as e:
            logger.error(f"Failed to initialize AsyncAnthropic client: {str(e)}")
            self.client = None
        
        # Initialize LangChain service
        self.langchain_service = LangChainService()
        
        # Initialize LangGraph service if available
        if LANGGRAPH_AVAILABLE:
            try:
                self.langgraph_service = LangGraphService()
                logger.info("LangGraph service successfully initialized")
            except ValueError as e:
                logger.error(f"LangGraph service configuration error: {str(e)}")
                self.langgraph_service = None
            except Exception as e:
                logger.error(f"Failed to initialize LangGraph service: {str(e)}")
                self.langgraph_service = None
        else:
            logger.warning("LangGraph service not available, skipping initialization")
            self.langgraph_service = None

    async def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate a response from Claude based on a conversation with a system prompt.
        
        Args:
            system_prompt: System prompt that guides Claude's behavior
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated response text
        """
        if not self.client:
            # Mock response for testing or when API key is not available
            logger.warning("Using mock response because Claude API client is not available")
            return "I'm sorry, I cannot process your request because the Claude API is not configured properly. Please check the API key and try again."
        
        try:
            # Convert message format to Anthropic's format
            formatted_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "assistant"
                formatted_messages.append({"role": role, "content": msg["content"]})
            
            logger.info(f"Sending request to Claude API with {len(formatted_messages)} messages")
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            error_message = f"I apologize, but there was an error processing your request: {str(e)}"
            return error_message

    async def process_pdf(self, pdf_data: bytes, filename: str) -> Tuple[ProcessedDocument, List[DocumentCitation]]:
        """
        Process a PDF using Claude's PDF support and citation extraction.
        
        Args:
            pdf_data: Raw bytes of the PDF file
            filename: Name of the PDF file
            
        Returns:
            A tuple containing the processed document and a list of citations
        """
        if not self.client:
            logger.error("Cannot process PDF because Claude API client is not available")
            raise ValueError("Claude API client is not available. Check your API key.")
        
        try:
            logger.info(f"Processing PDF: {filename} with Claude API and citations support")
            
            # Encode PDF data as base64
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            # Step 1: Extract raw text from PDF using PyPDF2
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
                logger.info(f"Successfully extracted {len(raw_text)} characters from PDF using PyPDF2")
            except Exception as extract_error:
                logger.warning(f"Failed to extract text from PDF using PyPDF2: {extract_error}")
                logger.info("Will continue with alternative extraction methods")
            
            # Step 2: Analyze document to determine type and periods
            logger.info("Analyzing document type")
            document_type, periods = await self._analyze_document_type(pdf_base64, filename)
            logger.info(f"Document classified as: {document_type.value} with periods: {periods}")
            
            # Step 3: Extract financial data with citations
            logger.info("Extracting financial data and citations")
            extracted_data, citations = await self._extract_financial_data_with_citations(
                pdf_content=pdf_data, 
                filename=filename, 
                document_type=document_type
            )
            logger.info(f"Extracted {len(citations)} citations")
            
            # Add or update raw_text in extracted_data if we have it
            if raw_text and len(raw_text.strip()) > 0:
                if not extracted_data:
                    extracted_data = {}
                extracted_data["raw_text"] = raw_text
                logger.info(f"Added {len(raw_text)} characters of raw text to extracted_data")
            
            # If we weren't able to extract raw text with PyPDF2, try to get it from Claude's response
            if not raw_text or len(raw_text.strip()) == 0:
                # Try to extract raw text from Claude's response if available
                if extracted_data.get("raw_text"):
                    raw_text = extracted_data.get("raw_text")
                    logger.info(f"Using raw text from Claude's response: {len(raw_text)} characters")
                else:
                    # If still no raw text, make one final attempt using OCR integration if available
                    try:
                        # Import OCR utility here to avoid circular imports
                        from pdf_processing.ocr_utilities import extract_text_with_ocr
                        
                        ocr_text = await extract_text_with_ocr(pdf_data)
                        if ocr_text and len(ocr_text.strip()) > 0:
                            raw_text = ocr_text
                            if not extracted_data:
                                extracted_data = {}
                            extracted_data["raw_text"] = raw_text
                            logger.info(f"Added {len(raw_text)} characters of OCR-extracted text")
                    except Exception as ocr_error:
                        logger.warning(f"OCR text extraction failed: {ocr_error}")
            
            # Log and return a warning if we still couldn't extract any text
            if not raw_text or len(raw_text.strip()) == 0:
                logger.warning(f"Failed to extract any text from PDF {filename} using multiple methods")
                # Create minimal raw text to avoid downstream issues
                raw_text = f"Failed to extract text content from {filename}. This document may contain scanned images or be password-protected."
                if not extracted_data:
                    extracted_data = {}
                extracted_data["raw_text"] = raw_text
            
            logger.info(f"Extracted data keys: {list(extracted_data.keys())}")
            
            # If we have financial data, update document type to FINANCIAL_REPORT if it wasn't already
            if extracted_data.get('financial_data') and extracted_data['financial_data']:
                if document_type != DocumentContentType.FINANCIAL_REPORT:
                    logger.info(f"Updating document type from {document_type.value} to FINANCIAL_REPORT based on extracted financial data")
                    document_type = DocumentContentType.FINANCIAL_REPORT
            
            # Create document metadata and processed document object
            document_id = str(uuid.uuid4())
            confidence_score = 0.8  # Default confidence score
            
            # Create document metadata
            metadata = DocumentMetadata(
                id=uuid.UUID(document_id),
                filename=filename,
                upload_timestamp=datetime.now(),
                file_size=len(pdf_data),
                mime_type="application/pdf",
                user_id="system"  # Default user for API processing
            )
            
            # Create processed document
            processed_document = ProcessedDocument(
                metadata=metadata,  # Include the required metadata
                content_type=document_type,
                extraction_timestamp=datetime.now(),
                periods=periods,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_status=ProcessingStatus.COMPLETED
            )
            
            return processed_document, citations
            
        except Exception as e:
            logger.exception(f"Error processing PDF: {e}")
            
            # Create minimal document with error information
            document_id = str(uuid.uuid4())
            metadata = DocumentMetadata(
                id=uuid.UUID(document_id),
                filename=filename,
                upload_timestamp=datetime.now(),
                file_size=len(pdf_data) if pdf_data else 0,
                mime_type="application/pdf",
                user_id="system"
            )
            
            error_message = f"Error processing PDF: {str(e)}"
            processed_document = ProcessedDocument(
                metadata=metadata,
                content_type=DocumentContentType.OTHER,
                extraction_timestamp=datetime.now(),
                extracted_data={"error": error_message, "raw_text": f"Failed to process document due to error: {str(e)}"},
                confidence_score=0.0,
                processing_status=ProcessingStatus.FAILED
            )
            
            return processed_document, []

    async def _analyze_document_type(self, pdf_base64: str, filename: str) -> Tuple[DocumentContentType, List[str]]:
        """
        Analyze the PDF to determine its document type and extract time periods.
        Uses the new document content format but doesn't need citations for this step.
        
        Args:
            pdf_base64: Base64 encoded PDF data
            filename: Name of the PDF file
            
        Returns:
            Tuple of document type and list of time periods
        """
        if not self.client:
            logger.error("Cannot analyze document type because Claude API client is not available")
            raise ValueError("Claude API client is not available. Check your API key.")
        
        try:
            logger.info(f"Analyzing document type for: {filename}")
            
            # Create messages using the new document format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this financial document. Determine if it's a balance sheet, income statement, cash flow statement, or other type of document. Also identify the time periods covered (e.g., Q1 2023, FY 2022, etc.). Return ONLY a JSON response in this format:\n\n{\n  \"document_type\": \"balance_sheet|income_statement|cash_flow|notes|other\",\n  \"periods\": [\"period1\", \"period2\", ...]\n}"
                        }
                    ]
                }
            ]
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=messages
            )
            
            # Extract JSON from the response
            result_text = response.content[0].text
            json_match = re.search(r'{.*}', result_text, re.DOTALL)
            if not json_match:
                logger.error(f"Could not extract JSON from response: {result_text[:100]}...")
                return DocumentContentType.OTHER, []
            
            # Parse the JSON response
            try:
                result = json.loads(json_match.group(0))
                
                # Handle pipe-separated document types (e.g., "balance_sheet|income_statement")
                doc_type_str = result.get("document_type", "other")
                logger.info(f"Raw document_type from Claude: {doc_type_str}")
                
                # Split by pipe if present and try each type
                if "|" in doc_type_str:
                    doc_types = doc_type_str.split("|")
                    # Try each type in order
                    for dt in doc_types:
                        dt = dt.strip()
                        try:
                            document_type = DocumentContentType(dt)
                            logger.info(f"Selected document type '{dt}' from combined types: {doc_type_str}")
                            break
                        except ValueError:
                            pass
                    else:
                        # If no valid type found, use OTHER
                        logger.warning(f"No valid document type found in '{doc_type_str}', using OTHER")
                        document_type = DocumentContentType.OTHER
                else:
                    # Single document type
                    try:
                        document_type = DocumentContentType(doc_type_str)
                    except ValueError:
                        logger.warning(f"Invalid document type '{doc_type_str}', using OTHER")
                        document_type = DocumentContentType.OTHER
                
                periods = result.get("periods", [])
                
                logger.info(f"Document classified as {document_type.value} with periods: {periods}")
                return document_type, periods
            except Exception as json_e:
                logger.error(f"Error parsing JSON response: {json_e}")
                return DocumentContentType.OTHER, []
            
        except Exception as e:
            logger.exception(f"Error in document type analysis: {e}")
            return DocumentContentType.OTHER, []

    async def _extract_financial_data_with_citations(self, pdf_content: bytes, filename: str = "document.pdf", document_type: DocumentContentType = None) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Extract financial data from a PDF with citations.
        
        Args:
            pdf_content: PDF file content as bytes or base64 string
            filename: Name of the PDF file
            document_type: Type of document being processed
            
        Returns:
            Tuple of extracted data dictionary and list of citations
        """
        if not self.client:
            logger.error("Cannot extract financial data because Claude API client is not available")
            raise ValueError("Claude API client is not available. Check your API key.")
        
        try:
            logger.info(f"Extracting financial data with citations from: {filename}")
            
            # Convert to base64 if needed
            if isinstance(pdf_content, bytes):
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            else:
                pdf_base64 = pdf_content
            
            # Prepare document type for the prompt
            doc_type_str = document_type.value if document_type else "financial document"
            
            # Financial analysis prompt with structured data extraction
            system_prompt = """You are a highly specialized financial document analysis assistant. Extract structured financial data from the document accurately.
Follow these guidelines:
1. Identify all financial tables and metrics
2. Extract values with their correct time periods, labels, and units
3. Present the data in a structured JSON format
4. Provide citations for all extracted data"""
            
            # Create messages with the PDF document
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": f"Analyze this {doc_type_str} and extract all financial data in a structured format. Include key metrics, time periods, and values. Return a comprehensive JSON with all the financial information."
                        }
                    ]
                }
            ]
            
            # Call Claude API with citations enabled
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=messages
            )
            
            # Extract text content and citations
            content = self._process_claude_response(response)
            text = content.get("text", "")
            citations = content.get("citations", [])
            
            # Parse the extracted data from the response text
            extracted_data = {}
            try:
                # Check for JSON format in the response
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                    # Clean up the JSON string if needed
                    json_str = re.sub(r'^```json\s*|\s*```$', '', json_str)
                    json_data = json.loads(json_str)
                    extracted_data = json_data
                else:
                    logger.warning("Could not find JSON data in Claude's response")
                    extracted_data = {"raw_text": text}
            except Exception as e:
                logger.error(f"Error parsing extracted data JSON: {str(e)}")
                extracted_data = {"raw_text": text, "error": str(e)}
            
            return extracted_data, citations
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            return {"error": str(e)}, []

    async def generate_response_with_citations(self, messages: List[Dict[str, Any]], documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response from Claude with support for citations.
        
        Args:
            messages: List of conversation messages with 'role' and 'content'
            documents: List of documents to include for citation
            
        Returns:
            Response with content, content blocks, and citations
        """
        # Debug logging for request tracking using print for immediate visibility
        print(f"DEBUG: generate_response_with_citations called with {len(messages)} messages and {len(documents)} documents")
        logger.info(f"generate_response_with_citations called with {len(messages)} messages and {len(documents)} documents")
        for doc in documents:
            doc_id = doc.get('id', 'unknown')
            doc_title = doc.get('title', 'Untitled')
            doc_type = doc.get('mime_type', 'unknown')
            print(f"DEBUG: Document in request: ID={doc_id}, Title={doc_title}, Type={doc_type}")
            logger.info(f"Document in request: ID={doc_id}, Title={doc_title}, Type={doc_type}")
        try:
            # Check if API client is available
            if not self.client:
                logger.error("Claude API client not initialized")
                return {
                    "content": "Error: Claude API not available. Please check your API key and try again.",
                    "content_blocks": [],
                    "citations": []
                }
            
            # Log message count and document count
            logger.info(f"Generating response with {len(messages)} messages and {len(documents)} documents")
            
            # Set system message as a separate parameter
            system_prompt = "You are Claude, an AI assistant by Anthropic. When you reference documents, provide specific citations."
            
            # Convert messages to Claude API format
            claude_messages = []
            
            # Process user and assistant messages
            for msg in messages:
                role = msg.get("role", "").lower()
                content = msg.get("content", "")
                
                # Map roles from our format to Claude's expected format
                if role == "user":
                    claude_role = "user"
                elif role == "assistant":
                    claude_role = "assistant"
                elif role == "system":
                    # Skip system messages as we're using a top-level system parameter
                    continue
                else:
                    logger.warning(f"Unknown message role: {role}, defaulting to user")
                    claude_role = "user"
                
                # Format the content correctly for Claude API
                if isinstance(content, str):
                    claude_content = [{"type": "text", "text": content}]
                elif isinstance(content, list):
                    claude_content = []
                    for item in content:
                        if isinstance(item, str):
                            claude_content.append({"type": "text", "text": item})
                        elif isinstance(item, dict) and "type" in item:
                            claude_content.append(item)
                        else:
                            logger.warning(f"Unsupported content format: {item}")
                else:
                    logger.warning(f"Unsupported content format: {content}")
                    claude_content = [{"type": "text", "text": str(content)}]
                
                claude_messages.append({
                    "role": claude_role,
                    "content": claude_content
                })
            
            # Prepare documents for citation
            if documents:
                # Find the user's last message to append documents
                last_user_msg_idx = -1
                for i, msg in enumerate(claude_messages):
                    if msg["role"] == "user":
                        last_user_msg_idx = i
                
                # If no user message exists, create one
                if last_user_msg_idx == -1:
                    logger.warning("No user message found to attach documents. Creating an empty one.")
                    claude_messages.append({
                        "role": "user",
                        "content": [{"type": "text", "text": "Please analyze these documents:"}]
                    })
                    last_user_msg_idx = len(claude_messages) - 1
                
                # Process and add each document
                for doc in documents:
                    doc_content = self._prepare_document_for_citation(doc)
                    if doc_content:
                        # Add document to the user's message content
                        claude_messages[last_user_msg_idx]["content"].append(doc_content)
                        logger.info(f"Added document {doc.get('id', 'unknown')} to user message")
                    else:
                        logger.warning(f"Failed to prepare document {doc.get('id', 'unknown')} for citation")
            
            # Log the final message structure (without large content)
            debug_messages = []
            for msg in claude_messages:
                debug_msg = {"role": msg["role"], "content": []}
                for content in msg["content"]:
                    if content["type"] == "document":
                        # Don't log the full base64 data
                        debug_content = {
                            "type": "document",
                            "source_type": content.get("source", {}).get("type", "unknown")
                        }
                    else:
                        # For text content, include a preview
                        text = content.get("text", "")
                        debug_content = {
                            "type": "text",
                            "text": text[:100] + "..." if len(text) > 100 else text
                        }
                    debug_msg["content"].append(debug_content)
                debug_messages.append(debug_msg)
            
            logger.debug(f"Claude API request messages: {json.dumps(debug_messages)}")
            
            # Call Claude API with system prompt as a top-level parameter
            try:
                # Add explicit citation enabling guidance to the system prompt
                enhanced_system_prompt = system_prompt + "\n\nIMPORTANT: Please provide detailed citations for all information from the documents. Be specific about page numbers and locations."
                
                # Dump messages for debugging
                logger.info(f"Sending request to Claude API with {len(claude_messages)} messages and system prompt")
                # Log the document structure for the first document (not the entire content)
                for msg in claude_messages:
                    if msg.get("role") == "user" and isinstance(msg.get("content"), list):
                        for item in msg.get("content", []):
                            if isinstance(item, dict) and item.get("type") == "document":
                                doc_type = item.get("source", {}).get("type")
                                citations_enabled = item.get("citations", {}).get("enabled", False)
                                logger.info(f"Document in request: type={doc_type}, citations_enabled={citations_enabled}")
                
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    messages=claude_messages,
                    system=enhanced_system_prompt
                )
                
                # Add detailed response logging with print for immediate visibility
                print(f"DEBUG: Claude API response received with {len(response.content)} content blocks")
                logger.info(f"Claude API response received with {len(response.content)} content blocks")
                
                # Inspect the full response object to see what fields it has
                print(f"DEBUG: Response type: {type(response)}")
                print(f"DEBUG: Response dir: {dir(response)}")
                
                # Dump first content block for analysis
                if len(response.content) > 0:
                    first_block = response.content[0]
                    print(f"DEBUG: First content block type: {first_block.type}")
                    print(f"DEBUG: First content block attrs: {dir(first_block)}")
                    # Check for raw citations field
                    if hasattr(first_block, '_citations') or hasattr(first_block, 'citations'):
                        citations_field = getattr(first_block, '_citations', getattr(first_block, 'citations', None))
                        print(f"DEBUG: First block citations: {citations_field}")
                
                # Check if there are any citations in the response
                citation_found = False
                for i, block in enumerate(response.content):
                    print(f"DEBUG: Content block {i} type: {block.type}")
                    if hasattr(block, 'citations') and block.citations:
                        citation_found = True
                        citation_count = len(block.citations)
                        print(f"DEBUG: Found {citation_count} citations in content block {i}")
                        logger.info(f"Found {citation_count} citations in content block {i}")
                        # Log first citation details for debugging
                        if citation_count > 0:
                            citation = block.citations[0]
                            citation_type = getattr(citation, 'type', 'unknown')
                            print(f"DEBUG: Sample citation type: {citation_type}")
                            print(f"DEBUG: Citation attributes: {dir(citation)}")
                            logger.info(f"Sample citation type: {citation_type}")
                    else:
                        print(f"DEBUG: No citations in content block {i}")
                        if hasattr(block, 'text'):
                            print(f"DEBUG: Block text preview: {block.text[:50]}...")
                
                if not citation_found:
                    print("DEBUG: WARNING - No citations found in the Claude API response")
                    logger.warning("No citations found in the Claude API response")
                
                # Process the response
                processed_response = self._process_claude_response(response)
                
                # Check if citations are available in the response
                citations = []
                if hasattr(response, 'content'):
                    for block in response.content:
                        if hasattr(block, 'citations') and block.citations:
                            for citation in block.citations:
                                citations.append(citation)
                
                logger.info(f"Extracted {len(citations)} citations from response")
                
                # Add citations to the processed response if available
                if citations:
                    processed_response["citations"] = citations
                    logger.info(f"Added {len(citations)} citations to response")
                
                return processed_response
                
            except Exception as e:
                logger.exception(f"Error calling Claude API: {e}")
                error_message = str(e)
                
                # Check for authentication errors
                if "authentication" in error_message.lower() or "api key" in error_message.lower() or "401" in error_message:
                    return {
                        "content": f"Error code: 401 - {error_message}",
                        "content_blocks": [],
                        "citations": []
                    }
                
                # Other API errors
                return {
                    "content": f"Error calling Claude API: {error_message}",
                    "content_blocks": [],
                    "citations": []
                }
            
        except Exception as e:
            logger.exception(f"Error generating response with citations: {e}")
            return {
                "content": f"An error occurred while processing your request: {str(e)}",
                "content_blocks": [],
                "citations": []
            }

    def _prepare_document_for_citation(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepare a document object for citation by Claude.
        
        Args:
            document: Document information dictionary
            
        Returns:
            Formatted document object for Claude API or None if invalid
        """
        try:
            # Extract document information
            doc_type = document.get("mime_type", "").lower()
            doc_id = document.get("id", "")
            doc_title = document.get("title", document.get("filename", f"Document {doc_id}"))
            
            # Try multiple sources for document content
            doc_content = None
            content_source = None
            
            # Log all available fields for debugging
            logger.info(f"Document fields: {list(document.keys())}")
            
            # First priority: "content" field
            if document.get("content"):
                doc_content = document.get("content")
                content_source = "content field"
            
            # Second priority: "raw_text" field
            elif document.get("raw_text"):
                doc_content = document.get("raw_text")
                content_source = "raw_text field"
                # For raw_text content, use text document type
                doc_type = "text/plain"
            
            # Third priority: "extracted_data.raw_text" field
            elif document.get("extracted_data") and isinstance(document.get("extracted_data"), dict) and document.get("extracted_data").get("raw_text"):
                doc_content = document.get("extracted_data").get("raw_text")
                content_source = "extracted_data.raw_text field"
                # For extracted text, use text document type
                doc_type = "text/plain"
            
            # Fourth priority: "text" field
            elif document.get("text"):
                doc_content = document.get("text")
                content_source = "text field"
                # For text content, use text document type
                doc_type = "text/plain"
                
            # Fifth priority: Try to get the raw PDF content from storage
            elif document.get("id"):
                try:
                    # Attempt to get the PDF data directly - this is a fallback mechanism
                    from repositories.document_repository import DocumentRepository
                    from repositories.database import get_database_session
                    
                    # Get session and repository
                    db_session = get_database_session()
                    document_repository = DocumentRepository(db_session)
                    
                    # Get document content directly
                    doc_content = asyncio.run(document_repository.get_document_file_content(document.get('id')))
                    
                    if doc_content and len(doc_content) > 0:
                        content_source = "direct PDF from storage"
                        doc_type = "application/pdf"
                        logger.info(f"Retrieved PDF content directly from storage for document {doc_id}")
                except Exception as storage_e:
                    logger.warning(f"Failed to get PDF directly from storage for document {doc_id}: {storage_e}")
                    
            # If all attempts to get content failed, create a minimal document with placeholder text
            if not doc_content:
                logger.warning(f"No document content found for {doc_id} - using fallback placeholder")
                doc_content = f"Document content unavailable for {doc_title}. Please try re-uploading the document."
                content_source = "fallback placeholder"
                doc_type = "text/plain"
            
            if content_source:
                logger.info(f"Using {content_source} for document {doc_id}")
            
            # Handle PDF documents
            if "pdf" in doc_type or doc_type == "application/pdf":
                # Ensure PDF content is bytes
                if not isinstance(doc_content, bytes):
                    if isinstance(doc_content, str) and doc_content.startswith(('data:application/pdf;base64,', 'data:;base64,')):
                        # Handle base64 encoded PDF data URLs
                        base64_content = doc_content.split('base64,')[1]
                        doc_content = base64.b64decode(base64_content)
                    elif isinstance(doc_content, str) and len(doc_content) > 0:
                        try:
                            # Check if it might be base64 encoded
                            if all(c in string.ascii_letters + string.digits + '+/=' for c in doc_content):
                                try:
                                    doc_content = base64.b64decode(doc_content)
                                    logger.info(f"Successfully decoded base64 content for document {doc_id}")
                                except:
                                    # Not valid base64, treat as text
                                    logger.warning(f"Content for {doc_id} looks like base64 but couldn't be decoded")
                                    doc_content = doc_content.encode('utf-8')
                            else:
                                # Regular text, encode to bytes
                                doc_content = doc_content.encode('utf-8')
                        except Exception as e:
                            logger.warning(f"Failed to convert string content to bytes for {doc_id}: {e}")
                            return None
                    else:
                        logger.warning(f"Invalid PDF content for {doc_id} - not bytes or base64 string")
                        return None
                
                # Validate PDF content
                if len(doc_content) < 10:  # Arbitrary small size check
                    logger.warning(f"PDF content for {doc_id} is too small ({len(doc_content)} bytes)")
                    return None
                
                # Check if content starts with PDF signature
                if not doc_content.startswith(b'%PDF'):
                    logger.warning(f"Content for {doc_id} doesn't start with PDF signature")
                    # We'll still try to use it, as it might be a valid PDF despite missing the signature
                
                # Create PDF document object for Claude API
                try:
                    base64_data = base64.b64encode(doc_content).decode()
                    logger.info(f"Successfully encoded PDF content for document {doc_id} ({len(doc_content)} bytes)")
                    
                    # Format according to Anthropic's Citations documentation
                    return {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64_data
                        },
                        "title": doc_title,
                        "citations": {"enabled": True}
                    }
                except Exception as e:
                    logger.exception(f"Error encoding PDF content for {doc_id}: {e}")
                    return None
            
            # At this point, treat as text document (either originally or after conversion)
            # Ensure we have valid string content
            text_content = ""
            if isinstance(doc_content, str):
                text_content = doc_content
            elif isinstance(doc_content, bytes):
                try:
                    text_content = doc_content.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    text_content = f"Binary content for {doc_title} (could not convert to text)"
            else:
                text_content = f"Content for {doc_title} in unsupported format: {type(doc_content)}"
            
            # Ensure we have some minimal content
            if not text_content.strip():
                text_content = f"Empty document content for {doc_title}"
            
            # Truncate very long text to avoid token limits (30,000 chars ~ 7,500 tokens)
            if len(text_content) > 30000:
                text_content = text_content[:30000] + f"\n\n[Document truncated due to length. Original size: {len(text_content)} characters]"
            
            logger.info(f"Prepared text document for Claude API: {doc_id}, length: {len(text_content)} chars")
            
            # Create proper text document format for Claude API
            return {
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": text_content
                },
                "title": doc_title,
                "citations": {"enabled": True}
            }
                
        except Exception as e:
            logger.exception(f"Error preparing document for citation: {e}")
            # Return a minimal valid document to prevent API errors
            return {
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": f"Error preparing document {document.get('id', 'unknown')} for citation: {str(e)}"
                },
                "title": document.get("title", document.get("filename", "Document")),
                "citations": {"enabled": True}
            }

    def _process_claude_response(self, response: AnthropicMessage) -> Dict[str, Any]:
        """
        Process Claude's response to extract content and citations.
        
        Args:
            response: Claude API response
            
        Returns:
            Processed response with text content and structured citations
        """
        result = {
            "text": "",
            "citations": []
        }
        
        # Extract text content
        if hasattr(response, "content") and response.content:
            # Combine all text content
            text_parts = []
            citations = []
            
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                    
                    # Process citations if available
                    if hasattr(block, "citations") and block.citations:
                        for citation in block.citations:
                            citation_obj = self._convert_claude_citation(citation)
                            if citation_obj:
                                citations.append(citation_obj)
            
            result["text"] = "\n".join(text_parts)
            result["citations"] = citations
        
        return result

    def _convert_claude_citation(self, citation: Any) -> Optional[Union[Dict[str, Any], Citation]]:
        """
        Convert Claude citation to our Citation model.
        
        Args:
            citation: Citation from Claude API
            
        Returns:
            Citation object or dictionary or None if conversion fails
        """
        try:
            # Handle both class attribute and dictionary access
            if hasattr(citation, 'type'):
                citation_type = citation.type
            elif isinstance(citation, dict):
                citation_type = citation.get('type')
            else:
                logger.warning(f"Unknown citation format: {type(citation)}")
                return None
            
            # Handle different citation types
            if citation_type == "page_citation" or citation_type == "page_location":
                # For PDF citations
                document_id = None
                # Only try to get document.id if the attribute exists
                if hasattr(citation, 'document') and hasattr(citation.document, 'id'):
                    document_id = citation.document.id
                elif isinstance(citation, dict) and 'document' in citation:
                    document_id = citation.get('document', {}).get('id')
                
                # Extract page information
                page_info = {}
                if hasattr(citation, 'page'):
                    page_info = {
                        'start_page': getattr(citation.page, 'start', 1),
                        'end_page': getattr(citation.page, 'end', 1)
                    }
                elif isinstance(citation, dict) and 'page' in citation:
                    page_info = {
                        'start_page': citation['page'].get('start', 1),
                        'end_page': citation['page'].get('end', 1)
                    }
                
                cited_text = ""
                if hasattr(citation, 'text'):
                    cited_text = citation.text
                elif isinstance(citation, dict):
                    cited_text = citation.get('text', '')
                
                return {
                    "type": "page_location",
                    "cited_text": cited_text,
                    "document_id": document_id,
                    "start_page_number": page_info.get('start_page', 1),
                    "end_page_number": page_info.get('end_page', 1)
                }
            
            elif citation_type in ["quote_citation", "text_citation", "char_location"]:
                # For text citations
                document_id = None
                # Only try to get document.id if the attribute exists
                if hasattr(citation, 'document') and hasattr(citation.document, 'id'):
                    document_id = citation.document.id
                elif isinstance(citation, dict) and 'document' in citation:
                    document_id = citation.get('document', {}).get('id')
                
                # Get cited text
                cited_text = ""
                if hasattr(citation, 'text'):
                    cited_text = citation.text
                elif hasattr(citation, 'cited_text'):
                    cited_text = citation.cited_text
                elif isinstance(citation, dict):
                    cited_text = citation.get('text', citation.get('cited_text', ''))
                
                # Get start and end indices if available
                start_index = 0
                end_index = 0
                
                # Handle different attribute names for character indices
                if hasattr(citation, 'start_index'):
                    start_index = citation.start_index
                elif hasattr(citation, 'start_char_index'):
                    start_index = citation.start_char_index
                elif isinstance(citation, dict):
                    start_index = citation.get('start_index', citation.get('start_char_index', 0))
                
                if hasattr(citation, 'end_index'):
                    end_index = citation.end_index
                elif hasattr(citation, 'end_char_index'):
                    end_index = citation.end_char_index
                elif isinstance(citation, dict):
                    end_index = citation.get('end_index', citation.get('end_char_index', 0))
                
                return {
                    "type": "char_location",
                    "cited_text": cited_text,
                    "document_id": document_id,
                    "start_char_index": start_index,
                    "end_char_index": end_index
                }
            
            else:
                logger.warning(f"Unknown citation type: {citation_type}")
                # Return a generic citation with available information
                if isinstance(citation, dict):
                    # Try to extract document info
                    document_id = citation.get('document', {}).get('id', 'unknown')
                    return {
                        "type": "unknown",
                        "document_id": document_id,
                        "cited_text": citation.get('text', '')
                    }
                return None
                
        except Exception as e:
            logger.exception(f"Error converting Claude citation: {e}")
            return None

    async def generate_response_with_langgraph(
        self,
        question: str,
        document_texts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using LangGraph for document Q&A.
        This is a lighter-weight alternative to running the full conversation graph.
        Supports Claude's citation feature for accurate document references.
        
        Args:
            question: The user's question
            document_texts: List of documents with their text content
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary containing the response text and any extracted citations
        """
        # Critical logging for document processing diagnosis
        logger.info(f"===== Claude API document processing request =====")
        logger.info(f"Question: {question[:100]}" + ("..." if len(question) > 100 else ""))
        logger.info(f"Number of documents: {len(document_texts)}")
        logger.info(f"History length: {len(conversation_history) if conversation_history else 0}")
        
        # Log document IDs for tracing
        doc_ids = [doc.get('id', 'unknown') for doc in document_texts]
        logger.info(f"Document IDs in request: {doc_ids}")
        
        # Check document content existence 
        for i, doc in enumerate(document_texts):
            doc_id = doc.get('id', f'doc_{i}')
            has_content = False
            
            # Check various possible content fields
            if 'raw_text' in doc and doc['raw_text']:
                has_content = True
                logger.info(f"Document {doc_id} has raw_text content: {len(doc['raw_text'])} chars")
            elif 'content' in doc and isinstance(doc['content'], str) and doc['content']:
                has_content = True
                logger.info(f"Document {doc_id} has string content: {len(doc['content'])} chars")
            elif 'text' in doc and doc['text']:
                has_content = True
                logger.info(f"Document {doc_id} has text content: {len(doc['text'])} chars")
            elif 'extracted_data' in doc and doc['extracted_data']:
                extracted_type = type(doc['extracted_data']).__name__
                logger.info(f"Document {doc_id} has extracted_data of type: {extracted_type}")
                
                if isinstance(doc['extracted_data'], dict) and 'raw_text' in doc['extracted_data']:
                    has_content = True
                    logger.info(f"Document {doc_id} has extracted_data.raw_text: {len(doc['extracted_data']['raw_text'])} chars")
            
            if not has_content:
                logger.warning(f"⚠️ Document {doc_id} has no usable text content! This may cause visibility issues.")
                logger.warning(f"Available keys: {list(doc.keys())}")
        
        logger.info(f"===== End Claude API document request information =====")
        
        if not LANGGRAPH_AVAILABLE or not self.langgraph_service:
            logger.warning("LangGraph service is not available, falling back to LangChain")
            # Fall back to LangChain if LangGraph is not available
            if self.langchain_service:
                logger.info("Using LangChain for response generation")
                response_text = await self.langchain_service.analyze_document_content(
                    question=question,
                    document_extracts=[doc.get("text", "") for doc in document_texts if "text" in doc],
                    conversation_history=conversation_history
                )
                return {
                    "content": response_text,
                    "citations": []  # No citations with LangChain fallback
                }
            else:
                logger.warning("LangChain service is not available, falling back to direct Claude API")
                # Fall back to regular response generation
                system_prompt = "You are a financial document analysis assistant. Answer questions based on your knowledge."
                messages = []
                
                # Add conversation history to messages
                if conversation_history:
                    for msg in conversation_history:
                        messages.append(msg)
                
                # Add current question
                messages.append({"role": "user", "content": question})
                
                response_text = await self.generate_response(
                    system_prompt=system_prompt,
                    messages=messages
                )
                return {
                    "content": response_text,
                    "citations": []  # No citations with direct API fallback
                }
        
        try:
            logger.info(f"Using LangGraph for response generation with {len(document_texts)} documents")
            # Use LangGraph service for document QA with citation support
            response = await self.langgraph_service.simple_document_qa(
                question=question,
                documents=document_texts,
                conversation_history=conversation_history
            )
            
            # Handle the response, which should now be a dictionary with content and citations
            if isinstance(response, dict):
                content = response.get("content", "")
                citations = response.get("citations", [])
                
                logger.info(f"Generated response with {len(citations)} citations")
                
                # Return the structured response with citations
                return {
                    "content": content,
                    "citations": citations
                }
            elif isinstance(response, str):
                # Handle legacy response format (string only)
                logger.warning("Received legacy string response from simple_document_qa")
                return {
                    "content": response,
                    "citations": []
                }
            else:
                # Handle unexpected response type
                logger.error(f"Unexpected response type from simple_document_qa: {type(response)}")
                return {
                    "content": "I apologize, but there was an error processing your request.",
                    "citations": []
                }
                
        except Exception as e:
            logger.error(f"Error in generate_response_with_langgraph: {str(e)}", exc_info=True)
            return {
                "content": f"I apologize, but there was an error processing your request: {str(e)}",
                "citations": []
            }

    async def extract_structured_financial_data(self, text: str, pdf_data: bytes = None, filename: str = None) -> Dict[str, Any]:
        """
        Extract structured financial data from raw text using Claude.
        This is a fallback method when standard extraction fails to find financial tables.
        
        Args:
            text: Raw text from a document
            pdf_data: Optional raw bytes of the PDF file for improved extraction with native PDF support
            filename: Optional filename of the PDF
            
        Returns:
            Dictionary of structured financial data
        """
        if not self.client:
            logger.error("Cannot extract structured data because Claude API client is not available")
            return {"error": "Claude API client is not available"}
        
        try:
            logger.info("Attempting to extract structured financial data from text")
            
            # Create a specialized prompt for financial data extraction
            extraction_prompt = """Please analyze this financial document text and extract structured financial data.
            
            Output the data in the following JSON format:
            {
                "metrics": [
                    {"name": "Revenue", "value": 1000000, "period": "2023", "unit": "USD"},
                    {"name": "Net Income", "value": 200000, "period": "2023", "unit": "USD"}
                ],
                "ratios": [
                    {"name": "Profit Margin", "value": 0.2, "description": "Net income divided by revenue"}
                ],
                "periods": ["2023", "2022"],
                "key_insights": [
                    "Revenue increased by 15% from 2022 to 2023",
                    "Profit margin improved from 15% to 20%"
                ]
            }
            
            If you can identify any financial statements (income statement, balance sheet, cash flow), please structure them accordingly.
            Be sure to extract specific numbers, dates, and proper units.
            If you cannot find specific financial data, return an empty object for that category."""
            
            # Setup system prompt
            system_prompt = """You are a financial data extraction assistant. Your task is to extract structured financial data from text.
            Always output valid JSON. If specific financial metrics are not available, include empty arrays in those categories.
            Be precise with numbers and dates. Recognize financial statements and extract metrics, ratios, and insights."""
            
            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": extraction_prompt
                        }
                    ]
                }
            ]
            
            # If we have PDF data, use it with the document content type for better extraction
            if pdf_data:
                logger.info(f"Using native PDF document support for financial data extraction")
                
                # Prepare the document for citation using our enhanced method
                document = {
                    "id": "financial_document",
                    "title": filename if filename else "Financial Document",
                    "content": pdf_data,
                    "mime_type": "application/pdf"
                }
                
                prepared_document = self._prepare_document_for_citation(document)
                if not prepared_document:
                    logger.warning("Failed to prepare document for financial data extraction, falling back to text")
                else:
                    # Add the prepared document as content in the user message
                    messages.append({
                        "role": "user",
                        "content": [prepared_document]
                    })
            else:
                # Fall back to using just the text content
                logger.info("Using text-only mode for financial data extraction")
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text[:15000]  # Limit text length
                        }
                    ]
                })
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=messages,
                system=system_prompt,
                temperature=0.0  # Use low temperature for factual extraction
            )
            
            # Extract the JSON from the response
            response_text = response.content[0].text if response.content else ""
            
            # Find JSON in the response
            json_pattern = r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}'
            json_match = re.search(json_pattern, response_text)
            
            if json_match:
                json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                try:
                    structured_data = json.loads(json_str)
                    logger.info(f"Successfully extracted structured financial data: {len(structured_data)} categories")
                    return structured_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Claude response: {e}")
                    return {"error": "Failed to parse financial data", "raw_response": response_text}
            else:
                logger.error("No JSON data found in Claude response")
                return {"error": "No structured data found in response", "raw_response": response_text}
        
        except Exception as e:
            logger.exception(f"Error in structured financial data extraction: {e}")
            return {"error": f"Extraction failed: {str(e)}"}