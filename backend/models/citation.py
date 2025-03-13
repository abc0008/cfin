from enum import Enum
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field

class CitationType(str, Enum):
    CHAR_LOCATION = "char_location"
    PAGE_LOCATION = "page_location"
    CONTENT_BLOCK_LOCATION = "content_block_location"

class CitationBase(BaseModel):
    """Base class for all citation types."""
    type: CitationType
    cited_text: str
    document_index: int
    document_title: str

class CharLocationCitation(CitationBase):
    """Citation for plain text documents."""
    type: Literal[CitationType.CHAR_LOCATION] = CitationType.CHAR_LOCATION
    start_char_index: int
    end_char_index: int

class PageLocationCitation(CitationBase):
    """Citation for PDF documents."""
    type: Literal[CitationType.PAGE_LOCATION] = CitationType.PAGE_LOCATION
    start_page_number: int
    end_page_number: int

class ContentBlockLocationCitation(CitationBase):
    """Citation for custom content documents."""
    type: Literal[CitationType.CONTENT_BLOCK_LOCATION] = CitationType.CONTENT_BLOCK_LOCATION
    start_block_index: int
    end_block_index: int

# Generic Citation type that could be any of the specific citation types
Citation = Union[CharLocationCitation, PageLocationCitation, ContentBlockLocationCitation]

class ContentBlock(BaseModel):
    """Model for a content block in Claude's response."""
    type: Literal["text"] = "text"
    text: str
    citations: Optional[List[Citation]] = None

class AnthropicMessage(BaseModel):
    """Model for a message in Claude's response."""
    content: List[ContentBlock] 