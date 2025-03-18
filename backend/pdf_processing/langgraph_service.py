import os
import json
import gc
import logging
import psutil
import re
import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from enum import Enum

from anthropic import Anthropic
from langchain_core.messages import SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from utils.database import SessionLocal
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
        # Note: We don't use the LangChain wrapper's PDF support - we handle PDFs directly in the simple_document_qa method
        self.llm = ChatAnthropic(
            model=self.model,
            temperature=0.3,
            anthropic_api_key=api_key,
            max_tokens=4000,
            # Use model_kwargs to set the system message and other model-specific parameters
            model_kwargs={
                "system": "You are a financial document analysis assistant that provides precise answers with citations. Always cite your sources when answering questions about documents."
                # We don't need the PDF beta flag here since we handle PDFs directly in the simple_document_qa method
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
        # Also set workflow attribute for consistent naming
        self.workflow = self.conversation_graph
        
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
        """Process documents referenced in the conversation."""
        active_docs = state.get("active_documents", [])
        logger.info(f"Document processor node triggered with {len(active_docs)} active document(s)")
        logger.info(f"Active document IDs: {active_docs}")
        
        documents = state.get("documents", [])
        document_ids = [doc.get("id") for doc in documents]
        logger.info(f"Current document IDs in state: {document_ids}")
        
        # Check if we need to add documents to the state
        docs_to_add = [doc_id for doc_id in active_docs if doc_id not in document_ids]
        
        if not docs_to_add:
            logger.info("No new documents to add to state")
            return state
        
        logger.info(f"Documents to add: {docs_to_add}")
        
        # Get document content for each document ID
        for doc_id in docs_to_add:
            try:
                doc_content = self._get_document_content(doc_id)
                
                # Log document content status
                if doc_content:
                    content_length = len(doc_content)
                    preview = doc_content[:100] + "..." if content_length > 100 else doc_content
                    logger.info(f"Retrieved content for document {doc_id} ({content_length} chars)")
                    logger.info(f"Content preview: {preview}")
                else:
                    logger.warning(f"No content found for document {doc_id}")
                
                # Add document to state
                doc_data = {
                    "id": doc_id,
                    "raw_text": doc_content
                }
                documents.append(doc_data)
                logger.info(f"Added document {doc_id} to state")
            except Exception as e:
                logger.error(f"Error retrieving content for document {doc_id}: {str(e)}")
                logger.exception(e)
                # Add an empty document with an error flag
                documents.append({
                    "id": doc_id,
                    "raw_text": f"[Error retrieving document content: {str(e)}]",
                    "error": True
                })
        
        # Update the state with the new documents
        state["documents"] = documents
        logger.info(f"Updated state with {len(state['documents'])} documents")
        
        # Log memory usage after processing
        current_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        logger.info(f"Current memory usage after document processing: {current_memory:.2f} MB")
        
        return state
    
    async def _response_generator_node(
        self, 
        state: AgentState, 
        anthropic_api_key: Optional[str] = None, 
        claude_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response using Claude or Anthropic API."""
        try:
            # Monitor memory and track memory usage pattern throughout processing
            memory_usage = self._monitor_memory_usage("response_generator_start")
            self._optimize_memory_if_needed(memory_usage)
            
            # Prepare model name and API key
            model = claude_model or os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
            api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            
            if not api_key:
                logger.error("No Anthropic API key provided")
                return {"response": "Error: Missing Anthropic API key configuration."}
            
            logger.info(f"Generating response using model: {model}")
            
            # Get the latest user message
            latest_message = self._get_latest_user_message(state)
            
            if not latest_message:
                logger.warning("No latest user message found")
                return {"response": "I don't see a question to respond to."}
            
            query = latest_message.get("content", "")
            logger.info(f"User query: {query[:100]}...")
            
            # Prepare document context
            document_context = self._prepare_document_context(state)
            
            # Check if we have any document content
            if not document_context:
                logger.warning("No document context available for LLM messages")
                
                # Check if we should have documents
                active_docs = state.get("active_documents", [])
                if active_docs:
                    logger.warning(f"Expected documents ({active_docs}) but couldn't prepare context")
                    return {
                        "response": "I'm having trouble retrieving the document content. Please check that the document was properly uploaded and try again."
                    }
            else:
                doc_context_length = len(document_context)
                logger.info(f"Document context prepared: {doc_context_length} characters")
                
                # Log a preview of the document context
                preview_length = min(200, doc_context_length)
                if preview_length > 0:
                    logger.info(f"Document context preview: {document_context[:preview_length]}...")
            
            # Prepare conversation history
            messages = []
            
            # System message
            system_message = """You are a financial document assistant. Your role is to analyze financial documents and answer questions about them.
When referencing information from documents, always provide citations that include document ID and 
the relevant section or page if available.
Format your responses in well-structured markdown.
"""
            messages.append({"role": "system", "content": system_message})
            
            # Add document context as a system message if available
            if document_context:
                context_message = f"Here are the financial documents to reference:\n\n{document_context}"
                messages.append({"role": "system", "content": context_message})
            
            # Add conversation history
            chat_history = state.get("messages", [])
            for msg in chat_history[-10:]:  # Last 10 messages to stay within context limits
                role = "user" if msg.get("role") == "user" else "assistant"
                content = msg.get("content", "")
                
                # Skip empty messages
                if not content:
                    continue
                    
                messages.append({"role": role, "content": content})
            
            # Add the latest query from the user if not already included
            if messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": query})
                
            # Log the full prompt for debugging
            message_summary = "\n".join([f"{m['role']}: {m['content'][:50]}..." for m in messages])
            logger.info(f"Sending messages to Claude:\n{message_summary}")
            
            # Check memory before API call
            pre_api_memory = self._monitor_memory_usage("before_claude_api_call")
            self._optimize_memory_if_needed(pre_api_memory)
            
            # Set up the client
            client = Anthropic(api_key=api_key)
            
            # Prepare request parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.2,
            }
            
            # Add citation support if the model supports it (claude-3-5-sonnet models)
            if "claude-3-5-sonnet" in model:
                logger.info("Using model with citation support")
                params["citation_search"] = {
                    "enabled": True,
                    "annotations": {"citations": True}
                }
            
            # Generate the response from Claude
            logger.info("Sending request to Claude API")
            start_time = time.time()
            
            response = client.messages.create(**params)
            
            end_time = time.time()
            logger.info(f"Claude API response received in {end_time - start_time:.2f} seconds")
            
            # Process the response
            ai_response = response.content[0].text
            logger.info(f"Response length: {len(ai_response)} characters")
            logger.info(f"Response preview: {ai_response[:200]}...")
            
            # Extract and format citations
            citations = self._process_citations_from_response(response, ai_response)
            
            # Monitor memory after processing
            post_memory = self._monitor_memory_usage("response_generator_end")
            self._optimize_memory_if_needed(post_memory)
            
            # Return the response with citations
            return {
                "response": ai_response,
                "citations": citations
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.exception(e)
            return {
                "response": "I encountered an error while processing your request. Please try again or contact support if the issue persists.",
                "error": str(e)
            }
    
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
    
    def _format_messages_for_llm(self, state: AgentState, system_prompt: Optional[str] = None, is_router: bool = False) -> List[Dict[str, Any]]:
        """Format messages for LLM with appropriate system prompt and document context."""
        # Use the router prompt if is_router is True
        if is_router:
            system_prompt = self.router_prompt
        elif system_prompt is None:
            system_prompt = self.response_generator_prompt
            
        # Get document context
        document_context = ""
        if "document_context" in state and state["document_context"]:
            # Use the cached document context if available
            document_context = state["document_context"]
            logger.info("Using cached document context from state")
        else:
            # Generate it fresh if not cached
            document_context = self._prepare_document_context(state)
            logger.info(f"Generated fresh document context (length: {len(document_context)})")
        
        # Log if document context is available
        if document_context:
            logger.info(f"Document context available for LLM messages (length: {len(document_context)})")
        else:
            logger.warning("No document context available for LLM messages")
        
        # Enhance system prompt with document context
        enhanced_system_prompt = system_prompt
        if document_context:
            # Create a system prompt that clearly separates document content from instructions
            enhanced_system_prompt = f"""
{system_prompt}

YOU HAVE ACCESS TO THE FOLLOWING DOCUMENTS:
-------------------------------------------------
{document_context}
-------------------------------------------------

IMPORTANT INSTRUCTIONS:
1. These documents contain financial information that you MUST use to answer the user's questions.
2. Always reference the specific document and its content in your responses.
3. If you can't find relevant information in the documents, acknowledge this limitation.
4. If no document is available, inform the user that you need a document uploaded to answer their question.
"""
            logger.info("Enhanced system prompt with document context")
        
        # Format messages for the LLM
        messages = []
        
        # Add system message with enhanced prompt
        messages.append({
            "role": "system",
            "content": enhanced_system_prompt
        })
        
        # Add conversation history
        for msg in state.get("messages", []):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Skip system messages in history
            if role != "system":
                messages.append({
                    "role": role,
                    "content": content
                })
        
        # Add current message if present
        if state.get("current_message"):
            current_msg = state["current_message"]
            messages.append({
                "role": current_msg.get("role", "user"),
                "content": current_msg.get("content", "")
            })
        
        # Log message count and message roles
        message_roles = [msg["role"] for msg in messages]
        logger.info(f"Formatted {len(messages)} messages for LLM with roles: {message_roles}")
        
        # Check if document context is actually included in the system prompt
        if document_context and "DOCUMENTS" in messages[0]["content"]:
            preview = messages[0]["content"][:100] + "..." if len(messages[0]["content"]) > 100 else messages[0]["content"]
            logger.info(f"System prompt with document context preview: {preview}")
        
        return messages
    
    def _prepare_document_context(self, state: AgentState) -> str:
        """Prepare document context for inclusion in LLM prompt."""
        if not state.get("documents"):
            logger.warning("No documents available in state for document context preparation")
            logger.warning(f"State keys: {list(state.keys())}")
            logger.warning(f"Active documents: {state.get('active_documents', [])}")
            return ""
        
        document_context = []
        logger.info(f"Preparing document context from {len(state.get('documents', []))} documents")
        
        for i, doc in enumerate(state.get("documents", [])):
            doc_id = doc.get("id", f"doc_{i}")
            title = doc.get("title", "") or doc.get("name", f"Document {i+1}")
            
            logger.info(f"Processing document {i+1}: ID={doc_id}, Title={title}")
            logger.info(f"Document keys: {list(doc.keys())}")
            
            # Check for raw_text in different possible locations
            raw_text = ""
            content_source = "none"
            
            # Try to get raw_text directly from the document
            if "raw_text" in doc and doc.get("raw_text"):
                raw_text = doc.get("raw_text")
                content_source = "raw_text"
                logger.info(f"Found content in raw_text field for document {doc_id} ({len(raw_text)} characters)")
            
            # If no raw_text directly, try extracted_data
            elif "extracted_data" in doc and doc.get("extracted_data"):
                logger.info(f"Extracted data keys: {list(doc.get('extracted_data', {}).keys())}")
                
                if "raw_text" in doc.get("extracted_data", {}):
                    raw_text = doc.get("extracted_data").get("raw_text")
                    content_source = "extracted_data.raw_text"
                    logger.info(f"Found content in extracted_data.raw_text for document {doc_id} ({len(raw_text)} characters)")
                
                # For chunked large documents, use a summarized version
                elif "text_chunks" in doc.get("extracted_data") and doc.get("extracted_data").get("text_chunks"):
                    chunks = doc.get("extracted_data").get("text_chunks")
                    content_source = "extracted_data.text_chunks"
                    # Use first chunk, middle chunk, and last chunk to represent the document
                    if len(chunks) <= 3:
                        raw_text = "\n\n".join(chunks)
                    else:
                        raw_text = f"{chunks[0]}\n\n[...Document continues...]\n\n{chunks[len(chunks)//2]}\n\n[...Document continues...]\n\n{chunks[-1]}"
                    logger.info(f"Using chunked text for large document {doc_id} ({len(raw_text)} characters from {len(chunks)} chunks)")
            
            # If we still don't have content, check other common fields
            if not raw_text and "content" in doc and doc.get("content"):
                raw_text = doc.get("content")
                content_source = "content"
                logger.info(f"Found content in content field for document {doc_id} ({len(raw_text)} characters)")
                
            if not raw_text and "text" in doc and doc.get("text"):
                raw_text = doc.get("text")
                content_source = "text"
                logger.info(f"Found content in text field for document {doc_id} ({len(raw_text)} characters)")
            
            if raw_text:
                # Truncate very long documents to prevent context overflow
                MAX_DOC_LENGTH = 10000  # Characters per document
                truncated = False
                
                if len(raw_text) > MAX_DOC_LENGTH:
                    original_length = len(raw_text)
                    raw_text = raw_text[:MAX_DOC_LENGTH] + f"\n\n[Document truncated due to length. Original size: {original_length} characters]"
                    truncated = True
                    logger.info(f"Truncated document {doc_id} from {original_length} to {MAX_DOC_LENGTH} chars for context")
                
                document_context.append(
                    f"Document: {title}\n"
                    f"ID: {doc_id}\n"
                    f"Content: {raw_text}\n"
                    f"------ END OF DOCUMENT ------\n"
                )
                logger.info(f"Added document {doc_id} to context (source: {content_source}, truncated: {truncated})")
            else:
                logger.warning(f"No content found for document {doc_id} in any expected field")
                # Add placeholder for document with no content
                document_context.append(
                    f"Document: {title}\n"
                    f"ID: {doc_id}\n"
                    f"Content: [No content available]\n"
                    f"------ END OF DOCUMENT ------\n"
                )
        
        final_context = "\n\n".join(document_context)
        logger.info(f"Final document context prepared: {len(final_context)} characters, {len(document_context)} documents")
        
        if not final_context:
            logger.warning("Document context preparation resulted in EMPTY context!")
        
        return final_context
    
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
            
            # Store state in conversation_states directly
            thread_id = f"conversation_{conversation_id}"
            self.conversation_states[thread_id] = initial_state
            
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
            
            # Get current state from conversation_states dictionary
            thread_id = f"conversation_{conversation_id}"
            state = self.conversation_states.get(thread_id)
            
            if not state:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Extract document data and citations
            doc_data = []
            all_citations = []
            
            for doc in documents:
                # Extract document content from extracted_data if available
                raw_text = ""
                if hasattr(doc, "extracted_data") and doc.extracted_data:
                    if "raw_text" in doc.extracted_data:
                        raw_text = doc.extracted_data["raw_text"]
                        logger.info(f"Using raw_text for document {doc.metadata.id} ({len(raw_text)} characters)")
                
                # Create truncated summary for UI display purposes
                summary = raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
                
                # Extract basic document info
                doc_info = {
                    "id": str(doc.metadata.id),
                    "title": doc.metadata.filename,
                    "document_type": doc.content_type.value,
                    "summary": summary,
                    "raw_text": raw_text,  # Include full raw text for LLM context
                    "upload_timestamp": str(doc.metadata.upload_timestamp)
                }
                
                # Add extracted_data as well if it exists
                if hasattr(doc, "extracted_data") and doc.extracted_data:
                    doc_info["extracted_data"] = doc.extracted_data
                
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
            self.conversation_states[thread_id] = new_state
            
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
        message_text: str,
        user_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a message within a conversation.
        
        Args:
            conversation_id: ID of the conversation
            message_text: Text of the message to process
            user_id: Optional ID of the user sending the message
            message_id: Optional ID of the message
            
        Returns:
            Result containing the response, citations, and status
        """
        try:
            # Initialize conversation state if it doesn't exist
            if conversation_id not in self.conversation_states:
                logger.info(f"Initializing new conversation state for {conversation_id}")
                self.conversation_states[conversation_id] = self._create_empty_state()
                self.conversation_states[conversation_id]["conversation_id"] = conversation_id
            
            # Get the conversation state
            state = self.conversation_states[conversation_id]
            
            # Add user message to conversation
            if "messages" not in state:
                state["messages"] = []
                
            user_message = {
                "id": message_id or str(uuid.uuid4()),
                "role": "user",
                "content": message_text,
                "created_at": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            state["messages"].append(user_message)
            state["current_message"] = user_message
            
            # Run the message through our workflow graph
            logger.info(f"Running message through workflow for conversation {conversation_id}")
            try:
                # Execute the graph with the current state
                result = await self.workflow.ainvoke(state)
                
                if not result:
                    logger.error("No result returned from workflow")
                    raise ValueError("No result returned from workflow")
                
                # Extract the AI response from the result
                if 'messages' in result and len(result['messages']) > 0:
                    # Get the latest AI message
                    ai_messages = [msg for msg in result['messages'] if msg['role'] == 'assistant']
                    
                    if ai_messages:
                        latest_ai_message = ai_messages[-1]
                        response_content = latest_ai_message.get('content', '')
                        
                        # Extract citations if available
                        citations = []
                        if latest_ai_message.get('citations'):
                            citations = latest_ai_message['citations']
                            logger.info(f"Found {len(citations)} citations in response")
                        
                        # Update the stored state with the new state including AI response
                        self.conversation_states[conversation_id] = result
                        
                        # Return the response and any citations
                        return {
                            "response": response_content,
                            "citations": citations,
                            "status": "success"
                        }
                    else:
                        logger.warning("No assistant message found in result")
                        return {
                            "response": "I couldn't generate a response at this time.",
                            "citations": [],
                            "status": "error"
                        }
                else:
                    logger.warning("No messages found in result")
                    return {
                        "response": "I couldn't generate a response at this time.",
                        "citations": [],
                        "status": "error"
                    }
                
            except Exception as e:
                logger.error(f"Error in workflow execution: {str(e)}", exc_info=True)
                return {
                    "response": f"An error occurred while processing your message: {str(e)}",
                    "citations": [],
                    "status": "error"
                }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "response": f"An error occurred while processing your message: {str(e)}",
                "citations": [],
                "status": "error"
            }
    
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
            
            # Check for empty document list
            if not documents:
                logger.warning("No documents provided to simple_document_qa")
                return {
                    "content": "I don't have any documents to analyze. Please upload a document first.",
                    "citations": []
                }
            
            # Detailed document diagnostic logging
            logger.info(f"===== Begin document diagnostic information for {len(documents)} documents =====")
            for i, doc in enumerate(documents):
                # Basic document metadata
                doc_id = doc.get('id', f'doc_{i}')
                doc_type = doc.get("document_type", doc.get("mime_type", "unknown"))
                doc_title = doc.get("title", doc.get("filename", f"Untitled document {i}"))
                
                # Content availability checks
                has_raw_text = 'raw_text' in doc and bool(doc.get('raw_text'))
                raw_text_len = len(doc.get('raw_text', '')) if has_raw_text else 0
                
                has_content = 'content' in doc and bool(doc.get('content'))
                content_type = type(doc.get('content')).__name__ if has_content else "None"
                content_len = len(doc.get('content', '')) if has_content and isinstance(doc.get('content'), (str, bytes)) else 0
                
                has_extracted_data = 'extracted_data' in doc and bool(doc.get('extracted_data'))
                has_text = 'text' in doc and bool(doc.get('text'))
                
                # Log comprehensive document info
                logger.info(f"Document {i+1}/{len(documents)} - ID: {doc_id}, Title: {doc_title}, Type: {doc_type}")
                logger.info(f"Content availability: raw_text={has_raw_text}({raw_text_len} chars), content={has_content}({content_type}, {content_len}), extracted_data={has_extracted_data}, text={has_text}")
            
            logger.info(f"===== End document diagnostic information =====")
            
            # Prepare documents for Claude API
            user_content = []
            
            # Import the repository to get document binary content if needed
            try:
                from repositories.document_repository import DocumentRepository
                from utils.database import get_db
                
                # Create a repository instance to fetch binary data if needed
                repository = None
                async for db in get_db():
                    repository = DocumentRepository(db)
                    break  # Just get the first one
                
                if repository:
                    logger.info("Successfully created document repository for binary access")
                else:
                    logger.warning("Could not create document repository - no database connection available")
            except Exception as repo_error:
                logger.warning(f"Could not create document repository for binary access: {str(repo_error)}")
                repository = None

            # Process each document
            for i, doc in enumerate(documents):
                doc_id = doc.get('id', f'doc_{i}')
                doc_title = doc.get("title", doc.get("filename", f"Document {doc_id}"))
                
                # Check if this is a PDF document
                is_pdf = False
                if doc.get("mime_type") == "application/pdf" or doc.get("document_type") == "application/pdf" or (doc.get("filename", "").lower().endswith(".pdf")):
                    is_pdf = True

                # For PDFs, try to get binary content
                if is_pdf:
                    pdf_binary = None
                    
                    # First check if binary content is already in the document
                    if "content" in doc and isinstance(doc.get("content"), bytes):
                        pdf_binary = doc.get("content")
                        logger.info(f"Using existing binary content for PDF document {doc_id}: {len(pdf_binary)} bytes")
                    
                    # If not, try to get it from repository
                    elif repository:
                        try:
                            pdf_content = await repository.get_document_content(doc_id)
                            if pdf_content and "content" in pdf_content and isinstance(pdf_content["content"], bytes):
                                pdf_binary = pdf_content["content"]
                                logger.info(f"Retrieved binary PDF data ({len(pdf_binary)} bytes) for document {doc_id}")
                        except Exception as e:
                            logger.warning(f"Could not retrieve binary data for document {doc_id}: {str(e)}")
                    
                    # If we have binary PDF data, encode it as base64 for Claude
                    if pdf_binary:
                        try:
                            import base64
                            base64_data = base64.b64encode(pdf_binary).decode('utf-8')
                            
                            # Create the document block in Claude's format
                            pdf_doc = {
                                "type": "document",
                                "title": doc_title,
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": base64_data
                                }
                            }
                            
                            user_content.append(pdf_doc)
                            logger.info(f"Added PDF document {doc_id} with base64 encoding to content")
                            continue
                        except Exception as e:
                            logger.error(f"Error encoding PDF as base64: {str(e)}")
                
                # For non-PDF documents or if PDF processing failed, fallback to text
                # Try to find content in various possible locations
                doc_content = None
                
                # Look for content in various fields with fallbacks
                if "raw_text" in doc and doc["raw_text"]:
                    doc_content = doc["raw_text"]
                    logger.info(f"Using raw_text field for document {doc_id}")
                elif "content" in doc and doc["content"] and isinstance(doc["content"], str):
                    doc_content = doc["content"]
                    logger.info(f"Using content field for document {doc_id}")
                elif "extracted_data" in doc and isinstance(doc["extracted_data"], dict) and "raw_text" in doc["extracted_data"]:
                    doc_content = doc["extracted_data"]["raw_text"]
                    logger.info(f"Using extracted_data.raw_text for document {doc_id}")
                elif "text" in doc and doc["text"]:
                    doc_content = doc["text"]
                    logger.info(f"Using text field for document {doc_id}")
                
                # If content was found, create a document block for Claude
                if doc_content and len(str(doc_content).strip()) > 0:
                    # Ensure content is a string
                    if not isinstance(doc_content, str):
                        try:
                            doc_content = str(doc_content)
                        except Exception as e:
                            logger.warning(f"Could not convert content to string: {e}")
                            continue
                    
                    # Create the document block
                    text_doc = {
                        "type": "document",
                        "title": doc_title,
                        "source": {
                            "type": "text",
                            "media_type": "text/plain",
                            "data": doc_content
                        }
                    }
                    
                    user_content.append(text_doc)
                    logger.info(f"Added text document {doc_id} with {len(doc_content)} chars to content")
                else:
                    logger.warning(f"Could not find any content for document {doc_id}, skipping")
            
            # If no documents were prepared, return an error message
            if not any(item.get("type") == "document" for item in user_content):
                logger.warning("No documents were prepared for the Claude API")
                return {
                    "content": "I couldn't process the document content. Please ensure the documents were properly uploaded and contain readable text.",
                    "citations": []
                }
            
            # Add the question as a text block
            user_content.append({"type": "text", "text": question})
            
            # Create the system prompt
            system_message = "You are a financial document analysis assistant that provides precise answers with citations. When answering questions: 1. Focus on information directly from the provided documents 2. Use citations to support your statements 3. Provide specific financial data from the documents where relevant 4. If a question cannot be answered from the documents, clearly state that 5. Be precise and factual in your analysis."
            
            # Format messages for Anthropic API
            anthropic_messages = []
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "").lower()
                    content = msg.get("content", "")
                    
                    # Map roles to Claude's expected format
                    if role in ["user", "human"]:
                        anthropic_messages.append({"role": "user", "content": content})
                    elif role in ["assistant", "ai"]:
                        anthropic_messages.append({"role": "assistant", "content": content})
            
            # Add current message with documents and question
            anthropic_messages.append({
                "role": "user",
                "content": user_content
            })
            
            # Log the API call
            logger.info(f"Calling Anthropic API with {len(anthropic_messages)} messages and {len([item for item in user_content if item.get('type') == 'document'])} documents")
            
            # Use a model that supports citations
            model_name = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            logger.info(f"Using Claude model: {model_name}")
            
            # Create the Anthropic client
            from anthropic import Anthropic
            anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            
            # Call the API
            try:
                response = anthropic_client.messages.create(
                    model=model_name,
                    system=system_message,
                    messages=anthropic_messages,
                    max_tokens=4000
                )
                
                # Process the response
                ai_response = response.content[0].text
                logger.info(f"Claude API response received: {len(ai_response)} characters")
                
                # Extract and format citations
                citations = self._process_citations_from_response(response, ai_response)
                
                return {
                    "content": ai_response,
                    "citations": citations
                }
            except Exception as api_error:
                logger.error(f"Error calling Claude API: {str(api_error)}", exc_info=True)
                return {
                    "content": f"An error occurred while processing your request: {str(api_error)}",
                    "citations": []
                }
        except Exception as e:
            logger.error(f"Error in simple_document_qa: {str(e)}", exc_info=True)
            return {
                "content": f"An error occurred while processing your request: {str(e)}",
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
    
    def _extract_citations_from_response(self, response):
        """Extract citation data from Claude API response."""
        citations = []
        
        if hasattr(response, 'content') and isinstance(response.content, list):
            for block in response.content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    # Extract any citation annotations
                    annotations = block.get('annotations', [])
                    for annotation in annotations:
                        if annotation.get('type') == 'citation':
                            # Process citation
                            citation_data = annotation.get('citation', {})
                            
                            # Determine citation type and extract appropriate fields
                            if 'document' in citation_data:
                                doc_idx = citation_data.get('document', {}).get('index', 0)
                                doc_id = f"doc_{doc_idx}"
                                text = citation_data.get('text', '')
                                
                                citations.append({
                                    "document_index": doc_idx,
                                    "document_id": doc_id,
                                    "text": text
                                })
        
        return citations
    
    def _process_citations_from_response(self, response, ai_response: str) -> List[Dict[str, Any]]:
        """
        Process and extract citations from the Claude API response.
        Returns a list of citation objects in a standardized format.
        
        Args:
            response: The direct Anthropic API response
            ai_response: The text content from the response
            
        Returns:
            List of standardized citation dictionaries
        """
        try:
            # Initialize empty list for citations
            citations = []
            
            # Check if response has content blocks
            if hasattr(response, 'content') and response.content:
                # Process each content block
                for block in response.content:
                    # Check for citations directly in the content block
                    if hasattr(block, 'citations') and block.citations:
                        logger.info(f"Found {len(block.citations)} citations in content block")
                        
                        for citation in block.citations:
                            # Process each citation
                            citation_dict = self._convert_citation_to_dict(citation)
                            if citation_dict:
                                citations.append(citation_dict)
                    
                    # Check for citations in annotations
                    if hasattr(block, 'annotations') and block.annotations:
                        logger.info(f"Found {len(block.annotations)} annotations in content block")
                        
                        for annotation in block.annotations:
                            if hasattr(annotation, 'citations') and annotation.citations:
                                for citation in annotation.citations:
                                    citation_dict = self._convert_citation_to_dict(citation)
                                    if citation_dict:
                                        citations.append(citation_dict)
            
            # Check for top-level citations (older API format)
            if hasattr(response, 'citations') and response.citations:
                logger.info(f"Found {len(response.citations)} top-level citations in response")
                
                for citation in response.citations:
                    citation_dict = self._convert_citation_to_dict(citation)
                    if citation_dict:
                        citations.append(citation_dict)
            
            # Check for top-level annotations (older API format)
            if hasattr(response, 'annotations') and response.annotations:
                logger.info(f"Found {len(response.annotations)} top-level annotations in response")
                
                for annotation in response.annotations:
                    if hasattr(annotation, 'citations') and annotation.citations:
                        for citation in annotation.citations:
                            citation_dict = self._convert_citation_to_dict(citation)
                            if citation_dict:
                                citations.append(citation_dict)
            
            # Log citation count
            if citations:
                logger.info(f"Extracted {len(citations)} citations from the Claude API response")
                
                # Log first citation as an example
                if len(citations) > 0:
                    logger.info(f"Example citation: {citations[0]}")
            else:
                logger.info("No citations found in the Claude API response")
            
            return citations
            
        except Exception as e:
            logger.error(f"Error processing citations from response: {str(e)}", exc_info=True)
            return []
    
    def _convert_citation_to_dict(self, citation) -> Dict[str, Any]:
        """
        Convert a citation object from the Anthropic API to our standardized dictionary format.
        
        Args:
            citation: Citation object from Anthropic API
            
        Returns:
            Standardized citation dictionary
        """
        try:
            # Determine citation type
            citation_type = getattr(citation, 'type', None)
            if not citation_type and hasattr(citation, 'page'):
                citation_type = "page_location"
            elif not citation_type and (hasattr(citation, 'start_index') or hasattr(citation, 'start_char_index')):
                citation_type = "char_location"
            else:
                citation_type = "standard"
            
            # Extract document information
            document_id = None
            if hasattr(citation, 'document'):
                # Extract ID from document object
                document_id = getattr(citation.document, 'id', None)
                if document_id is None and hasattr(citation.document, 'index'):
                    document_id = f"doc_{citation.document.index}"
            
            # Extract quoted text
            quoted_text = ""
            if hasattr(citation, 'text'):
                quoted_text = citation.text
            elif hasattr(citation, 'quote'):
                quoted_text = citation.quote
            
            # Base citation information
            citation_dict = {
                "type": citation_type,
                "cited_text": quoted_text,
                "document_id": document_id
            }
            
            # Add type-specific fields
            if citation_type == "page_location" and hasattr(citation, 'page'):
                # For PDF page citations
                start_page = getattr(citation.page, 'start', 1)
                end_page = getattr(citation.page, 'end', start_page)
                
                citation_dict.update({
                    "start_page_number": start_page,
                    "end_page_number": end_page
                })
            elif citation_type == "char_location":
                # For character-based citations
                start_index = getattr(citation, 'start_index', 
                                     getattr(citation, 'start_char_index', 0))
                end_index = getattr(citation, 'end_index',
                                   getattr(citation, 'end_char_index', 0))
                
                citation_dict.update({
                    "start_char_index": start_index,
                    "end_char_index": end_index
                })
            
            return citation_dict
        except Exception as e:
            logger.error(f"Error converting citation to dictionary: {str(e)}", exc_info=True)
            return {"type": "unknown", "cited_text": str(citation), "error": str(e)}
    
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
            "timestamp": datetime.now().isoformat(),
            "type": "transition_to_full_graph"
        }
        
        # Store the initial state with proper parameters
        self.memory.put(config, checkpoint, metadata)
        
        # Store the thread ID for later use
        self.conversation_states[conversation_id] = thread_id
        
        # Return the thread ID for future reference
        logger.info(f"Transitioned conversation {conversation_id} to full graph execution")
        return thread_id
    
    def _monitor_memory_usage(self, operation: str = "general") -> float:
        """
        Monitor and log memory usage at various points in document processing.
        Returns current memory usage in MB.
        """
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"Memory usage ({operation}): {memory_mb:.2f} MB")
        return memory_mb
        
    def _optimize_memory_if_needed(self, current_memory_mb: float, threshold_mb: float = 1000) -> None:
        """
        Perform memory optimization if current usage exceeds threshold.
        
        Args:
            current_memory_mb: Current memory usage in MB
            threshold_mb: Threshold in MB above which optimization will be performed
        """
        if current_memory_mb > threshold_mb:
            logger.warning(f"Memory usage ({current_memory_mb:.2f} MB) exceeds threshold ({threshold_mb} MB). Running garbage collection.")
            
            # Get memory before optimization
            before_gc = self._monitor_memory_usage("before_gc")
            
            # Force garbage collection
            gc.collect()
            
            # Get memory after optimization
            after_gc = self._monitor_memory_usage("after_gc")
            
            # Log memory savings
            memory_freed = before_gc - after_gc
            logger.info(f"Garbage collection freed {memory_freed:.2f} MB of memory")
    
    def _create_empty_state(self) -> AgentState:
        """
        Create an empty conversation state.
        
        Returns:
            Empty conversation state
        """
        return {
            "conversation_id": "",
            "messages": [],
            "documents": [],
            "citations": [],
            "active_documents": [],
            "current_message": None,
            "current_response": None,
            "citations_used": [],
            "context": {}
        }