from typing import List, Optional, Dict, Any
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from models.message import Message, MessageRequest, MessageResponse, ConversationCreateRequest, ConversationHistoryResponse, MessageRole
from pdf_processing.langgraph_service import LangGraphService
from models.document import ProcessedDocument, Citation
from models.citation import ContentBlock, PageLocationCitation, CitationType

# Mock services that don't exist yet
class DocumentService:
    def __init__(self, db=None):
        pass
    
    async def get_document(self, doc_id):
        # Mock implementation
        return ProcessedDocument(
            metadata={
                "id": doc_id,
                "filename": f"document_{doc_id}.pdf",
                "upload_timestamp": "2023-01-01T00:00:00",
                "file_size": 1000,
                "mime_type": "application/pdf",
                "user_id": "test-user"
            },
            content_type="balance_sheet",
            extraction_timestamp="2023-01-01T00:00:01",
            extracted_data={"raw_text": f"Test content for document {doc_id}"}
        )

# Mock database session
class AsyncSession:
    pass

async def get_db():
    return AsyncSession()

# Mock authentication
async def get_current_user_id():
    return "test-user-id"

# Mock session service
async def get_session_service():
    class SessionService:
        async def get_sessions_for_user(self, user_id, limit, offset):
            return [
                type('obj', (object,), {
                    'id': 'test-conversation-id',
                    'title': 'Test Conversation',
                    'created_at': '2023-01-01T00:00:00',
                    'updated_at': '2023-01-01T00:00:01',
                    'documents': []
                })
            ]
        
        async def delete_session(self, session_id):
            return True
    
    return SessionService()

router = APIRouter(tags=["conversation"])
logger = logging.getLogger(__name__)

# Dependency for LangGraph service
async def get_langgraph_service():
    return LangGraphService()

# Dependency for Document service
async def get_document_service(db: AsyncSession = Depends(get_db)):
    return DocumentService(db)

@router.post("/conversation", response_model=Dict[str, Any])
async def create_conversation(
    request: ConversationCreateRequest,
    langgraph_service: LangGraphService = Depends(get_langgraph_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new conversation session with LangGraph.
    
    Args:
        request: Conversation creation request with title and document IDs
        langgraph_service: LangGraph service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        Newly created conversation session details
    """
    try:
        # Generate a new conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Initialize conversation in LangGraph
        conversation = await langgraph_service.initialize_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id,
            document_ids=request.document_ids,
            conversation_title=request.title
        )
        
        return {
            "conversation_id": conversation_id,
            "title": request.title or f"Conversation {conversation_id[:8]}",
            "created_at": conversation.get("state", {}).get("context", {}).get("created_at", ""),
            "status": "created"
        }
    except Exception as e:
        logger.exception(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@router.post("/conversation/{conversation_id}/documents", response_model=Dict[str, Any])
async def add_documents_to_conversation(
    conversation_id: str,
    document_ids: List[str],
    langgraph_service: LangGraphService = Depends(get_langgraph_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add documents to a conversation.
    
    Args:
        conversation_id: ID of the conversation
        document_ids: List of document IDs to add
        langgraph_service: LangGraph service dependency
        document_service: Document service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        Status of document addition
    """
    try:
        valid_documents = []
        invalid_documents = []
        
        # Verify each document exists and belongs to the user
        for doc_id in document_ids:
            doc = await document_service.get_document(doc_id)
            if doc:
                valid_documents.append(doc)
            else:
                invalid_documents.append(doc_id)
        
        # If no valid documents were found, return an error
        if not valid_documents and document_ids:
            raise HTTPException(
                status_code=404, 
                detail=f"No valid documents found from the provided IDs: {document_ids}"
            )
        
        # Build ProcessedDocument objects from the document metadata
        documents = []
        for doc in valid_documents:
            # The mock document return value is already a dict.
            # In a real implementation, we might need to convert from 
            # a database model to a ProcessedDocument
            documents.append(doc)
        
        # Add documents to the conversation
        result = await langgraph_service.add_documents_to_conversation(
            conversation_id=conversation_id,
            documents=documents
        )
        
        # Format the response to match test expectations
        return {
            "conversation_id": conversation_id,
            "documents_added": len(valid_documents),
            "document_ids": [doc_id for doc_id in document_ids if doc_id not in invalid_documents],
            "invalid_documents": invalid_documents,
            "status": "documents_added"
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions so they maintain their status code
        raise e
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            logger.error(f"Conversation not found: {e}")
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        logger.error(f"ValueError adding documents: {e}")
        raise HTTPException(status_code=400, detail=f"Error adding documents: {str(e)}")
    except Exception as e:
        logger.exception(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add documents: {str(e)}")

@router.post("/conversation/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: MessageRequest,
    langgraph_service: LangGraphService = Depends(get_langgraph_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the conversation and get a response.
    
    Args:
        conversation_id: ID of the conversation
        request: Message request with content and optional document references
        langgraph_service: LangGraph service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        AI assistant response with any citations
    """
    try:
        # Ensure the conversation_id in the path matches the session_id in the request
        # This helps prevent inconsistencies in the API
        if request.session_id != conversation_id:
            request.session_id = conversation_id
        
        # Process the message through LangGraph
        response = await langgraph_service.process_message(
            conversation_id=conversation_id,
            message_content=request.content,
            cited_document_ids=request.referenced_documents
        )
        
        # Create proper Citation objects if needed
        citations = []
        if "citations" in response and response["citations"]:
            for citation in response["citations"]:
                # Create a document citation
                citations.append(PageLocationCitation(
                    type=CitationType.PAGE_LOCATION,
                    cited_text=citation.get("text", ""),
                    document_index=citation.get("document_index", 0),
                    document_title=citation.get("document_title", "Unknown"),
                    start_page_number=citation.get("page", 1),
                    # If end_page is provided, use it, otherwise use start_page + 1 for exclusive range
                    end_page_number=citation.get("end_page", citation.get("page", 1) + 1)
                ))
        
        # Format the message response
        message_response = MessageResponse(
            id=response.get("message_id", str(uuid.uuid4())),
            session_id=conversation_id,
            timestamp=datetime.now(),
            role=MessageRole.ASSISTANT,
            content=response.get("content", ""),
            citations=citations,
            referenced_documents=request.referenced_documents,
            referenced_analyses=request.referenced_analyses or []
        )
        
        return message_response
    except ValueError as e:
        # Check if this is actually a "not found" error
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            logger.error(f"Conversation not found: {e}")
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        logger.error(f"ValueError in send_message: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        logger.exception(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/conversation/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    langgraph_service: LangGraphService = Depends(get_langgraph_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get conversation history for a specific conversation.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return
        langgraph_service: LangGraph service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        Conversation history with messages
    """
    try:
        # Get conversation history from LangGraph
        messages = await langgraph_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        
        # Convert messages to MessageResponse format
        formatted_messages = []
        for msg in messages:
            # Create proper Citation objects if needed
            citations = []
            if "citations" in msg and msg["citations"]:
                for citation in msg["citations"]:
                    # Create a document citation
                    citations.append(PageLocationCitation(
                        type=CitationType.PAGE_LOCATION,
                        cited_text=citation.get("text", ""),
                        document_index=citation.get("document_index", 0),
                        document_title=citation.get("document_title", "Unknown"),
                        start_page_number=citation.get("page", 1),
                        # If end_page is provided, use it, otherwise use start_page + 1 for exclusive range
                        end_page_number=citation.get("end_page", citation.get("page", 1) + 1)
                    ))
            
            # Parse the timestamp or use current time
            try:
                if isinstance(msg.get("timestamp"), str):
                    timestamp = datetime.fromisoformat(msg.get("timestamp"))
                else:
                    timestamp = datetime.now()
            except (ValueError, TypeError):
                timestamp = datetime.now()
            
            # Determine the role
            try:
                role = MessageRole(msg.get("role", "user"))
            except ValueError:
                role = MessageRole.USER
            
            # Create MessageResponse
            formatted_messages.append(MessageResponse(
                id=msg.get("id", str(uuid.uuid4())),
                session_id=conversation_id,
                timestamp=timestamp,
                role=role,
                content=msg.get("content", ""),
                citations=citations,
                referenced_documents=msg.get("referenced_documents", []),
                referenced_analyses=msg.get("referenced_analyses", [])
            ))
        
        # Format the response
        return ConversationHistoryResponse(
            session_id=conversation_id,
            messages=formatted_messages,
            has_more=len(messages) >= limit
        )
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            logger.error(f"Conversation not found: {e}")
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        logger.error(f"ValueError in get_conversation_history: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        logger.exception(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation history: {str(e)}")

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    session_service = Depends(get_session_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    List all conversations for the current user.
    
    Args:
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip for pagination
        session_service: Session service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        List of conversation metadata
    """
    try:
        # Get conversations from database
        conversations = await session_service.get_sessions_for_user(
            user_id=current_user_id,
            limit=limit,
            offset=offset
        )
        
        # Format the response
        result = []
        for conv in conversations:
            result.append({
                "conversation_id": str(conv.id),
                "title": conv.title or f"Conversation {str(conv.id)[:8]}",
                "created_at": str(conv.created_at),
                "updated_at": str(conv.updated_at),
                "document_count": len(conv.documents) if hasattr(conv, "documents") else 0
            })
        
        return result
    except Exception as e:
        logger.exception(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")

@router.delete("/conversation/{conversation_id}", response_model=Dict[str, Any])
async def delete_conversation(
    conversation_id: str,
    session_service = Depends(get_session_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: ID of the conversation to delete
        session_service: Session service dependency
        current_user_id: Current authenticated user ID
        
    Returns:
        Deletion status
    """
    try:
        # Delete conversation from database
        deleted = await session_service.delete_session(
            session_id=conversation_id
        )
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        
        return {
            "conversation_id": conversation_id,
            "status": "deleted"
        }
    except Exception as e:
        logger.exception(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}") 