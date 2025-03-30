from typing import Dict, List, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict, RootModel
import logging

logger = logging.getLogger(__name__)

# Base Tool Schema
class ToolSchema(BaseModel):
    """Base model for tool definitions to be used with Claude API."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    cache_control: Optional[Dict[str, str]] = Field(default=None, description="Optional cache control settings")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
        validate_assignment=True,
        protected_namespaces=()
    )

# --- Chart Generation Tool ---

class ChartMetricConfig(BaseModel):
    """Configuration for a single metric/series in a chart."""
    label: str = Field(description="Display label for the metric/series")
    color: Optional[str] = Field(default=None, description="Hex color code for the series (e.g., '#8884d8')")
    unit: Optional[str] = Field(default=None, description="Unit for the metric (e.g., '$', '%')")
    formatter: Optional[str] = Field(default=None, description="Formatting type (e.g., 'currency', 'percent', 'compact')")
    precision: Optional[int] = Field(default=None, description="Number of decimal places for formatting")

class ChartConfig(BaseModel):
    """Configuration for the overall chart appearance and axes."""
    title: str = Field(description="Main title of the chart")
    description: Optional[str] = Field(default=None, description="Subtitle or description below the title")
    xAxisKey: Optional[str] = Field(default="name", description="The key in the 'data' array objects representing the x-axis category/label (e.g., 'period', 'category', 'name')")
    yAxisKey: Optional[str] = Field(default=None, description="The key for y-axis values if only one series (used less often with chartConfig)")
    xAxisLabel: Optional[str] = Field(default=None, description="Label for the x-axis")
    yAxisLabel: Optional[str] = Field(default=None, description="Label for the y-axis")
    showLegend: bool = Field(default=True, description="Whether to display the chart legend")
    legendPosition: Optional[Literal["top", "bottom", "left", "right"]] = Field(default="bottom", description="Position of the legend")
    showGrid: Optional[bool] = Field(default=True, description="Whether to show the chart grid lines")
    stack: Optional[bool] = Field(default=False, description="Whether bars/areas should be stacked")
    colors: Optional[List[str]] = Field(default=None, description="Optional list of hex colors for chart series")
    footer: Optional[str] = Field(default=None, description="Optional text to display below the chart")
    totalLabel: Optional[str] = Field(default=None, description="Optional label for displaying a total (e.g., for pie charts)")

class ChartDataItem(RootModel):
    """Represents a single data point or category in the chart data array."""
    # Example structure: { "name": "Q1 2023", "revenue": 120000, "profit": 35000 }
    # The specific keys (like 'revenue', 'profit') are defined dynamically
    # and should match the keys in chartConfig.
    # The key used for the x-axis label must match ChartConfig.xAxisKey.
    root: Dict[str, Union[str, float, int, None]] = Field(description="A flexible dictionary for chart data points")

class ChartGenerationInputSchema(BaseModel):
    """Input schema for the generate_graph_data tool."""
    chartType: Literal["bar", "multiBar", "line", "pie", "area", "stackedArea", "scatter"] = Field(description="The type of chart to generate")
    config: ChartConfig = Field(description="Overall configuration for the chart")
    data: List[Dict[str, Any]] = Field(description="The array of data points for the chart. Each object represents a category/period. Keys should match xAxisKey and keys in chartConfig.")
    chartConfig: Dict[str, ChartMetricConfig] = Field(description="Configuration for each metric/series being plotted. Keys must match the metric keys in the 'data' objects.")

class ChartGenerationTool(ToolSchema):
    """Tool for generating chart data in a format consumable by the frontend ChartRenderer."""
    name: str = "generate_graph_data"
    description: str = """Use this tool to generate structured JSON data for financial charts and graphs (bar, line, pie, area, scatter).
    Specify the chartType, provide general config (title, axis labels), the data array, and chartConfig for each series/metric.
    The 'data' array objects must contain a key matching 'config.xAxisKey' and keys matching the keys used in 'chartConfig'.
    For pie charts, 'data' objects typically have 'name' and 'value' keys.
    """
    input_schema: Dict[str, Any] = ChartGenerationInputSchema.model_json_schema()

# --- Table Generation Tool ---

class TableColumnConfig(BaseModel):
    """Configuration for a single table column."""
    key: str = Field(description="The key in the 'data' array objects for this column")
    label: str = Field(description="The display label for the column header")
    header: Optional[str] = Field(default=None, description="Alternative header text (if label is different)")
    format: Optional[Literal["number", "currency", "percentage", "text", "date"]] = Field(default="text", description="How to format the data in this column")
    width: Optional[int] = Field(default=None, description="Optional fixed width for the column in pixels")
    align: Optional[Literal["left", "center", "right"]] = Field(default="left", description="Text alignment for the column")

class TableConfig(BaseModel):
    """Configuration for the overall table appearance and behavior."""
    title: str = Field(description="Main title of the table")
    description: Optional[str] = Field(default=None, description="Subtitle or description below the title")
    footer: Optional[str] = Field(default=None, description="Optional text to display below the table")
    columns: List[TableColumnConfig] = Field(description="Array defining the columns of the table")
    showRowNumbers: Optional[bool] = Field(default=False, description="Whether to display row numbers")
    sortable: Optional[bool] = Field(default=True, description="Whether columns should be sortable")
    pagination: Optional[bool] = Field(default=True, description="Whether to enable pagination")
    pageSize: Optional[int] = Field(default=10, description="Number of rows per page if pagination is enabled")

class TableGenerationInputSchema(BaseModel):
    """Input schema for the generate_table_data tool."""
    tableType: Literal["simple", "matrix", "comparison", "detailed"] = Field(default="simple", description="The general type or purpose of the table")
    config: TableConfig = Field(description="Configuration for the table structure and appearance")
    data: List[Dict[str, Any]] = Field(description="The array of data objects representing table rows. Keys in objects must match 'config.columns.key'.")

class TableGenerationTool(ToolSchema):
    """Tool for generating structured tabular data for financial information."""
    name: str = "generate_table_data"
    description: str = """Use this tool to generate structured JSON data for creating financial data tables.
    Specify the tableType (e.g., 'comparison', 'detailed'), provide config (title, column definitions), and the data array.
    The 'data' objects' keys must match the 'key' values defined in 'config.columns'.
    Use appropriate 'format' values in column definitions (number, currency, percentage, text, date)."""
    input_schema: Dict[str, Any] = TableGenerationInputSchema.model_json_schema()

# Keep the existing FinancialMetricGenerationTool and ComparativePeriodGenerationTool
class FinancialMetricGenerationTool(ToolSchema):
    """Tool for generating financial metrics."""
    name: str = "generate_financial_metric"
    description: str = """Generate structured financial metrics with period information.
    
Metrics should include:
- Category: The metric category (Revenue, Expenses, Assets, etc.)
- Name: The specific metric name
- Period: The time period the metric applies to
- Value: The numeric value
- Unit: The unit of measurement (%, $, etc.)
- IsEstimated: Whether the value is estimated or directly from the document
"""
    
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "The category of the financial metric"
            },
            "name": {
                "type": "string",
                "description": "The name of the financial metric"
            },
            "period": {
                "type": "string",
                "description": "The time period the metric applies to"
            },
            "value": {
                "type": "number",
                "description": "The value of the metric"
            },
            "unit": {
                "type": "string",
                "description": "The unit of measurement (%, $, etc.)"
            },
            "isEstimated": {
                "type": "boolean",
                "description": "Whether the value is estimated"
            }
        },
        "required": ["category", "name", "period", "value"]
    }

class ComparativePeriodGenerationTool(ToolSchema):
    """Tool for generating comparative period data."""
    name: str = "generate_comparative_period"
    description: str = """Generate structured data for period-over-period comparisons.
    
Comparative periods should include:
- Metric: The metric being compared
- CurrentPeriod: The current time period
- PreviousPeriod: The previous time period
- CurrentValue: The value in the current period
- PreviousValue: The value in the previous period
- Change: The absolute change
- PercentChange: The percentage change
- Trend: Whether the change is positive, negative, or neutral
"""
    
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "metric": {
                "type": "string",
                "description": "The metric being compared"
            },
            "currentPeriod": {
                "type": "string",
                "description": "The current time period"
            },
            "previousPeriod": {
                "type": "string",
                "description": "The previous time period"
            },
            "currentValue": {
                "type": "number",
                "description": "The value in the current period"
            },
            "previousValue": {
                "type": "number",
                "description": "The value in the previous period"
            },
            "change": {
                "type": "number",
                "description": "The absolute change"
            },
            "percentChange": {
                "type": "number",
                "description": "The percentage change"
            },
            "trend": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
                "description": "The trend direction"
            }
        },
        "required": ["metric", "currentPeriod", "previousPeriod", "currentValue", "previousValue"]
    }

# List of all available tools for Claude
ALL_TOOLS: List[ToolSchema] = [
    ChartGenerationTool(),
    TableGenerationTool(),
    FinancialMetricGenerationTool(),
    ComparativePeriodGenerationTool()
]

# Create dictionary versions for the API call if needed
ALL_TOOLS_DICT = [tool.model_dump(exclude_none=True) for tool in ALL_TOOLS]

# Legacy name for backward compatibility
DEFAULT_TOOLS = ALL_TOOLS

logger.info(f"Loaded {len(ALL_TOOLS)} tools for Claude API.")
logger.info(f"Tool names: {[tool.name for tool in ALL_TOOLS]}")

# Example Usage (for testing schema generation)
if __name__ == "__main__":
    chart_schema = ChartGenerationTool().model_dump_json(indent=2)
    print("Chart Generation Tool Schema:")
    print(chart_schema)

    table_schema = TableGenerationTool().model_dump_json(indent=2)
    print("\nTable Generation Tool Schema:")
    print(table_schema) 