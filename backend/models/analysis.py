from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, UUID4


class FinancialRatio(BaseModel):
    name: str
    value: float
    description: str
    benchmark: Optional[float] = None
    trend: Optional[float] = None


class FinancialMetric(BaseModel):
    category: str
    name: str
    period: str
    value: float
    unit: str
    is_estimated: bool = False


class AnalysisResult(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    document_ids: List[str]
    analysis_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metrics: List[FinancialMetric] = Field(default_factory=list)
    ratios: List[FinancialRatio] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    visualization_data: Dict[str, Any] = Field(default_factory=dict)
    citation_references: Dict[str, str] = Field(default_factory=dict)


class AnalysisRequest(BaseModel):
    analysis_type: str
    document_ids: List[str]
    parameters: Dict[str, Any] = Field(default_factory=dict)