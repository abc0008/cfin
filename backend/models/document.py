from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, UUID4


class DocumentContentType(str, Enum):
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    NOTES = "notes"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Citation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    page: int
    text: str
    bounding_box: Optional[Dict[str, float]] = None
    section: Optional[str] = None


class DocumentMetadata(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    filename: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    file_size: int
    mime_type: str
    user_id: str
    citation_links: List[str] = Field(default_factory=list)


class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    content_type: DocumentContentType = DocumentContentType.OTHER
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    periods: List[str] = Field(default_factory=list)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    citations: List[Citation] = Field(default_factory=list)
    confidence_score: float = 0.0
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    document_id: UUID4
    filename: str
    status: ProcessingStatus
    message: str