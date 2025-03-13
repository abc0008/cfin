import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, and_, desc, or_

from models.database_models import Conversation, Message, User, Document, Citation, MessageCitation, ConversationDocument, AnalysisBlock
from models.document import Citation as CitationSchema
from utils.storage import StorageService

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Repository for conversation operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the conversation repository."""
        self.db = db
    
    async def create_conversation(self, title: str, user_id: str, document_ids: Optional[List[str]] = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            title: Title of the conversation
            user_id: ID of the user creating the conversation
            document_ids: Optional list of document IDs to associate with the conversation
            
        Returns:
            Created conversation
        """
        # Create the conversation record
        conversation = Conversation(
            id=str(uuid.uuid4()),
            title=title,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        self.db.add(conversation)
        await self.db.flush()
        
        # Associate documents if provided
        if document_ids:
            for doc_id in document_ids:
                conversation_document = ConversationDocument(
                    conversation_id=conversation.id,
                    document_id=doc_id
                )
                self.db.add(conversation_document)
        
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation if found, None otherwise
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalars().first()
    
    async def list_conversations(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Conversation]:
        """
        List conversations for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            offset: Starting index
            
        Returns:
            List of conversations
        """
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def count_conversations(self, user_id: str) -> int:
        """
        Count the number of conversations for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of conversations
        """
        result = await self.db.execute(
            select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        )
        return result.scalar()
    
    async def update_conversation(self, conversation_id: str, update_data: Dict[str, Any]) -> Optional[Conversation]:
        """
        Update a conversation.
        
        Args:
            conversation_id: ID of the conversation
            update_data: Dictionary of fields to update
            
        Returns:
            Updated conversation if found, None otherwise
        """
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_conversation(conversation_id)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            True if conversation was deleted, False otherwise
        """
        # Delete from database
        await self.db.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        await self.db.commit()
        
        return True
    
    async def add_message(
        self, 
        conversation_id: str, 
        content: str, 
        role: str,
        citation_ids: Optional[List[str]] = None
    ) -> Optional[Message]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            content: Message content
            role: Message role (user, assistant, system)
            citation_ids: Optional list of citation IDs to associate with the message
            
        Returns:
            Created message if conversation found, None otherwise
        """
        # Check if conversation exists
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        # Update conversation last updated timestamp
        await self.update_conversation(conversation_id, {})
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            content=content,
            role=role,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        self.db.add(message)
        await self.db.flush()
        
        # Associate citations if provided
        if citation_ids:
            for citation_id in citation_ids:
                message_citation = MessageCitation(
                    message_id=message.id,
                    citation_id=citation_id
                )
                self.db.add(message_citation)
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def get_message(self, message_id: str) -> Optional[Message]:
        """
        Get a message by ID.
        
        Args:
            message_id: ID of the message
            
        Returns:
            Message if found, None otherwise
        """
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalars().first()
        
    async def update_message(self, message: Message) -> Optional[Message]:
        """
        Update a message with new data.
        
        Args:
            message: Message object with updated fields
            
        Returns:
            Updated message if successful, None otherwise
        """
        try:
            # Just merge the message object with the database
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            
            logger.info(f"Updated message {message.id} - attributes: {dir(message)}")
            
            return message
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            await self.db.rollback()
            return None
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            offset: Starting index
            
        Returns:
            List of messages
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_message_citations(self, message_id: str) -> List[Citation]:
        """
        Get citations for a message.
        
        Args:
            message_id: ID of the message
            
        Returns:
            List of citations
        """
        result = await self.db.execute(
            select(Citation)
            .join(MessageCitation, MessageCitation.citation_id == Citation.id)
            .where(MessageCitation.message_id == message_id)
        )
        return result.scalars().all()
    
    async def add_analysis_block(
        self,
        message_id: str,
        block_type: str,
        title: str,
        content: Dict[str, Any]
    ) -> Optional[AnalysisBlock]:
        """
        Add an analysis block to a message.
        
        Args:
            message_id: ID of the message
            block_type: Type of analysis block (chart, insight, etc.)
            title: Title of the block
            content: JSON content of the block
            
        Returns:
            Created analysis block if message found, None otherwise
        """
        # Check if message exists
        message = await self.get_message(message_id)
        if not message:
            return None
        
        # Create analysis block
        analysis_block = AnalysisBlock(
            id=str(uuid.uuid4()),
            message_id=message_id,
            block_type=block_type,
            title=title,
            content=content,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        self.db.add(analysis_block)
        await self.db.commit()
        await self.db.refresh(analysis_block)
        
        return analysis_block
    
    async def get_message_analysis_blocks(self, message_id: str) -> List[AnalysisBlock]:
        """
        Get analysis blocks for a message.
        
        Args:
            message_id: ID of the message
            
        Returns:
            List of analysis blocks
        """
        result = await self.db.execute(
            select(AnalysisBlock)
            .where(AnalysisBlock.message_id == message_id)
            .order_by(AnalysisBlock.created_at.asc())
        )
        return result.scalars().all()
    
    async def add_document_to_conversation(self, conversation_id: str, document_id: str) -> bool:
        """
        Add a document to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            document_id: ID of the document
            
        Returns:
            True if successful, False otherwise
        """
        # Check if the association already exists
        result = await self.db.execute(
            select(ConversationDocument)
            .where(and_(
                ConversationDocument.conversation_id == conversation_id,
                ConversationDocument.document_id == document_id
            ))
        )
        
        if result.scalars().first():
            # Already associated
            return True
        
        # Create the association
        conversation_document = ConversationDocument(
            conversation_id=conversation_id,
            document_id=document_id
        )
        
        self.db.add(conversation_document)
        await self.db.commit()
        
        return True
    
    async def remove_document_from_conversation(self, conversation_id: str, document_id: str) -> bool:
        """
        Remove a document from a conversation.
        
        Args:
            conversation_id: ID of the conversation
            document_id: ID of the document
            
        Returns:
            True if successful, False otherwise
        """
        await self.db.execute(
            delete(ConversationDocument)
            .where(and_(
                ConversationDocument.conversation_id == conversation_id,
                ConversationDocument.document_id == document_id
            ))
        )
        await self.db.commit()
        
        return True
    
    async def get_conversation_documents(self, conversation_id: str) -> List[Document]:
        """
        Get documents for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of documents
        """
        result = await self.db.execute(
            select(Document)
            .join(ConversationDocument, ConversationDocument.document_id == Document.id)
            .where(ConversationDocument.conversation_id == conversation_id)
        )
        return result.scalars().all()
    
    async def search_conversations(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Conversation]:
        """
        Search conversations by title and content.
        
        Args:
            user_id: ID of the user
            query: Search query
            limit: Maximum number of conversations to return
            offset: Starting index
            
        Returns:
            List of matching conversations
        """
        # Search conversations by title
        conversations_query = (
            select(Conversation)
            .where(and_(
                Conversation.user_id == user_id,
                Conversation.title.ilike(f"%{query}%")
            ))
        )
        
        # Also get conversations with messages matching the query
        message_conversations_query = (
            select(Conversation)
            .join(Message, Message.conversation_id == Conversation.id)
            .where(and_(
                Conversation.user_id == user_id,
                Message.content.ilike(f"%{query}%")
            ))
            .distinct()
        )
        
        # Combine results
        combined_query = (
            select(Conversation)
            .where(or_(
                Conversation.id.in_(conversations_query.with_only_columns(Conversation.id)),
                Conversation.id.in_(message_conversations_query.with_only_columns(Conversation.id))
            ))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(combined_query)
        return result.scalars().all()