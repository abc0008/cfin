from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, UUID4

from models.citation import Citation, ContentBlock


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    role: MessageRole
    content: str
    referenced_documents: List[str] = Field(default_factory=list)
    referenced_analyses: List[str] = Field(default_factory=list)
    citation_links: List[str] = Field(default_factory=list)
    citations: Optional[List[Citation]] = Field(default_factory=list)
    content_blocks: Optional[List[ContentBlock]] = None
    analysis_blocks: Optional[List[Dict[str, Any]]] = None


class ConversationState(BaseModel):
    session_id: str
    active_documents: List[str] = Field(default_factory=list)
    active_analyses: List[str] = Field(default_factory=list)
    current_focus: Optional[str] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    message_history: List[Dict[str, Any]] = Field(default_factory=list)


class MessageRequest(BaseModel):
    session_id: str
    content: str
    user_id: str = "default-user"
    referenced_documents: List[str] = Field(default_factory=list)
    referenced_analyses: List[str] = Field(default_factory=list)
    citation_links: List[str] = Field(default_factory=list)
    citation_ids: Optional[List[str]] = Field(default_factory=list)


class ConversationCreateRequest(BaseModel):
    title: str
    user_id: str = "default-user"
    document_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: str
    session_id: str
    timestamp: datetime
    role: MessageRole
    content: str
    referenced_documents: List[str] = Field(default_factory=list)
    referenced_analyses: List[str] = Field(default_factory=list)
    citation_links: List[str] = Field(default_factory=list)
    citations: Optional[List[Citation]] = None
    content_blocks: Optional[List[ContentBlock]] = None
    analysis_blocks: Optional[List[Dict[str, Any]]] = None


class ConversationHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]
    has_more: bool = False
    next_cursor: Optional[str] = None