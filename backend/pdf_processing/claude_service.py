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

from models.document import ProcessedDocument, Citation as DocumentCitation, DocumentContentType
from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation, ContentBlockLocationCitation
from pdf_processing.langchain_service import LangChainService

# Set up logger
logger = logging.getLogger(__name__)

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
        self.model = "claude-3-5-sonnet-latest"  # Use latest version for best citation support
        try:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                default_headers={
                    "anthropic-beta": "citations-2023-11-13,pdfs-2024-09-25"  # Enable both citations and PDF support beta
                }
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
            
            # Step 1: Analyze document to determine type and periods
            logger.info("Analyzing document type")
            document_type, periods = await self._analyze_document_type(pdf_base64, filename)
            logger.info(f"Document classified as: {document_type.value} with periods: {periods}")
            
            # Step 2: Extract financial data with citations
            logger.info("Extracting financial data and citations")
            extracted_data, citations = await self._extract_financial_data_with_citations(
                pdf_content=pdf_data, 
                filename=filename, 
                document_type=document_type
            )
            logger.info(f"Extracted {len(citations)} citations")
            logger.info(f"Extracted data keys: {list(extracted_data.keys())}")
            logger.info(f"Financial data keys: {list(extracted_data.get('financial_data', {}).keys())}")
            
            # If we have financial data, update document type to FINANCIAL_REPORT if it wasn't already
            if extracted_data.get('financial_data') and extracted_data['financial_data']:
                if document_type != DocumentContentType.FINANCIAL_REPORT:
                    logger.info(f"Updating document type from {document_type.value} to FINANCIAL_REPORT based on extracted financial data")
                    document_type = DocumentContentType.FINANCIAL_REPORT
            
            # Create document metadata and processed document object
            document_id = str(uuid.uuid4())
            confidence_score = 0.8  # Default confidence score
            
            # Create processed document
            processed_document = ProcessedDocument(
                content_type=document_type,
                extraction_timestamp=datetime.now().isoformat(),
                periods=periods,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_status="completed"
            )
            
            return processed_document, citations
            
        except Exception as e:
            logger.exception(f"Error processing PDF: {e}")
            raise

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
        try:
            logger.info("Analyzing document type with Claude API")
            
            # Create message using document content type
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
                            },
                            "title": filename,
                            "citations": {"enabled": False}  # No need for citations in document type analysis
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
                document_type = DocumentContentType(result.get("document_type", "other"))
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
        try:
            logger.info(f"Extracting financial data from PDF: {filename}")
            
            # Handle both bytes and base64 string input
            if isinstance(pdf_content, bytes):
                # Convert PDF to base64
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            else:
                # Already base64
                pdf_base64 = pdf_content
            
            # Create a prompt to extract financial data
            prompt = """Please analyze this financial document and extract key financial information.
                     Identify important metrics like revenue, profit, EPS, and any significant financial events.
                     Be specific with numbers and cite the pages where you found the information."""
            
            # Set system prompt
            system_prompt = "You are a financial analyst assistant. Extract relevant financial metrics and data from documents with accurate citations."
            
            # Setup messages for Claude
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
                            },
                            "title": filename,
                            "citations": {"enabled": True}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            # Call Claude API with separate system prompt
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=messages,
                system=system_prompt
            )
            
            # Process the response with citation blocks
            extracted_data = {"raw_text": "", "financial_data": {}}
            citations = []
            
            # Extract raw text and citations from the response
            raw_text_parts = []
            financial_insights = {}
            
            # Track the financial metrics we've found
            metrics_count = 0
            
            # Process each content block in the response
            for content_block in response.content:
                if content_block.type == "text":
                    raw_text_parts.append(content_block.text)
                    
                    # If the block has citations, process them
                    if hasattr(content_block, "citations") and content_block.citations:
                        # This block contains useful financial insights with citations
                        block_text = content_block.text
                        
                        # Add an entry in financial_insights
                        insight_id = f"insight_{metrics_count}"
                        
                        # Actually store the insight in the financial_insights dictionary
                        financial_insights[insight_id] = {
                            "text": block_text,
                            "citations": [],
                            "page_references": []
                        }
                        
                        # Process each citation
                        for citation in content_block.citations:
                            citation_obj = self._convert_claude_citation(citation)
                            if citation_obj:
                                # Handle both dictionary and object formats
                                if isinstance(citation_obj, dict):
                                    citation_type = citation_obj.get("type", "unknown")
                                    
                                    # Extract page number based on citation type
                                    if citation_type == "page_location":
                                        page_num = citation_obj.get("start_page_number", 1)
                                    elif citation_type == "char_location":
                                        page_num = 1  # Default for char citations
                                    else:
                                        page_num = 1  # Default fallback
                                    
                                    doc_citation = DocumentCitation(
                                        id=str(uuid.uuid4()),
                                        page=page_num,
                                        text=citation_obj.get("cited_text", ""),
                                        section=f"Page {page_num}"
                                    )
                                else:
                                    # Handle object attributes with fallbacks
                                    if hasattr(citation_obj, "type"):
                                        citation_type = citation_obj.type
                                    else:
                                        citation_type = "unknown"
                                    
                                    # Extract page number based on citation type
                                    if hasattr(citation_obj, "start_page_number"):
                                        page_num = citation_obj.start_page_number
                                    else:
                                        page_num = 1  # Default fallback
                                    
                                    doc_citation = DocumentCitation(
                                        id=str(uuid.uuid4()),
                                        page=page_num,
                                        text=getattr(citation_obj, "cited_text", ""),
                                        section=f"Page {page_num}"
                                    )
                                # Add the page reference to the current insight
                                financial_insights[insight_id]["citations"].append(doc_citation.id)
                                financial_insights[insight_id]["page_references"].append(page_num)
                                
                                citations.append(doc_citation)
                        
                        metrics_count += 1
            
            # Combine all raw text parts
            extracted_data["raw_text"] = "\n".join(raw_text_parts)
            extracted_data["financial_data"] = financial_insights
            
            # If no financial insights were found, try structured extraction as a fallback
            if not financial_insights and extracted_data["raw_text"]:
                logger.info("No financial insights found with citations. Trying structured extraction fallback.")
                try:
                    structured_data = await self.extract_structured_financial_data(extracted_data["raw_text"])
                    
                    # If structured data was successfully extracted, use it
                    if structured_data and not structured_data.get("error"):
                        logger.info("Successfully extracted structured financial data as fallback")
                        
                        # Create financial insights from structured data
                        if "metrics" in structured_data and structured_data["metrics"]:
                            extracted_data["financial_data"]["metrics"] = structured_data["metrics"]
                            
                        if "ratios" in structured_data and structured_data["ratios"]:
                            extracted_data["financial_data"]["ratios"] = structured_data["ratios"]
                            
                        if "key_insights" in structured_data and structured_data["key_insights"]:
                            extracted_data["financial_data"]["insights"] = structured_data["key_insights"]
                            
                        if "periods" in structured_data and structured_data["periods"]:
                            extracted_data["periods"] = structured_data["periods"]
                            
                except Exception as fallback_error:
                    logger.error(f"Error in structured extraction fallback: {fallback_error}")
            
            return extracted_data, citations
            
        except Exception as e:
            logger.exception(f"Error extracting financial data: {e}")
            raise

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
                
                # Debug dump of raw citations extraction before processing
                citation_count = 0
                for block in response.content:
                    if hasattr(block, 'citations') and block.citations:
                        citation_count += len(block.citations)
                
                print(f"DEBUG: Found total of {citation_count} raw citations in Claude API response")
                
                # If no citations found, print a special warning
                if citation_count == 0:
                    print("DEBUG: WARNING - Claude API NOT returning structured citations!")
                    print("DEBUG: This indicates a potential issue with the API or model configuration.")
                    print("DEBUG: Forcing page-based manual citation extraction as fallback")
                    
                    # Create manual citations based on bracketed text in response
                    manual_citations = []
                    # Match patterns like [Page X], [page X], or just [X] where X is a number
                    page_citation_patterns = [
                        r'\[Page (\d+)\]',
                        r'\[page (\d+)\]', 
                        r'\[p\.? (\d+)\]',
                        r'\[(\d+)\]'
                    ]
                    
                    for i, block in enumerate(response.content):
                        if block.type == "text" and hasattr(block, 'text'):
                            text = block.text
                            all_matches = []
                            
                            # Try all citation patterns
                            for pattern in page_citation_patterns:
                                page_matches = re.findall(pattern, text)
                                if page_matches:
                                    all_matches.extend(page_matches)
                            
                            if all_matches:
                                print(f"DEBUG: Found {len(all_matches)} manual page citations in text: {all_matches}")
                                
                                # Try to extract context around the citation
                                # Find sentences containing citations
                                sentences = re.split(r'(?<=[.!?])\s+', text)
                                for sentence in sentences:
                                    for pattern in page_citation_patterns:
                                        page_refs = re.findall(pattern, sentence)
                                        if page_refs:
                                            for page_num in page_refs:
                                                # Get the sentence text without the citation pattern
                                                clean_sentence = re.sub(r'\[[^\]]*\]', '', sentence).strip()
                                                
                                                manual_citation = {
                                                    "type": "page_location",
                                                    "document_index": 0,  # First document
                                                    "document_title": "Financial Report",  # Generic title
                                                    "start_page_number": int(page_num),
                                                    "end_page_number": int(page_num) + 1,
                                                    "cited_text": clean_sentence[:200],  # Limit text length
                                                }
                                                manual_citations.append(manual_citation)
                            
                            # If no sentence-based citations were found, fallback to simple page numbers
                            if not manual_citations:
                                for pattern in page_citation_patterns:
                                    page_matches = re.findall(pattern, text)
                                    if page_matches:
                                        for page_num in page_matches:
                                            manual_citation = {
                                                "type": "page_location",
                                                "document_index": 0,  # First document
                                                "document_title": "Financial Report",  # Generic title
                                                "start_page_number": int(page_num),
                                                "end_page_number": int(page_num) + 1,
                                                "cited_text": f"Financial data from page {page_num}",
                                            }
                                            manual_citations.append(manual_citation)
                    
                    if manual_citations:
                        print(f"DEBUG: Created {len(manual_citations)} manual fallback citations")
                
                # Process the response
                processed_response = self._process_claude_response(response)
                
                # If we created manual citations, add them to the processed response
                if citation_count == 0 and 'manual_citations' in locals() and manual_citations:
                    processed_response["citations"] = manual_citations
                    print(f"DEBUG: Added {len(manual_citations)} manual citations to response")
                    # Make sure manual citations are easy to identify for debugging
                    print(f"DEBUG: Manual citation example: {manual_citations[0] if manual_citations else 'None'}")
                
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
            doc_content = document.get("content", "")
            doc_id = document.get("id", "")
            doc_title = document.get("title", f"Document {doc_id}")
            
            if not doc_content:
                logger.warning(f"Empty document content for {doc_id}")
                return None
            
            # Default to PDF type if not specified but content is bytes
            if not doc_type and isinstance(doc_content, bytes):
                doc_type = "application/pdf"
                logger.info(f"Assuming PDF type for document {doc_id} based on bytes content")
            
            # Handle PDF documents
            if "pdf" in doc_type or doc_type == "application/pdf":
                # Ensure PDF content is bytes
                if not isinstance(doc_content, bytes):
                    if isinstance(doc_content, str) and doc_content.startswith(('data:application/pdf;base64,', 'data:;base64,')):
                        # Handle base64 encoded PDF data URLs
                        base64_content = doc_content.split('base64,')[1]
                        doc_content = base64.b64decode(base64_content)
                    elif isinstance(doc_content, str) and len(doc_content) > 0:
                        # Try to convert string to bytes if it's not empty
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
            
            # Handle text documents
            elif doc_type == "text/plain" or isinstance(doc_content, str):
                text_content = doc_content if isinstance(doc_content, str) else doc_content.decode('utf-8')
                return {
                    "type": "document",
                    "source": {
                        "type": "text",
                        "text": text_content
                    },
                    "title": doc_title,
                    "citations": {"enabled": True}
                }
            
            else:
                logger.warning(f"Unsupported document type: {doc_type}")
                return None
                
        except Exception as e:
            logger.exception(f"Error preparing document for citation: {e}")
            return None

    def _process_claude_response(self, response: AnthropicMessage) -> Dict[str, Any]:
        """
        Process Claude's response to extract content and citations.
        
        Args:
            response: Claude API response
            
        Returns:
            Processed response with text content and structured citations
        """
        try:
            processed_response = {
                "content": "",
                "content_blocks": [],
                "citations": []
            }
            
            # Check if response contains content
            if not response.content or len(response.content) == 0:
                logger.warning("Claude returned empty response content")
                return processed_response
            
            # Log response structure for debugging
            logger.info(f"Processing Claude response with {len(response.content)} content blocks")
            for i, block in enumerate(response.content):
                logger.info(f"Content block {i}: type={block.type}")
                if hasattr(block, 'citations') and block.citations:
                    logger.info(f"  - Contains {len(block.citations)} citations")
                    # Log citation details
                    for j, citation in enumerate(block.citations):
                        if hasattr(citation, 'type'):
                            logger.info(f"    - Citation {j}: type={citation.type}")
                        elif isinstance(citation, dict):
                            logger.info(f"    - Citation {j}: type={citation.get('type', 'unknown')}")
                        else:
                            logger.info(f"    - Citation {j}: unknown format {type(citation)}")
                
            # Process each content block
            full_text = []
            citation_count = 0
            
            for content_block in response.content:
                # Handle text blocks
                if content_block.type == "text":
                    # Add text to full response text
                    full_text.append(content_block.text)
                    
                    # Create content block
                    block = {
                        "type": "text",
                        "text": content_block.text
                    }
                    
                    # Process citations if present
                    if hasattr(content_block, 'citations') and content_block.citations:
                        block_citations = []
                        
                        # Convert each citation to our model
                        for citation in content_block.citations:
                            citation_obj = self._convert_claude_citation(citation)
                            if citation_obj:
                                # Add a unique ID to the citation
                                citation_count += 1
                                citation_id = f"citation_{citation_count}"
                                
                                # Update the citation object with the ID
                                if isinstance(citation_obj, dict):
                                    citation_obj["id"] = citation_id
                                else:
                                    citation_obj.id = citation_id
                                
                                block_citations.append(citation_obj)
                                
                                # Add to the global citations list
                                processed_response["citations"].append(citation_obj)
                        
                        # Add citations to the block
                        if block_citations:
                            block["citations"] = block_citations
                    
                    processed_response["content_blocks"].append(block)
                
                # Handle other content types if needed
                else:
                    logger.warning(f"Unhandled content block type: {content_block.type}")
            
            # Combine text into one response
            processed_response["content"] = "\n".join(full_text)
            
            # Log citation count
            if processed_response["citations"]:
                logger.info(f"Processed {len(processed_response['citations'])} citations from Claude response")
                # Log some details about the first few citations
                for i, citation in enumerate(processed_response["citations"][:3]):
                    if isinstance(citation, dict):
                        logger.info(f"Citation {i}: type={citation.get('type', 'unknown')}, text={citation.get('cited_text', '')[:50]}...")
                    else:
                        logger.info(f"Citation {i}: type={getattr(citation, 'type', 'unknown')}, text={getattr(citation, 'cited_text', '')[:50]}...")
            else:
                logger.warning("No citations found in Claude response")
            
            return processed_response
            
        except Exception as e:
            logger.exception(f"Error processing Claude response: {e}")
            # Return basic response without citations
            try:
                # Try to extract basic text content
                content = ""
                if response.content and len(response.content) > 0:
                    for block in response.content:
                        if hasattr(block, "text"):
                            content += block.text + "\n"
                
                return {
                    "content": content.strip(),
                    "content_blocks": [],
                    "citations": []
                }
            except Exception as nested_error:
                logger.exception(f"Error extracting basic content from response: {nested_error}")
                # Fallback for any other errors
                return {
                    "content": "Error processing response",
                    "content_blocks": [],
                    "citations": []
                }

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

    async def extract_structured_financial_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured financial data from raw text using Claude.
        This is a fallback method when standard extraction fails to find financial tables.
        
        Args:
            text: Raw text from a document
            
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
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{extraction_prompt}\n\n{text[:15000]}"  # Limit text length
                            }
                        ]
                    }
                ],
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