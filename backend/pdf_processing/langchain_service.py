import os
import logging
from typing import Dict, List, Any, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.config import RunnableConfig

from models.message import Message
from models.document import ProcessedDocument, Citation

logger = logging.getLogger(__name__)

class LangChainService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-latest")
        self.llm = ChatAnthropic(
            model=self.model,
            temperature=0.2,
            anthropic_api_key=api_key
        )
        
        # Initialize prompt templates
        self._init_prompt_templates()
    
    def _init_prompt_templates(self):
        """Initialize commonly used prompt templates."""
        # Financial Analysis System Prompt
        self.financial_analysis_system_prompt = """You are a financial document analysis assistant specialized in extracting insights from financial statements, reports, and related documents.
        Your goal is to provide accurate, detailed analysis with citations to the source material.
        When referencing information from documents, include citation markers in the format [Citation: id].
        Always maintain professional language and ensure all financial analyses are backed by data from the documents."""
        
        # Citation extraction prompt
        self.citation_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract citations from this financial document for relevant figures, statements, and tables.
                For each important piece of financial information, identify the exact text, page number, and section.
                Return the citations as a JSON array with the following fields for each citation:
                - id: A unique identifier for the citation
                - page: The page number where the citation appears
                - text: The exact text being cited
                - section: The section name or heading where the citation appears (if available)
                
                Focus on extracting citations for key financial metrics, trends, ratios, and important statements."""),
            ("human", "{document_text}")
        ])
        
        # Financial analysis prompt with citations
        self.financial_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", self.financial_analysis_system_prompt),
            ("human", """Please analyze the following financial information and respond to this question: {question}
            
            Document extracts with citations:
            {document_extracts}
            
            Previous conversation context:
            {conversation_history}
            
            Please be specific and cite your sources using the citation IDs provided in square brackets [Citation: id].
            """)
        ])
    
    async def extract_citations(self, document_text: str) -> List[Citation]:
        """
        Extract citations from document text using LangChain.
        
        Args:
            document_text: The text extracted from the document
            
        Returns:
            List of Citation objects
        """
        try:
            # Create extraction chain
            extraction_chain = (
                self.citation_extraction_prompt 
                | self.llm 
                | JsonOutputParser()
            )
            
            # Run the chain
            citations_data = await extraction_chain.ainvoke({"document_text": document_text})
            
            # Convert to Citation objects
            citations = []
            for i, citation_data in enumerate(citations_data):
                citation = Citation(
                    id=citation_data.get("id", f"citation_{i}"),
                    page=citation_data.get("page", 0),
                    text=citation_data.get("text", ""),
                    section=citation_data.get("section")
                )
                citations.append(citation)
            
            return citations
            
        except Exception as e:
            logger.error(f"Error extracting citations: {str(e)}")
            return []
    
    async def analyze_document_content(
        self, 
        question: str, 
        document_extracts: List[str], 
        conversation_history: List[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze document content and answer user questions with citations.
        
        Args:
            question: The user's question
            document_extracts: List of document extracts with citation information
            conversation_history: Previous conversation turns for context
            
        Returns:
            AI response with citation references
        """
        if conversation_history is None:
            conversation_history = []
        
        # Format document extracts with citations
        formatted_extracts = "\n\n".join(document_extracts)
        
        # Format conversation history
        formatted_history = ""
        if conversation_history:
            for i, message in enumerate(conversation_history):
                role = message.get("role", "user")
                content = message.get("content", "")
                formatted_history += f"{role.capitalize()}: {content}\n\n"
        
        # Create analysis chain
        analysis_chain = (
            self.financial_analysis_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        # Run the chain
        response = await analysis_chain.ainvoke({
            "question": question,
            "document_extracts": formatted_extracts,
            "conversation_history": formatted_history
        })
        
        return response
    
    async def generate_insights(self, financial_data: Dict[str, Any]) -> List[str]:
        """
        Generate financial insights from extracted data.
        
        Args:
            financial_data: Dictionary containing financial data
            
        Returns:
            List of insights
        """
        # Create a prompt for generating insights
        insights_prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate key financial insights based on the provided financial data.
                Focus on identifying trends, anomalies, and noteworthy patterns.
                Provide 3-5 concise, specific insights that would be valuable for financial decision-making."""),
            ("human", "Financial data: {financial_data}")
        ])
        
        # Create insights chain
        insights_chain = (
            insights_prompt 
            | self.llm 
            | RunnableLambda(lambda x: x.content.split("\n"))  # Split into separate insights
        )
        
        # Run the chain
        insights = await insights_chain.ainvoke({"financial_data": str(financial_data)})
        
        # Clean and filter insights
        cleaned_insights = [
            insight.strip().replace("- ", "") 
            for insight in insights 
            if insight.strip() and not insight.strip().startswith("Financial insights:")
        ]
        
        return cleaned_insights