from typing import Dict, List, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime

class MetricConfig(BaseModel):
    """Configuration for a metric in a chart."""
    label: str
    unit: Optional[str] = None  # Added for frontend consistency
    color: Optional[str] = None
    formatter: Optional[str] = None  # Added for frontend formatting
    precision: Optional[int] = None  # Added for frontend number formatting

class ChartConfig(BaseModel):
    """Configuration for a chart."""
    title: str
    description: str
    subtitle: Optional[str] = None  # Added for frontend consistency
    xAxisLabel: Optional[str] = None  # Added for frontend chart labels
    yAxisLabel: Optional[str] = None  # Added for frontend chart labels
    xAxisKey: Optional[str] = None
    trend: Optional[Dict[str, Any]] = None
    footer: Optional[str] = None
    totalLabel: Optional[str] = None
    showLegend: bool = True  # Added for frontend chart legend control
    legendPosition: Optional[Literal["top", "bottom", "left", "right"]] = "bottom"  # Added for frontend
    showGrid: Optional[bool] = True  # Added for frontend grid display
    height: Optional[int] = None  # Added for frontend sizing
    width: Optional[int] = None  # Added for frontend sizing
    stack: Optional[bool] = False  # Added for frontend stacked charts

class ChartData(BaseModel):
    """Base model for chart data."""
    chartType: Literal["bar", "multiBar", "line", "pie", "area", "stackedArea"]
    config: ChartConfig
    data: List[Dict[str, Any]]
    chartConfig: Dict[str, MetricConfig]
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )

class TableColumn(BaseModel):
    """Definition of a table column."""
    key: str
    label: str  # Backend uses 'label'
    header: Optional[str] = None  # Added for frontend (uses 'header' instead of 'label')
    format: Optional[Literal["number", "currency", "percentage", "text"]] = None
    width: Optional[int] = None  # Added for frontend column sizing
    align: Optional[Literal["left", "center", "right"]] = "left"  # Added for frontend text alignment
    formatter: Optional[str] = None  # Added for frontend custom formatting

class TableConfig(BaseModel):
    """Configuration for a table."""
    title: str
    description: str
    subtitle: Optional[str] = None  # Added for frontend consistency
    footer: Optional[str] = None
    columns: List[TableColumn]
    showRowNumbers: Optional[bool] = False  # Added for frontend row numbering
    sortable: Optional[bool] = True  # Added for frontend sorting functionality
    pagination: Optional[bool] = True  # Added for frontend pagination
    pageSize: Optional[int] = 10  # Added for frontend pagination size
    height: Optional[int] = None  # Added for frontend sizing
    width: Optional[int] = None  # Added for frontend sizing

class TableData(BaseModel):
    """Model for table data."""
    tableType: Literal["simple", "matrix", "comparison"]
    config: TableConfig
    data: List[Dict[str, Any]]
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )

class VisualizationData(BaseModel):
    """Container for different visualization types."""
    charts: Optional[List[ChartData]] = Field(default_factory=list)
    tables: Optional[List[TableData]] = Field(default_factory=list)
    
    # Common chart types expected by frontend
    monetaryValues: Optional[Dict[str, Any]] = Field(default_factory=dict)
    percentages: Optional[Dict[str, Any]] = Field(default_factory=dict)
    keywordFrequency: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    ) 