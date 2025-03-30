from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message, MessageRole, MessageRequest, ConversationState, ConversationCreateRequest
from models.document import ProcessedDocument, Citation
from pdf_processing.document_service import DocumentService
from repositories.document_repository import DocumentRepository
from repositories.conversation_repository import ConversationRepository
from services.conversation_service import ConversationService
from pdf_processing.claude_service import ClaudeService
from utils.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversation", tags=["conversation"])

# Dependencies
async def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepository(db)

async def get_document_service(
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    return DocumentService(document_repository)

async def get_conversation_repository(db: AsyncSession = Depends(get_db)):
    return ConversationRepository(db)

async def get_conversation_service(
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    return ConversationService(
        conversation_repository=conversation_repository,
        document_repository=document_repository
    )

async def get_claude_service():
    return ClaudeService()

async def get_current_user_id():
    # This is a placeholder for authentication
    # In a real application, this would validate the JWT token and return the user ID
    return "default-user"

@router.post("", response_model=ConversationState, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new conversation with optional document associations.
    """
    try:
        # Override the user_id with the authenticated user
        conversation_data.user_id = user_id
        
        # Create the conversation
        conversation = await conversation_service.create_conversation(
            title=conversation_data.title,
            user_id=conversation_data.user_id,
            document_ids=conversation_data.document_ids or []
        )
        
        # Create and return the conversation state
        state = ConversationState(
            session_id=conversation.id,
            active_documents=conversation_data.document_ids or [],
            last_updated=conversation.updated_at
        )
        
        logger.info(f"Created conversation: {conversation.id} for user: {user_id}")
        return state
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )

@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    message: MessageRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """
    Send a message to a conversation and get an AI response using Claude API.
    
    The message will be processed and a response generated based on the conversation context.
    If documents are attached to the conversation, they will be used for context.
    
    Args:
        session_id: The ID of the conversation session
        message: The message content and optional citation IDs
        
    Returns:
        The AI response message
    """
    if message.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID in path must match session ID in request body"
        )
    
    try:
        result = await conversation_service.process_user_message(
            conversation_id=session_id,
            content=message.content,
            citation_ids=message.citation_links
        )
        
        if not result.get("success", True):
            # Return the error message but with a 200 status code
            # This allows the client to handle the error gracefully
            logger.warning(f"Error processing message: {result.get('error', 'Unknown error')}")
            return result.get("message")
        
        return result.get("message")
    except ValueError as e:
        logger.error(f"Bad request while processing message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the message: {str(e)}"
        )

def is_financial_analysis_request(message: str) -> bool:
    """
    Determine if a message is asking for financial analysis.
    
    Args:
        message: User message text
        
    Returns:
        True if the message appears to be a financial question, False otherwise
    """
    # Simple heuristic to determine if this is a financial question
    financial_keywords = [
        "financial", "revenue", "profit", "margin", "expense", "income",
        "balance sheet", "cash flow", "ratio", "trend", "growth", "forecast",
        "comparison", "analyze", "calculate", "metric", "performance", "quarterly",
        "annual", "fiscal", "q1", "q2", "q3", "q4", "year-over-year", "yoy"
    ]
    
    message_lower = message.lower()
    
    # Check for financial keywords
    if any(keyword in message_lower for keyword in financial_keywords):
        return True
    
    # Check for questions about calculations, comparisons, or visualizations
    calculation_phrases = [
        "calculate", "compare", "show me", "what is the", "how much",
        "visualize", "chart", "graph", "plot", "trend", "over time"
    ]
    
    if any(phrase in message_lower for phrase in calculation_phrases):
        return True
    
    return False

@router.get("/{conversation_id}/history", response_model=List[Message])
async def get_conversation_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get the history of messages for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return
        offset: Starting offset for pagination
        
    Returns:
        List of messages in the conversation
    """
    # Check if the conversation exists and belongs to the user
    conversation = await conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get the conversation messages
    messages = await conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    
    # Convert messages to API response format
    api_messages = []
    
    for msg in messages:
        # Get citations for this message
        citations = await conversation_service.conversation_repository.get_message_citations(msg.id)
        
        # Convert citations to Citation objects
        citation_objects = []
        for citation in citations:
            # Get the document for this citation
            document = await conversation_service.document_repository.get_document(citation.document_id)
            doc_title = document.filename if document else "Unknown Document"
            
            citation_objects.append(
                Citation(
                    id=citation.id,
                    document_id=citation.document_id,
                    document_title=doc_title,
                    content=citation.content,
                    metadata=citation.metadata or {},
                    type=citation.metadata.get("type", "unknown") if citation.metadata else "unknown"
                )
            )
        
        # Create content blocks if available
        content_blocks = None
        if hasattr(msg, 'content_blocks') and msg.content_blocks:
            content_blocks = msg.content_blocks
        
        # Get analysis blocks for this message
        analysis_blocks = []
        if hasattr(msg, 'analysis_blocks'):
            for block in msg.analysis_blocks:
                analysis_blocks.append({
                    "id": block.id,
                    "block_type": block.block_type,
                    "title": block.title,
                    "content": block.content,
                    "created_at": block.created_at
                })
        
        api_messages.append(
            Message(
                id=msg.id,
                session_id=msg.conversation_id,
                timestamp=msg.created_at,
                role=MessageRole(msg.role),
                content=msg.content,
                referenced_documents=[],  # We don't store this directly in the database
                referenced_analyses=[],   # We don't store this directly in the database
                citation_links=[citation.id for citation in citations],
                citations=citation_objects,
                content_blocks=content_blocks,
                analysis_blocks=analysis_blocks
            )
        )
    
    return api_messages

@router.get("", response_model=List[Dict[str, Any]])
async def list_conversations(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all conversations for the current user.
    """
    try:
        conversations = await conversation_service.list_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Get the total count
        total_count = await conversation_service.conversation_repository.count_conversations(user_id)
        
        # Format the response
        result = []
        for conversation in conversations:
            # Get the last message for preview
            messages = await conversation_service.get_conversation_messages(
                conversation_id=conversation.id,
                limit=1
            )
            
            last_message = None
            if messages:
                last_message = {
                    "content": messages[0].content[:100] + "..." if len(messages[0].content) > 100 else messages[0].content,
                    "role": messages[0].role,
                    "timestamp": messages[0].created_at.isoformat()
                }
            
            # Get associated documents
            documents = await conversation_service.conversation_repository.get_conversation_documents(conversation.id)
            document_count = len(documents)
            
            result.append({
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "last_message": last_message,
                "document_count": document_count
            })
        
        return result
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing conversations: {str(e)}"
        )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a conversation and all associated messages.
    """
    try:
        # Check if the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this conversation"
            )
        
        # Delete the conversation
        deleted = await conversation_service.conversation_repository.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )

@router.post("/{conversation_id}/document/{document_id}", status_code=status.HTTP_200_OK)
async def add_document_to_conversation(
    conversation_id: str,
    document_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    document_service: DocumentService = Depends(get_document_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add a document to a conversation.
    """
    try:
        # Check if the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this conversation"
            )
        
        # Check if the document exists and belongs to the user
        document = await document_service.document_repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this document"
            )
        
        # Add the document to the conversation
        success = await conversation_service.conversation_repository.add_document_to_conversation(
            conversation_id=conversation_id,
            document_id=document_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add document to conversation"
            )
        
        return {"message": "Document added to conversation successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error adding document to conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding document to conversation: {str(e)}"
        )

@router.get("/{conversation_id}/document", response_model=List[Dict[str, Any]])
async def get_conversation_documents(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all documents associated with a conversation.
    """
    try:
        # Check if the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this conversation"
            )
        
        # Get the documents
        documents = await conversation_service.conversation_repository.get_conversation_documents(conversation_id)
        
        # Format the response
        result = []
        for doc in documents:
            result.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "mime_type": doc.mime_type,
                "upload_timestamp": doc.upload_timestamp.isoformat(),
                "document_type": doc.document_type.value if doc.document_type else "other"
            })
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting conversation documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation documents: {str(e)}"
        )

@router.delete("/{conversation_id}/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_from_conversation(
    conversation_id: str,
    document_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Remove a document from a conversation.
    """
    try:
        # Check if the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this conversation"
            )
        
        # Remove the document from the conversation
        success = await conversation_service.conversation_repository.remove_document_from_conversation(
            conversation_id=conversation_id,
            document_id=document_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found in conversation"
            )
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error removing document from conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing document from conversation: {str(e)}"
        )