"""
Utility functions for converting between different message formats.

This module provides conversion functions for:
1. Converting between Claude API message format and internal message models
2. Converting between frontend message format and internal message models
3. Converting citations between different formats
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.message import Message, MessageRole
from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation, ContentBlock, AnthropicMessage

def claude_message_to_internal(claude_message: Dict[str, Any]) -> Message:
    """
    Convert a Claude API message to our internal Message model.
    
    Args:
        claude_message: Message from Claude API
        
    Returns:
        Internal Message model
    """
    message_id = str(uuid.uuid4())
    role = claude_message.get("role", "assistant").lower()
    
    # Extract content from Claude message format
    content = ""
    content_blocks = []
    citations = []
    
    # Process content blocks if they exist
    if "content" in claude_message and isinstance(claude_message["content"], list):
        for block in claude_message["content"]:
            if block.get("type") == "text":
                content += block.get("text", "")
                
                # Convert citations if they exist
                if "citations" in block:
                    for citation in block.get("citations", []):
                        citation_obj = _convert_claude_citation(citation)
                        if citation_obj:
                            citations.append(citation_obj)
                
                # Create content block
                content_block = ContentBlock(
                    text=block.get("text", ""),
                    citations=[_convert_claude_citation(citation) for citation in block.get("citations", [])]
                )
                content_blocks.append(content_block)
    elif "content" in claude_message and isinstance(claude_message["content"], str):
        content = claude_message["content"]
    
    # Create Message object
    message = Message(
        id=message_id,
        session_id=claude_message.get("session_id", ""),
        timestamp=datetime.now().isoformat(),
        role=MessageRole(role),
        content=content,
        content_blocks=content_blocks,
        citations=citations,
        referenced_documents=claude_message.get("referenced_documents", []),
        referenced_analyses=claude_message.get("referenced_analyses", [])
    )
    
    return message

def internal_message_to_claude(message: Message) -> Dict[str, Any]:
    """
    Convert an internal Message model to Claude API format.
    
    Args:
        message: Internal Message model
        
    Returns:
        Message in Claude API format
    """
    # Create Claude message structure
    claude_message = {
        "role": message.role.value,
    }
    
    # Handle content blocks if they exist
    if message.content_blocks:
        claude_message["content"] = []
        for block in message.content_blocks:
            content_block = {
                "type": "text",
                "text": block.text
            }
            
            # Add citations if they exist
            if block.citations:
                content_block["citations"] = [
                    _convert_internal_citation_to_claude(citation)
                    for citation in block.citations
                ]
            
            claude_message["content"].append(content_block)
    else:
        # Simple text content
        claude_message["content"] = [{"type": "text", "text": message.content}]
    
    return claude_message

def frontend_message_to_internal(frontend_message: Dict[str, Any]) -> Message:
    """
    Convert a frontend message format to our internal Message model.
    
    Args:
        frontend_message: Message from frontend
        
    Returns:
        Internal Message model
    """
    # Extract fields from frontend message
    message_id = frontend_message.get("id", str(uuid.uuid4()))
    session_id = frontend_message.get("sessionId", "")
    timestamp = frontend_message.get("timestamp", datetime.now().isoformat())
    role = frontend_message.get("role", "user").lower()
    content = frontend_message.get("content", "")
    
    # Extract citations if they exist
    citations = []
    if "citationLinks" in frontend_message and frontend_message["citationLinks"]:
        for citation in frontend_message["citationLinks"]:
            citation_obj = _convert_frontend_citation(citation)
            if citation_obj:
                citations.append(citation_obj)
    
    # Create Message object
    message = Message(
        id=message_id,
        session_id=session_id,
        timestamp=timestamp,
        role=MessageRole(role),
        content=content,
        citations=citations,
        referenced_documents=frontend_message.get("referencedDocuments", []),
        referenced_analyses=frontend_message.get("referencedAnalyses", [])
    )
    
    return message

def internal_message_to_frontend(message: Message) -> Dict[str, Any]:
    """
    Convert an internal Message model to frontend format.
    
    Args:
        message: Internal Message model
        
    Returns:
        Message in frontend format
    """
    # Create frontend message structure
    frontend_message = {
        "id": message.id,
        "sessionId": message.session_id,
        "timestamp": message.timestamp,
        "role": message.role.value,
        "content": message.content,
        "referencedDocuments": message.referenced_documents,
        "referencedAnalyses": message.referenced_analyses,
    }
    
    # Add citations if they exist
    if message.citations:
        frontend_message["citationLinks"] = [
            _convert_internal_citation_to_frontend(citation)
            for citation in message.citations
        ]
    
    return frontend_message

def _convert_claude_citation(claude_citation: Dict[str, Any]) -> Optional[Citation]:
    """
    Convert a Claude citation to internal Citation model.
    
    Args:
        claude_citation: Citation from Claude API
        
    Returns:
        Internal Citation model or None if conversion fails
    """
    try:
        citation_type = claude_citation.get("type")
        
        if citation_type == "char_location":
            # Text document citation
            return CharLocationCitation(
                type=CitationType.CHAR_LOCATION,
                cited_text=claude_citation.get("content", {}).get("quote", ""),
                document_index=0,  # Default to first document
                document_title=claude_citation.get("document", {}).get("title", ""),
                start_char_index=claude_citation.get("start_char_offset", 0),
                end_char_index=claude_citation.get("end_char_offset", 0)
            )
        elif citation_type == "page_location":
            # PDF document citation
            page_num = claude_citation.get("page", 1)
            return PageLocationCitation(
                type=CitationType.PAGE_LOCATION,
                cited_text=claude_citation.get("content", {}).get("quote", ""),
                document_index=0,  # Default to first document
                document_title=claude_citation.get("document", {}).get("title", ""),
                start_page_number=page_num,
                end_page_number=page_num
            )
        else:
            # Unsupported citation type
            return None
    except Exception as e:
        print(f"Error converting Claude citation: {e}")
        return None

def _convert_internal_citation_to_claude(citation: Citation) -> Dict[str, Any]:
    """
    Convert an internal Citation model to Claude API format.
    
    Args:
        citation: Internal Citation model
        
    Returns:
        Citation in Claude API format
    """
    if citation.type == CitationType.CHAR_LOCATION:
        citation = citation  # type: CharLocationCitation
        return {
            "type": "char_location",
            "start_char_offset": citation.start_char_index,
            "end_char_offset": citation.end_char_index,
            "content": {
                "quote": citation.cited_text
            },
            "document": {
                "title": citation.document_title,
                "url": ""
            }
        }
    elif citation.type == CitationType.PAGE_LOCATION:
        citation = citation  # type: PageLocationCitation
        return {
            "type": "page_location",
            "page": citation.start_page_number,
            "content": {
                "quote": citation.cited_text
            },
            "document": {
                "title": citation.document_title,
                "url": ""
            }
        }
    elif citation.type == CitationType.CONTENT_BLOCK_LOCATION:
        citation = citation  # type: ContentBlockLocationCitation
        return {
            "type": "content_block_location",
            "start_block_index": citation.start_block_index,
            "end_block_index": citation.end_block_index,
            "content": {
                "quote": citation.cited_text
            },
            "document": {
                "title": citation.document_title,
                "url": ""
            }
        }
    else:
        # Unsupported citation type
        return {}

def _convert_frontend_citation(frontend_citation: Dict[str, Any]) -> Optional[Citation]:
    """
    Convert a frontend citation to internal Citation model.
    
    Args:
        frontend_citation: Citation from frontend
        
    Returns:
        Internal Citation model or None if conversion fails
    """
    try:
        # Most frontend citations will be page-based (PDF)
        page_num = frontend_citation.get("page", 1)
        return PageLocationCitation(
            type=CitationType.PAGE_LOCATION,
            cited_text=frontend_citation.get("text", ""),
            document_index=0,  # Default to first document
            document_title=frontend_citation.get("title", ""),
            start_page_number=page_num,
            end_page_number=page_num
        )
    except Exception as e:
        print(f"Error converting frontend citation: {e}")
        return None

def _convert_internal_citation_to_frontend(citation: Citation) -> Dict[str, Any]:
    """
    Convert an internal Citation model to frontend format.
    
    Args:
        citation: Internal Citation model
        
    Returns:
        Citation in frontend format
    """
    frontend_citation = {
        "text": citation.cited_text,
        "documentId": f"doc-{citation.document_index}"  # Generate a document ID
    }
    
    if citation.type == CitationType.PAGE_LOCATION:
        citation = citation  # type: PageLocationCitation
        frontend_citation["page"] = citation.start_page_number
        
    elif citation.type == CitationType.CHAR_LOCATION:
        citation = citation  # type: CharLocationCitation
        frontend_citation["startChar"] = citation.start_char_index
        frontend_citation["endChar"] = citation.end_char_index
    
    return frontend_citation 