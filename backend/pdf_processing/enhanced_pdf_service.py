import os
import base64
import io
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, BinaryIO
import PyPDF2
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser

from models.document import ProcessedDocument, DocumentContentType, Citation

logger = logging.getLogger(__name__)

class EnhancedPDFService:
    """Enhanced PDF processing service using LangChain."""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-latest")
        self.llm = ChatAnthropic(
            model=self.model,
            temperature=0.1,
            anthropic_api_key=api_key
        )
        
        # Initialize structured extraction prompts
        self._init_extraction_prompts()
    
    def _init_extraction_prompts(self):
        """Initialize the prompts for structured data extraction."""
        
        # Prompt for extracting table data
        self.table_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial document analysis assistant specialized in extracting tabular data from financial documents.
            Extract all tables from this financial document page. For each table:
            1. Identify the table title/caption
            2. Extract the table structure (headers and data)
            3. Determine the table position on the page
            
            Return the data in the following JSON format:
            {
              "tables": [
                {
                  "title": "string",
                  "headers": ["column1", "column2", ...],
                  "rows": [
                    ["cell1", "cell2", ...],
                    ...
                  ],
                  "page": number,
                  "position": {
                    "top": number,
                    "left": number,
                    "bottom": number,
                    "right": number
                  }
                }
              ]
            }
            
            Return ONLY valid JSON. Ensure the JSON is properly formatted and can be parsed."""),
            ("human", "Here is a page from a financial document:\n\n{page_content}")
        ])
        
        # Prompt for financial metrics extraction
        self.metrics_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial document analysis assistant specialized in extracting key financial metrics.
            Extract all important financial metrics from this document, such as:
            - Revenue figures
            - Profit/loss amounts
            - Growth percentages
            - Financial ratios
            - Cash flow figures
            
            For each metric, identify:
            1. The metric name
            2. The metric value
            3. The time period it applies to
            4. The page and paragraph/section where it appears
            
            Return the data in the following JSON format:
            {
              "metrics": [
                {
                  "name": "string",
                  "category": "Revenue|Expenses|Profitability|Liquidity|Growth|Other",
                  "value": number,
                  "unit": "string",
                  "period": "string",
                  "page": number,
                  "section": "string",
                  "text": "string" (the exact text where this metric appears)
                }
              ]
            }
            
            Return ONLY valid JSON. Ensure the JSON is properly formatted and can be parsed."""),
            ("human", "Here is a financial document:\n\n{document_content}")
        ])
        
        # Prompt for document type classification
        self.document_classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial document analysis assistant specialized in classifying financial documents.
            Classify this document as one of the following types:
            - balance_sheet
            - income_statement
            - cash_flow
            - notes
            - other
            
            Also identify the time periods covered in the document.
            
            Return the data in the following JSON format:
            {
              "document_type": "balance_sheet|income_statement|cash_flow|notes|other",
              "periods": ["period1", "period2", ...]
            }
            
            Return ONLY valid JSON. Ensure the JSON is properly formatted and can be parsed."""),
            ("human", "Here is a financial document:\n\n{document_content}")
        ])
        
        # Prompt for citation extraction
        self.citation_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial document analysis assistant specialized in identifying important information.
            Identify all important financial statements, facts, and figures in this document that would be useful for citation.
            For each important piece of information, extract:
            1. The exact text
            2. The page number
            3. The section or paragraph it appears in
            4. A unique ID for this citation
            
            Focus on extracting content that provides meaningful financial insights, such as:
            - Key financial metrics and their values
            - Important trends or changes
            - Significant financial events
            - Forward-looking statements
            - Risk factors
            
            Return the data in the following JSON format:
            {
              "citations": [
                {
                  "id": "string" (unique identifier),
                  "text": "string" (the exact text to cite),
                  "page": number,
                  "section": "string" (if available),
                  "importance": "high|medium|low" (indicating how crucial this information is)
                }
              ]
            }
            
            Return ONLY valid JSON. Ensure the JSON is properly formatted and can be parsed."""),
            ("human", "Here is a financial document:\n\n{document_content}")
        ])
    
    async def extract_tables(self, page_content: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Extract tables from a single PDF page.
        
        Args:
            page_content: The text content of the page
            page_number: The page number
            
        Returns:
            List of extracted tables
        """
        try:
            # Create the extraction chain
            chain = (
                self.table_extraction_prompt 
                | self.llm 
                | JsonOutputParser()
            )
            
            # Run the chain
            result = await chain.ainvoke({"page_content": page_content})
            
            # Add the page number to each table if not already included
            tables = result.get("tables", [])
            for table in tables:
                if "page" not in table:
                    table["page"] = page_number
            
            return tables
        except Exception as e:
            logger.error(f"Error extracting tables from page {page_number}: {str(e)}")
            return []
    
    async def extract_metrics(self, document_content: str) -> List[Dict[str, Any]]:
        """
        Extract financial metrics from document content.
        
        Args:
            document_content: The text content of the document
            
        Returns:
            List of extracted metrics
        """
        try:
            # Create the extraction chain
            chain = (
                self.metrics_extraction_prompt 
                | self.llm 
                | JsonOutputParser()
            )
            
            # Run the chain
            result = await chain.ainvoke({"document_content": document_content})
            
            return result.get("metrics", [])
        except Exception as e:
            logger.error(f"Error extracting metrics: {str(e)}")
            return []
    
    async def classify_document(self, document_content: str) -> Tuple[DocumentContentType, List[str]]:
        """
        Classify document type and extract time periods.
        
        Args:
            document_content: The text content of the document
            
        Returns:
            Tuple of document type and list of periods
        """
        try:
            # Create the classification chain
            chain = (
                self.document_classification_prompt 
                | self.llm 
                | JsonOutputParser()
            )
            
            # Run the chain
            result = await chain.ainvoke({"document_content": document_content})
            
            # Parse the result
            doc_type_str = result.get("document_type", "other")
            periods = result.get("periods", [])
            
            # Convert to DocumentContentType enum
            try:
                doc_type = DocumentContentType(doc_type_str)
            except ValueError:
                logger.warning(f"Invalid document type: {doc_type_str}. Using 'other' instead.")
                doc_type = DocumentContentType.OTHER
            
            return doc_type, periods
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            return DocumentContentType.OTHER, []
    
    async def extract_citations(self, document_content: str) -> List[Citation]:
        """
        Extract citations from document content.
        
        Args:
            document_content: The text content of the document
            
        Returns:
            List of Citation objects
        """
        try:
            # Create the citation extraction chain
            chain = (
                self.citation_extraction_prompt 
                | self.llm 
                | JsonOutputParser()
            )
            
            # Run the chain
            result = await chain.ainvoke({"document_content": document_content})
            
            # Convert to Citation objects
            citations_data = result.get("citations", [])
            citations = []
            
            for citation_data in citations_data:
                citation = Citation(
                    id=citation_data.get("id", f"citation_{len(citations)}"),
                    page=citation_data.get("page", 0),
                    text=citation_data.get("text", ""),
                    section=citation_data.get("section")
                )
                citations.append(citation)
            
            return citations
        except Exception as e:
            logger.error(f"Error extracting citations: {str(e)}")
            return []
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> Tuple[str, Dict[int, str]]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_data: Raw bytes of the PDF file
            
        Returns:
            Tuple of full document text and dictionary mapping page numbers to page text
        """
        try:
            # Open the PDF file
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from each page
            full_text = ""
            page_texts = {}
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                page_texts[i + 1] = page_text  # Page numbers are 1-indexed
                full_text += page_text + "\n\n"
            
            return full_text, page_texts
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return "", {}
    
    async def process_pdf(self, pdf_data: bytes, filename: str) -> Tuple[ProcessedDocument, List[Citation]]:
        """
        Process a PDF file using LangChain for enhanced extraction.
        
        Args:
            pdf_data: Raw bytes of the PDF file
            filename: Name of the PDF file
            
        Returns:
            Tuple of processed document and list of citations
        """
        logger.info(f"Processing PDF: {filename}")
        
        # Extract text from PDF
        full_text, page_texts = self.extract_text_from_pdf(pdf_data)
        
        if not full_text:
            logger.error(f"Failed to extract text from PDF: {filename}")
            raise ValueError("Could not extract text from PDF")
        
        # Process in parallel for efficiency
        import asyncio
        
        # Classify document and extract citations
        doc_type, periods = await self.classify_document(full_text)
        citations = await self.extract_citations(full_text)
        metrics = await self.extract_metrics(full_text)
        
        # Extract tables from each page
        tables = []
        for page_num, page_text in page_texts.items():
            page_tables = await self.extract_tables(page_text, page_num)
            tables.extend(page_tables)
        
        # Create document metadata
        metadata = {
            "filename": filename,
            "upload_timestamp": datetime.now().isoformat(),
            "file_size": len(pdf_data),
            "mime_type": "application/pdf",
            "user_id": "default-user",
            "citation_links": [citation.id for citation in citations]
        }
        
        # Prepare extracted data
        extracted_data = {
            "raw_text": full_text,
            "financial_data": self._organize_financial_data(metrics, periods),
            "tables": tables,
            "metrics": metrics
        }
        
        # Create processed document
        document = ProcessedDocument(
            metadata=metadata,
            content_type=doc_type,
            periods=periods,
            extracted_data=extracted_data,
            citations=citations,
            confidence_score=0.95,
            processing_status="completed"
        )
        
        logger.info(f"Successfully processed PDF: {filename}")
        return document, citations
    
    def _organize_financial_data(self, metrics: List[Dict[str, Any]], periods: List[str]) -> Dict[str, Any]:
        """
        Organize metrics into structured financial data.
        
        Args:
            metrics: List of extracted metrics
            periods: List of time periods
            
        Returns:
            Structured financial data
        """
        # Initialize structured data
        financial_data = {
            "revenue": {},
            "expenses": {},
            "profit": {},
            "assets": {},
            "liabilities": {},
            "equity": {}
        }
        
        # Organize metrics by category and period
        for metric in metrics:
            category = metric.get("category", "").lower()
            period = metric.get("period", "")
            value = metric.get("value", 0)
            name = metric.get("name", "").lower()
            
            # Skip metrics without a period
            if not period:
                continue
            
            # Map to appropriate category
            if category == "revenue" or "revenue" in name:
                financial_data["revenue"][period] = value
            elif category == "expenses" or "expense" in name or "cost" in name:
                financial_data["expenses"][period] = value
            elif category == "profitability" or "profit" in name or "income" in name:
                financial_data["profit"][period] = value
            elif "asset" in name:
                financial_data["assets"][period] = value
            elif "liabilit" in name or "debt" in name:
                financial_data["liabilities"][period] = value
            elif "equity" in name:
                financial_data["equity"][period] = value
        
        return financial_data