import os
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple, TypedDict, Union, cast
from enum import Enum
import json
import re
import datetime
import base64
import string

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.message import Message, MessageRole
from models.citation import Citation, CitationType
from models.document import ProcessedDocument

logger = logging.getLogger(__name__)

# Define state types
class ConversationNodeType(str, Enum):
    """Types of nodes in the conversation graph."""
    ROUTER = "router"
    DOCUMENT_PROCESSOR = "document_processor"
    RESPONSE_GENERATOR = "response_generator"
    CITATION_PROCESSOR = "citation_processor"
    END = "end"

class AgentState(TypedDict):
    """State definition for conversation agent."""
    conversation_id: str
    messages: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    active_documents: List[str]
    current_message: Optional[Dict[str, Any]]
    current_response: Optional[Dict[str, Any]]
    citations_used: List[Dict[str, Any]]
    context: Dict[str, Any]

class LangGraphService:
    """Service to manage LangGraph workflows for financial analysis."""
    
    def __init__(self):
        """Initialize the LangGraph service."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        # Initialize with parameters set for the latest Claude model which has citation support built-in
        self.llm = ChatAnthropic(
            model=self.model,
            temperature=0.2,
            anthropic_api_key=api_key,
            max_tokens=4000,
            # Use model_kwargs to set the system message and any other model-specific parameters
            model_kwargs={
                "system": "You are a financial document analysis assistant that provides precise answers with citations. Always cite your sources when answering questions about documents."
            }
        )
        
        # Create memory saver for graph state persistence
        self.memory = MemorySaver()
        
        # Initialize conversation manager
        self.conversation_states = {}
        
        # Initialize system prompts
        self._init_system_prompts()
        
        # Setup conversation graph
        self.conversation_graph = self._create_conversation_graph()
        
        logger.info(f"LangGraphService initialized with model: {self.model}")
    
    def _init_system_prompts(self):
        """Initialize system prompts for different nodes."""
        self.router_prompt = """You are a router for a financial document analysis conversation.
        Your job is to determine what action to take next based on the user's message and conversation context.
        
        Choose one of the following options:
        - "document_processor": If the user is referring to documents or we need to process document context
        - "response_generator": If we have enough context to generate a response
        - "citation_processor": If we need to process citations before responding
        - "end": If the conversation should end
        
        Reply with just the action name, nothing else."""
        
        self.document_processor_prompt = """You are a document processing agent for financial analysis.
        Your job is to extract relevant information from documents based on the user's query.
        
        For each document mentioned in the query or relevant to the query:
        1. Identify key sections that address the user's question
        2. Extract important financial data, metrics, and insights
        3. Format the information in a structured way
        4. Include citation information so the main assistant can properly cite sources
        
        Be thorough but focus on relevance to the user's specific question."""
        
        self.response_generator_prompt = """You are a financial document analysis assistant specializing in answering questions about financial documents.
        
        When responding to the user:
        1. Provide clear, direct answers to their questions
        2. Base your responses on the document content provided
        3. Use specific financial data, metrics, and insights from the documents
        4. Always cite your sources using [Citation: ID] format when referencing specific information
        5. Be professional and precise in your analysis
        6. If you're uncertain about something, acknowledge it rather than guessing
        7. If the user asks about something not covered in the documents, politely explain that you don't have that information
        
        The user has uploaded financial documents which you can reference and cite."""
        
        self.citation_processor_prompt = """You are a citation processing agent for financial document analysis.
        Your job is to ensure all citations in a response are properly formatted and accurate.
        
        For each citation in the response:
        1. Verify the citation against the document content
        2. Ensure the citation format is consistent
        3. Check that citations are relevant to the user's query
        4. Remove any citations that cannot be verified
        
        The final response should maintain academic-level citation quality."""
    
    def _create_conversation_graph(self) -> StateGraph:
        """Create the conversation state graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("document_processor", self._document_processor_node)
        workflow.add_node("response_generator", self._response_generator_node)
        workflow.add_node("citation_processor", self._citation_processor_node)
        
        # Add edges for non-router nodes
        workflow.add_edge("document_processor", "response_generator")
        workflow.add_edge("response_generator", "citation_processor")
        workflow.add_edge("citation_processor", END)
        
        # Add conditional edges for router only
        workflow.add_conditional_edges(
            "router",
            self._route_conversation,
            {
                "document_processor": "document_processor",
                "response_generator": "response_generator",
                "citation_processor": "citation_processor",
                "end": END
            }
        )
        
        # Set entry point
        workflow.set_entry_point("router")
        
        return workflow.compile()
    
    def _router_node(self, state: AgentState) -> AgentState:
        """Route the conversation based on the current state."""
        messages = self._format_messages_for_llm(state, is_router=True)
        response = self.llm.invoke(messages)
        
        # Update state with router decision
        new_state = state.copy()
        new_state["context"] = {
            **new_state.get("context", {}),
            "router_decision": response.content.strip().lower()
        }
        
        return new_state
    
    def _route_conversation(self, state: AgentState) -> str:
        """Determine the next node based on router output."""
        router_decision = state.get("context", {}).get("router_decision", "")
        
        if "document_processor" in router_decision:
            return "document_processor"
        elif "response_generator" in router_decision:
            return "response_generator"
        elif "citation_processor" in router_decision:
            return "citation_processor"
        elif "end" in router_decision:
            return "end"
        else:
            # Default to response generator if no clear decision
            return "response_generator"
    
    def _document_processor_node(self, state: AgentState) -> AgentState:
        """Process documents in the conversation context."""
        # Get user message
        user_message = self._get_latest_user_message(state)
        if not user_message:
            return state
        
        # Prepare document context from state
        document_context = self._prepare_document_context(state)
        
        # Create prompt with document context
        messages = self._format_messages_for_llm(state, self.document_processor_prompt)
        
        # Add document context to system message
        if document_context and messages:
            # Add document context to first system message
            for i, msg in enumerate(messages):
                if isinstance(msg, SystemMessage):
                    messages[i] = SystemMessage(content=f"{msg.content}\n\n{document_context}")
                    break
        
        # Call LLM with document context to extract relevant information
        response = self.llm.invoke(messages)
        
        # Update state with processed document information
        new_state = state.copy()
        new_state["context"] = {
            **new_state.get("context", {}),
            "processed_documents": response.content
        }
        
        return new_state
    
    def _response_generator_node(self, state: AgentState) -> AgentState:
        """Generate a response based on processed documents and user query."""
        # Prepare messages with document context and processed documents
        messages = self._format_messages_for_llm(state, self.response_generator_prompt)
        
        # Add processed document information to system message if available
        processed_docs = state.get("context", {}).get("processed_documents")
        if processed_docs and messages:
            # Add processed document info to first system message
            for i, msg in enumerate(messages):
                if isinstance(msg, SystemMessage):
                    messages[i] = SystemMessage(content=f"{msg.content}\n\nDocument Analysis:\n{processed_docs}")
                    break
        
        # Call LLM to generate response
        response = self.llm.invoke(messages)
        
        # Extract citations from response
        response_content, citations_used = self._extract_citations_from_text(response.content, state["citations"])
        
        # Update state with response and citations
        new_state = state.copy()
        new_state["current_response"] = {
            "content": response_content,
            "role": "assistant"
        }
        new_state["citations_used"] = citations_used
        
        return new_state
    
    def _citation_processor_node(self, state: AgentState) -> AgentState:
        """Process and validate citations in the response."""
        if not state.get("current_response"):
            return state
        
        # Get the current response and citations
        response_content = state["current_response"]["content"]
        citations_used = state.get("citations_used", [])
        
        # Format message for citation processing
        citation_prompt = f"""
            {self.citation_processor_prompt}
            
            Original response: 
            {response_content}
            
            Citations used:
            {json.dumps(citations_used, indent=2)}
            
            Please verify and format these citations properly.
            """
        
        messages = [SystemMessage(content=citation_prompt)]
        
        # Call LLM to process citations
        response = self.llm.invoke(messages)
        
        # Update state with processed response
        new_state = state.copy()
        new_state["current_response"]["content"] = response.content
        
        # Add response to message history
        new_state["messages"].append({
            "role": "assistant",
            "content": response.content,
            "citations": citations_used
        })
        
        return new_state
    
    def _format_messages_for_llm(self, state: AgentState, system_prompt: Optional[str] = None, is_router: bool = False) -> List[BaseMessage]:
        """Format conversation messages for LLM input."""
        formatted_messages = []
        
        # Add system message
        if system_prompt:
            formatted_messages.append(SystemMessage(content=system_prompt))
        elif is_router:
            formatted_messages.append(SystemMessage(content=self.router_prompt))
        
        # Add conversation history
        for msg in state["messages"]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted_messages.append(AIMessage(content=content))
            elif role == "system":
                formatted_messages.append(SystemMessage(content=content))
        
        # Add current user message if it exists and not already in history
        if state.get("current_message") and state["current_message"] not in state["messages"]:
            current_msg = state["current_message"]
            formatted_messages.append(HumanMessage(content=current_msg["content"]))
        
        return formatted_messages
    
    def _prepare_document_context(self, state: AgentState) -> str:
        """Prepare document context for inclusion in LLM prompt."""
        if not state.get("documents"):
            return ""
        
        context_parts = ["Document Context:"]
        
        for i, doc in enumerate(state["documents"]):
            doc_title = doc.get("title", f"Document {i+1}")
            doc_type = doc.get("document_type", "unknown")
            doc_summary = doc.get("summary", "No summary available")
            
            context_parts.append(f"Document {i+1}: {doc_title}")
            context_parts.append(f"Type: {doc_type}")
            context_parts.append(f"Summary: {doc_summary}\n")
        
        if state.get("citations"):
            context_parts.append("Available Citations:")
            for i, citation in enumerate(state["citations"]):
                cite_id = citation.get("id", f"citation_{i}")
                cite_text = citation.get("text", "")[:100] + "..." if len(citation.get("text", "")) > 100 else citation.get("text", "")
                doc_title = citation.get("document_title", "Unknown document")
                
                context_parts.append(f"[Citation: {cite_id}] \"{cite_text}\" from {doc_title}")
        
        return "\n".join(context_parts)
    
    def _get_latest_user_message(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Get the latest user message from state."""
        # Check current message first
        if state.get("current_message") and state["current_message"].get("role") == "user":
            return state["current_message"]
        
        # Otherwise check message history in reverse
        for msg in reversed(state["messages"]):
            if msg.get("role") == "user":
                return msg
        
        return None
    
    def _extract_citations_from_text(self, text: str, available_citations: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract citation references from text and map them to actual citations.
        
        Args:
            text: The text to process
            available_citations: List of available citation objects
            
        Returns:
            Tuple of processed text and list of used citations
        """
        used_citations = []
        citation_map = {}
        
        # Create a map of citation IDs to citation objects
        for citation in available_citations:
            cid = citation.get("id", "")
            if cid:
                citation_map[cid] = citation
        
        # Look for citation patterns in text
        citation_pattern = r'\[Citation:\s*([^\]]+)\]'
        matches = re.finditer(citation_pattern, text)
        
        for match in matches:
            cite_id = match.group(1).strip()
            if cite_id in citation_map and citation_map[cite_id] not in used_citations:
                used_citations.append(citation_map[cite_id])
        
        return text, used_citations
    
    async def initialize_conversation(
        self, 
        conversation_id: str, 
        user_id: str, 
        document_ids: Optional[List[str]] = None,
        conversation_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize a new conversation state with LangGraph.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user
            document_ids: List of document IDs relevant to the conversation
            conversation_title: Optional title for the conversation
            
        Returns:
            Initial conversation state
        """
        try:
            logger.info(f"Initializing conversation {conversation_id} for user {user_id}")
            
            # Create initial state
            initial_state: AgentState = {
                "conversation_id": conversation_id,
                "messages": [],
                "documents": [],
                "citations": [],
                "active_documents": document_ids or [],
                "current_message": None,
                "current_response": None,
                "citations_used": [],
                "context": {
                    "user_id": user_id,
                    "title": conversation_title or f"Conversation {conversation_id[:8]}",
                    "documents_loaded": False
                }
            }
            
            # Store state in memory
            thread_id = f"conversation_{conversation_id}"
            config = self.conversation_graph.get_config()
            self.memory.save(thread_id, config.name, initial_state)
            
            return {
                "conversation_id": conversation_id,
                "status": "initialized",
                "state": initial_state
            }
            
        except Exception as e:
            logger.exception(f"Error initializing conversation: {e}")
            raise
    
    async def add_documents_to_conversation(
        self, 
        conversation_id: str, 
        documents: List[ProcessedDocument]
    ) -> Dict[str, Any]:
        """
        Add documents to conversation context.
        
        Args:
            conversation_id: ID of the conversation
            documents: List of processed documents to add
            
        Returns:
            Updated conversation state
        """
        try:
            logger.info(f"Adding {len(documents)} documents to conversation {conversation_id}")
            
            # Get current state
            thread_id = f"conversation_{conversation_id}"
            config = self.conversation_graph.get_config()
            state = cast(AgentState, self.memory.load(thread_id, config.name))
            
            if not state:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Extract document data and citations
            doc_data = []
            all_citations = []
            
            for doc in documents:
                # Extract basic document info
                doc_info = {
                    "id": str(doc.metadata.id),
                    "title": doc.metadata.filename,
                    "document_type": doc.content_type.value,
                    "summary": doc.extracted_data.get("raw_text", "")[:500] + "..." if len(doc.extracted_data.get("raw_text", "")) > 500 else doc.extracted_data.get("raw_text", ""),
                    "upload_timestamp": str(doc.metadata.upload_timestamp)
                }
                doc_data.append(doc_info)
                
                # Extract citations
                if doc.citations:
                    for citation in doc.citations:
                        citation_obj = {
                            "id": citation.id,
                            "text": citation.text,
                            "page": citation.page,
                            "document_id": str(doc.metadata.id),
                            "document_title": doc.metadata.filename,
                            "document_type": doc.content_type.value
                        }
                        all_citations.append(citation_obj)
            
            # Update state
            new_state = state.copy()
            new_state["documents"].extend(doc_data)
            new_state["citations"].extend(all_citations)
            new_state["context"]["documents_loaded"] = True
            
            # Add active document IDs
            for doc in documents:
                doc_id = str(doc.metadata.id)
                if doc_id not in new_state["active_documents"]:
                    new_state["active_documents"].append(doc_id)
            
            # Save updated state
            self.memory.save(thread_id, config.name, new_state)
            
            return {
                "conversation_id": conversation_id,
                "status": "documents_added",
                "document_count": len(documents),
                "citation_count": len(all_citations)
            }
            
        except Exception as e:
            logger.exception(f"Error adding documents to conversation: {e}")
            raise
    
    async def process_message(
        self, 
        conversation_id: str, 
        message_content: str,
        cited_document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the LangGraph conversation flow.
        
        Args:
            conversation_id: ID of the conversation
            message_content: User message content
            cited_document_ids: Optional list of document IDs explicitly cited by the user
            
        Returns:
            Processing result with AI response
        """
        try:
            logger.info(f"Processing message in conversation {conversation_id}")
            
            # Get current state
            thread_id = f"conversation_{conversation_id}"
            config = self.conversation_graph.get_config()
            state = cast(AgentState, self.memory.load(thread_id, config.name))
            
            if not state:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Create message object
            message = {
                "role": "user",
                "content": message_content,
                "cited_document_ids": cited_document_ids or []
            }
            
            # Update state with new message
            new_state = state.copy()
            new_state["messages"].append(message)
            new_state["current_message"] = message
            
            # If user explicitly cites documents, update active documents
            if cited_document_ids:
                for doc_id in cited_document_ids:
                    if doc_id not in new_state["active_documents"]:
                        new_state["active_documents"].append(doc_id)
            
            # Save updated state before processing
            self.memory.save(thread_id, config.name, new_state)
            
            # Process message through LangGraph
            for events in self.conversation_graph.stream(new_state, thread_id):
                # Process events if needed (for real-time updates)
                pass
            
            # Get final state after processing
            final_state = cast(AgentState, self.memory.load(thread_id, config.name))
            
            # Extract response
            if final_state.get("messages", []) and final_state["messages"][-1].get("role") == "assistant":
                # Get response from last message
                response = final_state["messages"][-1]
                assistant_message = {
                    "content": response.get("content", ""),
                    "role": "assistant",
                    "citations": response.get("citations", [])
                }
            else:
                # Fallback if no response was generated
                assistant_message = {
                    "content": "I'm sorry, I was unable to process your request.",
                    "role": "assistant",
                    "citations": []
                }
                
                # Add fallback message to state
                final_state["messages"].append(assistant_message)
                self.memory.save(thread_id, config.name, final_state)
            
            # Format citations for response
            citations_data = []
            for citation in assistant_message.get("citations", []):
                citation_obj = {
                    "id": citation.get("id", ""),
                    "text": citation.get("text", ""),
                    "document_id": citation.get("document_id", ""),
                    "document_title": citation.get("document_title", ""),
                    "page": citation.get("page", 0)
                }
                citations_data.append(citation_obj)
            
            return {
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4()),
                "content": assistant_message["content"],
                "role": assistant_message["role"],
                "citations": citations_data
            }
            
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            raise

    async def get_conversation_history(
        self, 
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        try:
            # Get current state
            thread_id = f"conversation_{conversation_id}"
            config = self.conversation_graph.get_config()
            state = cast(AgentState, self.memory.load(thread_id, config.name))
            
            if not state:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Get messages with limit
            messages = state.get("messages", [])[-limit:]
            
            # Format messages
            formatted_messages = []
            for msg in messages:
                message = {
                    "id": str(uuid.uuid4()),  # Generate ID since messages may not have one
                    "conversation_id": conversation_id,
                    "content": msg.get("content", ""),
                    "role": msg.get("role", "user"),
                    "citations": msg.get("citations", []),
                    "timestamp": msg.get("timestamp", "")
                }
                formatted_messages.append(message)
            
            return formatted_messages
            
        except Exception as e:
            logger.exception(f"Error getting conversation history: {e}")
            raise

    async def simple_document_qa(
        self,
        question: str,
        documents: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simple question-answering against document content without full graph execution.
        This is a lightweight wrapper around the response_generator node for basic QA.
        Uses Claude's citation feature to provide accurate references to document content.
        
        Args:
            question: The user's question
            documents: List of documents with their content
            conversation_history: Previous conversation messages (optional)
            
        Returns:
            Dictionary with AI response text and extracted citations
        """
        try:
            logger.info(f"Running simple_document_qa with {len(documents)} documents")
            
            # Prepare documents for citation - ensure they have citations enabled
            prepared_documents = []
            for doc in documents:
                # Convert document to the format expected by Claude API with citations enabled
                prepared_doc = {
                    "type": "document",
                    "title": doc.get("title", f"Document {doc.get('id', '')}"),
                    "citations": {"enabled": True}
                }
                
                # Handle different document types
                doc_type = doc.get("mime_type", "").lower()
                doc_content = doc.get("content", "")
                
                if "pdf" in doc_type or doc_type == "application/pdf":
                    # PDF document
                    if isinstance(doc_content, bytes):
                        prepared_doc["source"] = {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64.b64encode(doc_content).decode()
                        }
                    elif isinstance(doc_content, str):
                        # Check if it's already base64 encoded
                        if all(c in string.ascii_letters + string.digits + '+/=' for c in doc_content):
                            prepared_doc["source"] = {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": doc_content
                            }
                        else:
                            # Encode it as base64
                            prepared_doc["source"] = {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64.b64encode(doc_content.encode('utf-8')).decode()
                            }
                    else:
                        logger.warning(f"Skipping document with invalid content: {doc.get('id', '')}")
                        continue
                else:
                    # Plain text document
                    if isinstance(doc_content, bytes):
                        text_content = doc_content.decode('utf-8', errors='replace')
                    else:
                        text_content = str(doc_content)
                    
                    prepared_doc["source"] = {
                        "type": "text",
                        "media_type": "text/plain",
                        "data": text_content
                    }
                
                # Add document metadata as context if available (optional)
                if "metadata" in doc:
                    prepared_doc["context"] = json.dumps(doc["metadata"])
                
                prepared_documents.append(prepared_doc)
            
            # Prepare user message content with documents and question
            user_content = []
            
            # Add all prepared documents to the message content
            for prepared_doc in prepared_documents:
                user_content.append(prepared_doc)
            
            # Add the question as a text block
            user_content.append({"type": "text", "text": question})
            
            # Create messages in dictionary format expected by Claude
            messages = [
                {
                    "role": "system", 
                    "content": "You are a financial document analysis assistant that provides precise answers with citations. When answering questions: 1. Focus on information directly from the provided documents 2. Use citations to support your statements 3. Provide specific financial data from the documents where relevant 4. If a question cannot be answered from the documents, clearly state that 5. Be precise and factual in your analysis."
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                history_messages = []
                for msg in conversation_history:
                    role = msg.get("role", "").lower()
                    content = msg.get("content", "")
                    
                    # Map roles to Claude's expected format
                    if role in ["user", "human"]:
                        history_messages.append({"role": "user", "content": content})
                    elif role in ["assistant", "ai"]:
                        history_messages.append({"role": "assistant", "content": content})
                
                # Insert history before the current user message (if any)
                if history_messages:
                    messages = [messages[0]] + history_messages + [messages[-1]]
            
            # Call the API with the properly formatted messages
            logger.info(f"Calling Claude API with {len(messages)} messages")
            response = self.llm.invoke(messages)
            
            # Process citation data from response
            response_content = ""
            citations = []
            
            if hasattr(response, 'content'):
                # Check if content is a list (structured response with citations)
                if isinstance(response.content, list):
                    # Extract text from content blocks
                    response_content = self._process_response_with_citations(response.content)
                    # Extract citations from content blocks
                    citations = self._extract_citations_from_response(response)
                else:
                    # Handle simple string response
                    response_content = str(response.content)
            else:
                # Fallback for unexpected response format
                response_content = str(response)
            
            logger.info(f"Generated response with {len(citations)} citations")
            
            return {
                "content": response_content,
                "citations": citations
            }
            
        except Exception as e:
            logger.error(f"Error in simple_document_qa: {str(e)}", exc_info=True)
            return {
                "content": "I'm sorry, I couldn't process your question due to a technical issue.",
                "citations": []
            }
    
    def _process_response_with_citations(self, content_blocks) -> str:
        """
        Process response content blocks to extract text.
        
        Args:
            content_blocks: Content blocks from the response
            
        Returns:
            Extracted text from all content blocks
        """
        if not content_blocks:
            return ""
            
        # If content is not a list, just convert to string
        if not isinstance(content_blocks, list):
            return str(content_blocks)
            
        # Extract text from content blocks
        full_text = ""
        for block in content_blocks:
            if isinstance(block, dict) and 'text' in block:
                full_text += block['text']
            elif hasattr(block, 'text'):
                full_text += block.text
            elif isinstance(block, str):
                full_text += block
                
        return full_text
        
    def _extract_citations_from_response(self, response) -> List[Dict[str, Any]]:
        """
        Extract and process citations from Anthropic response.
        
        Args:
            response: The response from Anthropic API
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Check if response has content
        if not hasattr(response, 'content'):
            logger.warning("Response does not have 'content' attribute")
            return citations
            
        content = response.content
        logger.info(f"Response content type: {type(content)}")
        
        # Dump the raw response for debugging if it's not too large
        if isinstance(content, list) and len(content) < 10:
            try:
                logger.info(f"Raw response content: {str(content)[:500]}...")
            except:
                logger.info("Could not convert raw response to string")
        
        # If content is not a list, return empty citations
        if not isinstance(content, list):
            logger.warning(f"Content is not a list: {type(content)}")
            return citations
            
        logger.info(f"Content has {len(content)} blocks")
        
        # Process each content block
        for i, block in enumerate(content):
            logger.info(f"Processing content block {i}: {type(block)}")
            
            # Dump the raw block for debugging
            try:
                if isinstance(block, dict):
                    logger.info(f"Block {i} keys: {block.keys()}")
                    for key in block.keys():
                        logger.info(f"Block {i} - {key}: {type(block[key])}")
                        if key == 'citations' and block[key]:
                            logger.info(f"Block {i} has {len(block[key])} citations")
                            for j, citation in enumerate(block[key]):
                                logger.info(f"Citation {j} type: {type(citation)}")
                                if isinstance(citation, dict):
                                    logger.info(f"Citation {j} keys: {citation.keys()}")
                else:
                    logger.info(f"Block {i} attributes: {dir(block)[:100]}...")
            except Exception as e:
                logger.error(f"Error examining block {i}: {str(e)}")
            
            # Handle different ways citations might be present
            if isinstance(block, dict):
                # Check for citations in dict format
                if 'citations' in block and block['citations']:
                    logger.info(f"Found {len(block['citations'])} citations in block {i}")
                    for citation in block['citations']:
                        citation_dict = self._convert_citation_from_dict(citation)
                        if citation_dict and citation_dict not in citations:
                            citations.append(citation_dict)
                # Also check for text to log what we're finding
                if 'text' in block:
                    logger.info(f"Found text in block {i}: {block['text'][:50]}...")
            
            # Check for citations as an attribute
            elif hasattr(block, 'citations') and block.citations:
                logger.info(f"Found citations attribute in block {i}")
                for citation in block.citations:
                    citation_dict = self._convert_citation_to_dict(citation)
                    if citation_dict and citation_dict not in citations:
                        citations.append(citation_dict)
        
        logger.info(f"Extracted {len(citations)} citations from response")
        return citations
    
    def _convert_citation_from_dict(self, citation) -> Dict[str, Any]:
        """Convert citation from dictionary format."""
        try:
            citation_dict = {
                "type": citation.get("type", "unknown"),
                "cited_text": citation.get("cited_text", ""),
                "document_title": citation.get("document_title", "")
            }
            
            # Add type-specific fields
            if citation_dict["type"] == "char_location":
                citation_dict.update({
                    "start_char_index": citation.get("start_char_index", 0),
                    "end_char_index": citation.get("end_char_index", 0),
                    "document_index": citation.get("document_index", 0)
                })
            elif citation_dict["type"] == "page_location":
                citation_dict.update({
                    "start_page_number": citation.get("start_page_number", 1),
                    "end_page_number": citation.get("end_page_number", 1),
                    "document_index": citation.get("document_index", 0)
                })
            elif citation_dict["type"] == "content_block_location":
                citation_dict.update({
                    "start_block_index": citation.get("start_block_index", 0),
                    "end_block_index": citation.get("end_block_index", 0),
                    "document_index": citation.get("document_index", 0)
                })
            
            return citation_dict
        except Exception as e:
            logger.error(f"Error converting citation dictionary: {str(e)}")
            return {}
    
    def _convert_citation_to_dict(self, citation) -> Dict[str, Any]:
        """Convert Claude citation object to dictionary format for our app."""
        try:
            citation_dict = {
                "type": getattr(citation, "type", "unknown"),
                "cited_text": getattr(citation, "cited_text", ""),
                "document_title": getattr(citation, "document_title", "")
            }
            
            # Add type-specific fields
            if citation_dict["type"] == "char_location":
                citation_dict.update({
                    "start_char_index": getattr(citation, "start_char_index", 0),
                    "end_char_index": getattr(citation, "end_char_index", 0),
                    "document_index": getattr(citation, "document_index", 0)
                })
            elif citation_dict["type"] == "page_location":
                citation_dict.update({
                    "start_page_number": getattr(citation, "start_page_number", 1),
                    "end_page_number": getattr(citation, "end_page_number", 1),
                    "document_index": getattr(citation, "document_index", 0)
                })
            elif citation_dict["type"] == "content_block_location":
                citation_dict.update({
                    "start_block_index": getattr(citation, "start_block_index", 0),
                    "end_block_index": getattr(citation, "end_block_index", 0),
                    "document_index": getattr(citation, "document_index", 0)
                })
            
            return citation_dict
        except Exception as e:
            logger.error(f"Error converting citation: {str(e)}", exc_info=True)
            return {}
    
    async def transition_to_full_graph(
        self,
        conversation_id: str,
        current_state: AgentState
    ) -> str:
        """
        Transition a conversation from simple QA to full graph execution.
        This allows a conversation that started with simple_document_qa to later
        use the full power of the conversation graph for more complex needs.
        
        Args:
            conversation_id: ID of the conversation
            current_state: Current simple QA state
            
        Returns:
            Unique thread ID for the full graph execution
        """
        # Initialize the conversation with the full graph
        thread_id = str(uuid.uuid4())
        
        # Create config and metadata for the memory store
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create a checkpoint with the state data
        checkpoint = {
            "id": thread_id,  # Use thread_id as checkpoint id
            "state": current_state
        }
        
        # Create metadata for the checkpoint
        metadata = {
            "conversation_id": conversation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "transition_to_full_graph"
        }
        
        # Store the initial state with proper parameters
        self.memory.put(config, checkpoint, metadata)
        
        # Store the thread ID for later use
        self.conversation_states[conversation_id] = thread_id
        
        # Return the thread ID for future reference
        logger.info(f"Transitioned conversation {conversation_id} to full graph execution")
        return thread_id