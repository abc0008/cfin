from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, UUID4, ConfigDict


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
    isEstimated: bool = Field(default=False, alias="is_estimated")
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )


class ComparativePeriod(BaseModel):
    metric: str
    currentPeriod: str = Field(alias="current_period")
    previousPeriod: str = Field(alias="previous_period")
    currentValue: float = Field(alias="current_value")
    previousValue: float = Field(alias="previous_value")
    change: float
    percentChange: float = Field(alias="percent_change")
    trend: Literal["positive", "negative", "neutral"] = "neutral"
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )


class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    documentIds: List[str] = Field(alias="document_ids")
    analysisType: str = Field(alias="analysis_type")
    timestamp: datetime = Field(default_factory=datetime.now)
    metrics: List[FinancialMetric] = Field(default_factory=list)
    ratios: List[FinancialRatio] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    visualizationData: Dict[str, Any] = Field(default_factory=dict, alias="visualization_data")
    citationReferences: Dict[str, str] = Field(default_factory=dict, alias="citation_references")
    comparativePeriods: List[ComparativePeriod] = Field(default_factory=list, alias="comparative_periods")
    analysisText: Optional[str] = Field(default=None, alias="analysis_text")
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )


class AnalysisRequest(BaseModel):
    analysisType: str = Field(alias="analysis_type")
    documentIds: List[str] = Field(alias="document_ids")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    query: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )