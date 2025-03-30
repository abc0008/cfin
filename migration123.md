<Implementation_Plan>
Okay, I understand the goal. You want to migrate the PDF reading, data extraction, and visualization part of your `FDAS_APPLICATION` to follow the pattern used in the `Anthropic_Financial_Data_Analyst` application, specifically leveraging Claude's tool-calling capabilities for generating structured visualization data (charts and tables) that the frontend can directly render.

I've reviewed your initial `Implementation_Plan` and the code structure/contents of your `FDAS_APPLICATION` (`claude_service.py`, `analysis_service.py`, and the `nextjs-fdas` frontend structure). I've also analyzed the provided code dump for the `Anthropic_Financial_Data_Analyst` to understand its target flow.

**My Thoughts & Analysis:**

1.  **Target Flow Confirmation:** My analysis of the `Anthropic_Financial_Data_Analyst` code dump confirms the core flow you're aiming for:
    *   Backend receives a user query and relevant document context.
    *   Backend defines tools (e.g., `generate_graph_data`, `generate_table_data`) with specific JSON output schemas matching the frontend's expectations.
    *   Backend calls Claude with the context, query, and tools, instructing it to *use the tools* for visualization.
    *   Claude's response includes both textual analysis and structured JSON data generated via tool calls.
    *   Backend extracts this structured data.
    *   Backend sends a response to the frontend containing both the text analysis and the structured visualization JSON (likely in separate fields).
    *   Frontend renders the text using a Markdown component and the JSON using dedicated `ChartRenderer` and `TableRenderer` components, which dispatch to specific `recharts`-based components.

2.  **Current Application State:** Your `FDAS_APPLICATION` already has many necessary building blocks (FastAPI backend, Next.js frontend, `recharts`, Claude integration). The key migration task is shifting from potentially simpler Claude interactions to this structured, tool-driven visualization generation flow.

3.  **Initial Plan Review:** Your `Implementation_Plan` is a solid starting point. It correctly identifies the need for tool schema standardization, Claude service updates, API changes, and frontend component refactoring (`ChartRenderer`, `Canvas`).

**Refined Migration Plan:**

Here's a refined plan incorporating insights from both codebases and your initial plan, focusing on clarity and actionable steps:

**Phase 1: Backend Refactoring - Tool Definition and Claude Interaction**

1.  **Define Precise Tool Schemas (`models/tools.py`):**
    *   **Goal:** Define the *exact* JSON structure Claude needs to generate for charts and tables, matching what the target frontend components expect.
    *   **Action:**
        *   Analyze the `ChartData` interface in your plan (derived from `Anthropic_Financial_Data_Analyst`'s `ChartRenderer.tsx`) and potentially the props expected by individual chart components (`BarChart.tsx`, `LineChart.tsx`, etc. in `components/charts/`).
        *   Define `CHART_GENERATION_TOOL` (`generate_graph_data`) in `models/tools.py`. Ensure its `input_schema` precisely matches the structure derived above (including `chartType`, `config`, `data`, `chartConfig` keys and their nested properties).
        *   Similarly, define `TABLE_GENERATION_TOOL` (`generate_table_data`) based on the expected structure for `components/tables/TableRenderer.tsx`.
    *   **Evidence:** The target frontend's `ChartRenderer.tsx` and individual chart components dictate the required JSON structure.

2.  **Update System Prompt (`pdf_processing/claude_service.py`):**
    *   **Goal:** Instruct Claude to prioritize using the defined tools for generating visualizations.
    *   **Action:** Modify `FINANCIAL_ANALYSIS_SYSTEM_PROMPT` to be more directive:
        ```python
        FINANCIAL_ANALYSIS_SYSTEM_PROMPT = """You are an expert financial analyst. Your primary task is to analyze the provided financial document(s) and respond to the user's query.

        CRITICAL INSTRUCTION: Whenever you need to present data in a chart, graph, or table format, you MUST use the provided tools ('generate_graph_data' for charts, 'generate_table_data' for tables). Do NOT describe chart data or table data in plain text. Use the tools to generate the structured JSON required for visualization.

        Analysis Steps:
        1. Understand the user's query in the context of the provided document(s).
        2. Extract relevant financial figures, metrics, trends, and tables.
        3. If the query requires a chart or graph visualization, use the 'generate_graph_data' tool. Ensure the chartType, config, data, and chartConfig match the tool's schema.
        4. If the query requires presenting detailed data in a table, use the 'generate_table_data' tool. Ensure the tableType, config, columns, and data match the tool's schema.
        5. Provide a concise textual analysis summarizing key findings and directly answering the user's query, referencing the generated visualizations/tables where appropriate.
        """
        ```
    *   **Evidence:** This prompt explicitly mandates tool use, aligning with the target application's flow.

3.  **Refactor Claude Service (`pdf_processing/claude_service.py`):**
    *   **Goal:** Implement the tool-calling logic and process Claude's response to extract text and structured visualization data.
    *   **Action:**
        *   Create a new method, e.g., `analyze_with_visualization_tools`. This method should:
            *   Accept `document_text`, `user_query`.
            *   Load the standardized tools (`CHART_GENERATION_TOOL`, `TABLE_GENERATION_TOOL`).
            *   Call the Anthropic API (`self.client.messages.create`) with the system prompt, user message (including document text), `tools`, and `tool_choice={"type": "any"}`.
        *   Implement `_process_tool_calls` (or similar) to handle the response from Claude:
            *   Iterate through `response.content`.
            *   Extract text blocks (`type == "text"`) and concatenate them into `analysis_text`.
            *   Extract tool use blocks (`type == "tool_use"`).
            *   For each `tool_use` block, check the `name` (`generate_graph_data` or `generate_table_data`) and store the `input` JSON in appropriate lists (`charts` or `tables`).
            *   Return a dictionary like: `{"analysis_text": "...", "visualizations": { "charts": [...], "tables": [...] } }`. *Crucially, pass the tool's `input` directly without modification.*
    *   **Evidence:** The target flow requires the backend to manage the tool call and parse the structured response.

4.  **Refactor Analysis Service (`services/analysis_service.py`):**
    *   **Goal:** Integrate the new Claude service method into the analysis workflow.
    *   **Action:**
        *   Modify `_run_comprehensive_analysis` (or create a dedicated method for this flow).
        *   Call `self.claude_service.analyze_with_visualization_tools`.
        *   Structure the returned data to clearly separate `analysis_text` and `visualization_data` (containing `charts` and `tables` lists).
        *   Update the final `result_data` structure returned by the service method. Your plan's example structure looks mostly correct.
            ```python
            # Inside analysis_service.py
            async def _run_tool_based_analysis(self, document, parameters):
                # ... get document_text ...
                query = parameters.get("query", "Analyze this financial document comprehensively and generate visualizations.")
                
                claude_result = await self.claude_service.analyze_with_visualization_tools(
                    document_text=document.text,
                    user_query=query
                )
                
                result_data = {
                    "analysis_text": claude_result.get("analysis_text", ""),
                    "visualization_data": claude_result.get("visualizations", {"charts": [], "tables": []}),
                    "document_type": document.document_type.value,
                    "periods": document.periods or [],
                    "query": query
                }
                return result_data
            ```
    *   **Evidence:** This connects the new Claude interaction to the API layer.

5.  **Update/Create API Endpoint (`app/routes/analysis.py`):**
    *   **Goal:** Expose the new analysis capability via API, returning the structured data.
    *   **Action:**
        *   Modify an existing endpoint or create `/financial-analysis` (or similar).
        *   Use dependency injection to get the `AnalysisService`.
        *   Call the appropriate service method (e.g., `_run_tool_based_analysis`).
        *   Define Pydantic models in `models/api_models.py` (or a dedicated file) for the request (`document_id`, `query`) and the response structure:
            ```python
            # Example Pydantic Response Model
            class VisualizationDataResponse(BaseModel):
                charts: List[Dict[str, Any]] = [] # Use Dict for now, refine later if needed
                tables: List[Dict[str, Any]] = [] # Use Dict for now, refine later if needed

            class FinancialAnalysisResponse(BaseModel):
                analysis_text: str
                visualization_data: VisualizationDataResponse
                # ... other metadata fields if needed
            ```
        *   Return the data using the Pydantic response model.
    *   **Evidence:** This provides the necessary data structure for the frontend.

**Phase 2: Frontend Refactoring - Consuming Structured Data**

6.  **Update Frontend Types (`src/types/visualization.ts`, `src/types/index.ts`):**
    *   **Goal:** Align frontend TypeScript types with the JSON structure generated by the backend/Claude tools.
    *   **Action:** Define/update `ChartData` and `TableData` interfaces to precisely match the `input_schema` defined in `models/tools.py`. Ensure consistency with the backend's Pydantic response models.
    *   **Evidence:** Type safety ensures correct data handling.

7.  **Implement `ChartRenderer.tsx` (`src/components/charts/ChartRenderer.tsx`):**
    *   **Goal:** Create the central component to render different chart types based on the received JSON.
    *   **Action:**
        *   Implement the component as outlined in your plan.
        *   It should accept a `data: ChartData` prop.
        *   Use a `switch` statement on `data.chartType`.
        *   Import and render the specific chart components (e.g., `<BarChartComponent data={data} />`) from `src/components/charts/`. Pass the *entire* `data` object (which includes `config`, `data`, `chartConfig`) to the specific chart components.
    *   **Evidence:** This matches the target application's rendering pattern.

8.  **Implement Individual Chart Components (`src/components/charts/`):**
    *   **Goal:** Ensure each chart component correctly uses the `recharts` library based on the `ChartData` prop.
    *   **Action:** Review/update `BarChart.tsx`, `LineChart.tsx`, etc. They should destructure the `config`, `data`, and `chartConfig` from the received `data` prop to configure and render the `recharts` components.
    *   **Evidence:** `recharts` requires specific props which must be mapped from the received JSON.

9.  **Implement `TableRenderer.tsx` (`src/components/tables/TableRenderer.tsx`):**
    *   **Goal:** Render tables based on the JSON from the `generate_table_data` tool.
    *   **Action:** Create this component. It should accept a `data: TableData` prop (define this interface based on the tool schema). Use standard HTML `<table>` or a UI library table component to render the data according to `data.config.columns` and `data.data`.
    *   **Evidence:** Required for displaying structured table data.

10. **Refactor Canvas Component (`src/components/visualization/Canvas.tsx`):**
    *   **Goal:** Integrate the new renderers and fetch data from the updated API.
    *   **Action:**
        *   Modify the component to fetch data from your new backend endpoint (e.g., `/api/financial-analysis`).
        *   Expect the response structure `{ analysis_text, visualization_data: { charts, tables } }`.
        *   Render `analysis_text` (potentially using `MarkdownRenderer`).
        *   Map over `visualization_data.charts` and render `<ChartRenderer key={index} data={chart} />`.
        *   Map over `visualization_data.tables` and render `<TableRenderer key={index} data={table} />`.
    *   **Evidence:** This integrates the backend changes into the main visualization area.

11. **Update Workspace Page (`src/app/workspace/page.tsx`):**
    *   **Goal:** Ensure the main workspace page uses the refactored `Canvas` and correctly passes necessary props (like `documentId`, `query`).
    *   **Action:** Update the state management and data fetching logic within this page to work with the new API endpoint and the revised `Canvas` component.
    *   **Evidence:** This connects the user interface interaction to the new visualization flow.

**Phase 3: Testing and Refinement**

12. **Testing:**
    *   **Backend:** Write unit tests for the schema definitions, `claude_service` processing, and `analysis_service` structuring. Write integration tests for the API endpoint.
    *   **Frontend:** Write component tests for `ChartRenderer`, `TableRenderer`, and individual chart components. Write integration tests for the `Canvas` and `Workspace` page.
    *   **End-to-End:** Test the full flow with various PDF documents and user queries. Verify that visualizations are generated correctly based on tool calls.

13. **Prompt & Schema Refinement:**
    *   **Goal:** Optimize the system prompt and tool schemas based on observed results.
    *   **Action:** Analyze Claude's responses. If it fails to use tools correctly or generates incorrect JSON, refine the system prompt instructions and the `description` or `input_schema` fields in `models/tools.py`. Iterate until the desired output is consistently achieved.
    *   **Evidence:** Real-world testing often reveals nuances in how the LLM interprets instructions and schemas.


This refined plan provides more specific actions and considers the details needed to successfully implement the target application's flow within your existing structure. Let me know when you're ready to dive into specific code modifications for any of these steps.
</Implementation_Plan>


<Detailed_Code_Changes>
**Phase 1: Backend Refactoring**

**1. `backend/models/tools.py`**

```python
# backend/models/tools.py
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
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

class ChartDataItem(BaseModel):
    """Represents a single data point or category in the chart data array."""
    # Example structure: { "name": "Q1 2023", "revenue": 120000, "profit": 35000 }
    # The specific keys (like 'revenue', 'profit') are defined dynamically
    # and should match the keys in chartConfig.
    # The key used for the x-axis label must match ChartConfig.xAxisKey.
    __root__: Dict[str, Union[str, float, int, None]] = Field(description="A flexible dictionary for chart data points")

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


# --- Optional: Placeholder for other potential tools ---
# class FinancialMetricTool(...): ...
# class ComparativePeriodTool(...): ...

# List of all available tools for Claude
ALL_TOOLS: List[ToolSchema] = [
    ChartGenerationTool(),
    TableGenerationTool(),
    # Add other tools here if needed
]

# Create dictionary versions for the API call if needed
ALL_TOOLS_DICT = [tool.model_dump(exclude_none=True) for tool in ALL_TOOLS]

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
```

**2. `backend/pdf_processing/claude_service.py`**

```python
# backend/pdf_processing/claude_service.py
import os
import base64
import asyncio
import json
import re
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage, ToolUseBlock
import string
from datetime import datetime
import contextlib

from models.document import ProcessedDocument, Citation as DocumentCitation, DocumentContentType, DocumentMetadata, ProcessingStatus
from models.citation import Citation, CitationType, CharLocationCitation, PageLocationCitation, ContentBlockLocationCitation
from pdf_processing.langchain_service import LangChainService
from models.tools import ALL_TOOLS, ALL_TOOLS_DICT, ToolSchema # Import tools

# Set up logger
logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def get_anthropic_client():
    """
    Context manager to get an Anthropic client.
    This function helps avoid circular imports between modules.

    Yields:
        AsyncAnthropic: An Anthropic API client
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = AsyncAnthropic(api_key=api_key)
    try:
        yield client
    finally:
        # No need to close the client explicitly as AsyncAnthropic handles this
        pass

# LangGraph availability check remains the same
try:
    from pdf_processing.langgraph_service import LangGraphService
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph import failed: {e}. LangGraph features will be disabled.")
except Exception as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph unexpected error: {e}. LangGraph features will be disabled.")


# Refined System Prompt for Tool Usage
FINANCIAL_ANALYSIS_SYSTEM_PROMPT = """You are an expert financial analyst. Your primary task is to analyze the provided financial document(s) and respond to the user's query.

CRITICAL INSTRUCTION: Whenever you need to present data in a chart, graph, or table format, you MUST use the provided tools ('generate_graph_data' for charts, 'generate_table_data' for tables). Do NOT describe chart data or table data in plain text. Use the tools to generate the structured JSON required for visualization based on their input schemas.

Analysis Steps:
1. Understand the user's query in the context of the provided document(s).
2. Extract relevant financial figures, metrics, trends, and tables from the document(s).
3. If the query requires a chart or graph visualization, use the 'generate_graph_data' tool. Ensure the chartType, config, data, and chartConfig match the tool's input schema precisely.
4. If the query requires presenting detailed data in a table, use the 'generate_table_data' tool. Ensure the tableType, config, columns, and data match the tool's input schema precisely.
5. Provide a concise textual analysis summarizing key findings and directly answering the user's query, referencing the generated visualizations/tables where appropriate (e.g., "As shown in the Revenue Trend chart...").
"""

class ClaudeService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API service with API key from parameter or environment variable.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("Missing ANTHROPIC_API_KEY. Claude API calls will fail.")
            self.client = None
            self.langgraph_service = None # Ensure langgraph is None if client fails
            return

        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***masked***"
        logger.info(f"Initializing Claude API with key prefix: {masked_key}")

        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
        try:
            self.client = AsyncAnthropic(api_key=self.api_key)
            logger.info(f"ClaudeService initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize AsyncAnthropic client: {str(e)}")
            self.client = None

        # LangChain and LangGraph initialization remains the same...
        self.langchain_service = LangChainService()
        if LANGGRAPH_AVAILABLE:
            try:
                self.langgraph_service = LangGraphService()
                logger.info("LangGraph service successfully initialized")
            except Exception as e:
                logger.error(f"Failed to initialize LangGraph service: {str(e)}")
                self.langgraph_service = None
        else:
            logger.warning("LangGraph service not available, skipping initialization")
            self.langgraph_service = None

    # --- Existing Methods (generate_response, process_pdf, _analyze_document_type, _extract_financial_data_with_citations, etc.) ---
    # Keep the existing methods for other functionalities, but ensure they don't conflict.
    # The primary change is adding/refactoring for tool use.

    async def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        # ... (keep existing implementation or adapt if necessary) ...
        # This method is less relevant for the visualization flow but might be used elsewhere.
        pass

    async def process_pdf(self, pdf_data: bytes, filename: str) -> Tuple[ProcessedDocument, List[DocumentCitation]]:
        # ... (keep existing implementation or adapt if necessary) ...
        # This might need adjustments depending on how document content is passed to the new tool-based analysis method.
        pass

    async def _analyze_document_type(self, pdf_base64: str, filename: str) -> Tuple[DocumentContentType, List[str]]:
        # ... (keep existing implementation) ...
        pass

    async def _extract_financial_data_with_citations(self, pdf_content: Union[bytes, str], filename: str = "document.pdf", document_type: DocumentContentType = None) -> Tuple[Dict[str, Any], List[Any]]:
        # ... (keep existing implementation, maybe mark as legacy or refactor if overlapping) ...
        pass


    # --- NEW/REFACTORED Method for Tool-Based Analysis ---

    async def analyze_with_visualization_tools(
        self,
        document_text: str,
        user_query: str,
        knowledge_base: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a financial document using Claude with tool support for visualizations.

        Args:
            document_text: Text content of the financial document.
            user_query: The user's specific question or analysis request.
            knowledge_base: Optional additional context or domain knowledge.

        Returns:
            A dictionary containing:
            - "analysis_text": The textual analysis from Claude.
            - "visualizations": A dict with "charts": [...] and "tables": [...]
                                containing the structured JSON data generated by tools.
        """
        if not self.client:
            logger.error("Cannot analyze document because Claude API client is not available.")
            return {
                "analysis_text": "Error: Claude API client not configured.",
                "visualizations": {"charts": [], "tables": []}
            }

        try:
            logger.info(f"Starting analysis with visualization tools for query: '{user_query[:50]}...'")

            # Prepare the user message content, including the document text and knowledge base
            user_content_parts = [
                {"type": "text", "text": "Analyze the following financial document(s):"}
            ]

            # Add document text - using text type for simplicity here
            # In a more robust implementation, we might pass the PDF directly if available
            user_content_parts.append({
                "type": "text",
                "text": f"<financial_document>\n{document_text}\n</financial_document>"
            })

            if knowledge_base:
                user_content_parts.append({
                    "type": "text",
                    "text": f"<knowledge_base>\n{knowledge_base}\n</knowledge_base>"
                })

            user_content_parts.append({
                "type": "text",
                "text": f"\nUser Query: {user_query}"
            })

            # Prepare messages list for Claude API
            messages = [{"role": "user", "content": user_content_parts}]

            # Log request details
            logger.debug(f"Sending request to Claude with {len(messages)} message(s) and {len(ALL_TOOLS_DICT)} tools.")

            # Call Claude API with tools
            response = await self.client.messages.create(
                model=self.model,
                system=FINANCIAL_ANALYSIS_SYSTEM_PROMPT,  # Use the refined system prompt
                messages=messages,
                tools=ALL_TOOLS_DICT,
                tool_choice={"type": "any"},
                temperature=0.3, # Lower temp for more factual/structured output
                max_tokens=4096  # Maximize token limit for complex responses
            )

            logger.info("Received response from Claude API.")
            #logger.debug(f"Claude Raw Response: {response}") # Careful logging raw response

            # Process the response to extract text and tool uses
            processed_result = self._process_tool_calls(response)

            logger.info(f"Analysis complete. Text length: {len(processed_result['analysis_text'])}. "
                        f"Charts: {len(processed_result['visualizations']['charts'])}. "
                        f"Tables: {len(processed_result['visualizations']['tables'])}.")

            return processed_result

        except Exception as e:
            logger.exception(f"Error during analysis with visualization tools: {e}")
            return {
                "analysis_text": f"An error occurred during analysis: {e}",
                "visualizations": {"charts": [], "tables": []}
            }

    def _process_tool_calls(self, response: AnthropicMessage) -> Dict[str, Any]:
        """
        Processes Claude's response, extracting text and structured data from tool calls.

        Args:
            response: The AnthropicMessage object received from the API.

        Returns:
            A dictionary containing 'analysis_text' and 'visualizations' (with 'charts' and 'tables').
        """
        analysis_text = ""
        charts = []
        tables = []

        if not response.content:
            logger.warning("Claude response has no content.")
            return {
                "analysis_text": "No content received from analysis.",
                "visualizations": {"charts": [], "tables": []}
            }

        for block in response.content:
            if block.type == "text":
                analysis_text += block.text + "\n"
            elif block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                logger.info(f"Processing tool use: {tool_name}")
                #logger.debug(f"Tool Input: {json.dumps(tool_input, indent=2)}") # Log tool input for debugging

                if tool_name == "generate_graph_data":
                    try:
                        # Basic validation (Pydantic models in tools.py handle deeper validation)
                        if isinstance(tool_input, dict) and "chartType" in tool_input and "config" in tool_input and "data" in tool_input:
                            charts.append(tool_input)
                            logger.info(f"Successfully processed chart data for tool ID {block.id}")
                        else:
                            logger.warning(f"Invalid input structure for generate_graph_data tool (ID: {block.id}): Missing required keys.")
                            # Optionally, include the invalid input in the analysis text for debugging
                            analysis_text += f"\n[Note: Failed to process chart data for tool {block.id}. Input: {json.dumps(tool_input)}]\n"
                    except Exception as e:
                        logger.error(f"Error processing generate_graph_data input (ID: {block.id}): {e}")
                        analysis_text += f"\n[Note: Error processing chart data for tool {block.id}: {e}]\n"

                elif tool_name == "generate_table_data":
                    try:
                        # Basic validation
                        if isinstance(tool_input, dict) and "tableType" in tool_input and "config" in tool_input and "data" in tool_input:
                            tables.append(tool_input)
                            logger.info(f"Successfully processed table data for tool ID {block.id}")
                        else:
                            logger.warning(f"Invalid input structure for generate_table_data tool (ID: {block.id}): Missing required keys.")
                            analysis_text += f"\n[Note: Failed to process table data for tool {block.id}. Input: {json.dumps(tool_input)}]\n"
                    except Exception as e:
                        logger.error(f"Error processing generate_table_data input (ID: {block.id}): {e}")
                        analysis_text += f"\n[Note: Error processing table data for tool {block.id}: {e}]\n"
                # Add handling for other tools if necessary
                # elif tool_name == "generate_financial_metric": ...
                # elif tool_name == "generate_comparative_period": ...

            else:
                logger.warning(f"Unsupported content block type: {block.type}")

        return {
            "analysis_text": analysis_text.strip(),
            "visualizations": {
                "charts": charts,
                "tables": tables
            }
        }


    # --- Keep other helper methods like _process_claude_response, _convert_claude_citation ---
    # Ensure they are compatible or create new versions if needed.

    def _process_claude_response(self, response: AnthropicMessage) -> Dict[str, Any]:
        # ... (existing implementation, might need adjustments for tool_use blocks if called outside _process_tool_calls) ...
        pass

    def _convert_claude_citation(self, citation: Any) -> Optional[Union[Dict[str, Any], Citation]]:
        # ... (existing implementation) ...
        pass

    async def generate_response_with_langgraph(self, question: str, document_texts: List[Dict[str, Any]], conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # ... (existing implementation - This uses a different flow, maybe keep for non-tool-based interactions or refactor) ...
        pass

    async def extract_structured_financial_data(self, text: str, pdf_data: bytes = None, filename: str = None) -> Dict[str, Any]:
        # ... (existing implementation - May become less relevant if tool-based extraction is primary) ...
        pass

    async def analyze_financial_document(self, document_text: str, template: str) -> Dict[str, Any]:
         # ... (existing implementation - Mark as deprecated or adapt) ...
         pass

    async def analyze_financial_document_with_binary(self, file_binary: bytes, template: str) -> Dict[str, Any]:
         # ... (existing implementation - Mark as deprecated or adapt) ...
         pass
```

**3. `backend/services/analysis_service.py`**

```python
# backend/services/analysis_service.py
import os
import logging
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from repositories.analysis_repository import AnalysisRepository
from repositories.document_repository import DocumentRepository
from pdf_processing.claude_service import ClaudeService
from pdf_processing.financial_agent import FinancialAnalysisAgent # Keep if still used elsewhere
from models.database_models import AnalysisResult, Document

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for managing financial analysis."""

    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        document_repository: DocumentRepository
    ):
        """
        Initialize the analysis service.

        Args:
            analysis_repository: Repository for analysis operations
            document_repository: Repository for document operations
        """
        self.analysis_repository = analysis_repository
        self.document_repository = document_repository
        self.claude_service = ClaudeService()
        # Keep financial_agent if other analysis types still use it
        # self.financial_agent = FinancialAnalysisAgent()

    async def run_analysis(
        self,
        document_ids: List[str],
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Run financial analysis on one or more documents.
        Routes to the appropriate analysis method based on analysis_type.

        Args:
            document_ids: List of document IDs to analyze
            analysis_type: Type of analysis to run
            parameters: Optional parameters for the analysis

        Returns:
            Tuple of (analysis_id, result_data_with_metadata)
        """
        if parameters is None:
            parameters = {}

        if not document_ids:
            raise ValueError("No documents provided for analysis")

        # For now, handle single document analysis primarily
        document_id = document_ids[0]
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            # --- ROUTING LOGIC ---
            if analysis_type == "comprehensive" or analysis_type == "comprehensive_tools":
                logger.info(f"Routing to comprehensive tool-based analysis for document {document_id}")
                result_data = await self._run_tool_based_comprehensive_analysis(document, parameters)
                # Ensure the analysis type reflects tool usage if requested directly
                if analysis_type == "comprehensive_tools":
                    analysis_type = "comprehensive_tools"
                else:
                    # If comprehensive was called, mark it as tool-based if successful
                    # This might need adjustment based on how you distinguish
                    analysis_type = "comprehensive_tools"

            elif analysis_type == "financial_ratios":
                 # If you keep other analysis types, implement their calls here
                 # result_data = await self._run_financial_ratio_analysis(document, parameters)
                 logger.warning(f"Analysis type '{analysis_type}' might not be fully migrated to tool-based flow yet.")
                 # Fallback to comprehensive for now, or raise error
                 result_data = await self._run_tool_based_comprehensive_analysis(document, parameters)
                 analysis_type = "comprehensive_tools" # Mark as tool-based for consistency

            # Add other analysis types here...
            # elif analysis_type == "trend_analysis": ...
            # elif analysis_type == "benchmarking": ...
            # elif analysis_type == "sentiment_analysis": ...

            else:
                # Default to comprehensive tool-based analysis if type is unknown or not specifically handled
                logger.warning(f"Unknown or unhandled analysis type '{analysis_type}'. Defaulting to comprehensive tool-based analysis.")
                result_data = await self._run_tool_based_comprehensive_analysis(document, parameters)
                analysis_type = "comprehensive_tools" # Mark as tool-based

            # --- End Routing Logic ---

            # Save the analysis result
            # Ensure result_data structure matches what the DB expects (e.g., needs metrics, ratios, insights keys)
            db_result_data = {
                "analysis_text": result_data.get("analysis_text", ""),
                "metrics": result_data.get("metrics", []), # Extract metrics if returned by Claude
                "ratios": result_data.get("ratios", []), # Extract ratios if returned
                "insights": result_data.get("insights", []), # Extract insights if returned
                "visualization_data": result_data.get("visualization_data", {"charts": [], "tables": []}),
                "citation_references": result_data.get("citation_references", {}),
                "comparative_periods": result_data.get("comparative_periods", []) # Extract comparisons if returned
                # Add other fields expected by the DB model if necessary
            }

            analysis = await self.analysis_repository.create_analysis(
                document_id=document_id,
                analysis_type=analysis_type,
                result_data=db_result_data # Pass the structured data for DB
            )

            # Create an ID for the analysis response (can be different from DB ID if needed)
            analysis_response_id = f"analysis-{analysis.id}"

            # Structure the final response payload for the API
            # This structure should match the frontend expectations closely
            response_payload = {
                "id": analysis_response_id,
                "documentIds": document_ids,
                "analysisType": analysis_type,
                "timestamp": analysis.created_at.isoformat(),
                "analysisText": result_data.get("analysis_text", ""),
                "visualizationData": result_data.get("visualization_data", {"charts": [], "tables": []}),
                "metrics": result_data.get("metrics", []), # Include metrics in the response
                "ratios": result_data.get("ratios", []), # Include ratios if available
                "comparativePeriods": result_data.get("comparative_periods", []), # Include comparisons
                "insights": result_data.get("insights", []), # Include insights if available
                "citationReferences": result_data.get("citation_references", {}),
                # Add other relevant metadata
                "document_type": document.document_type.value if document.document_type else "other",
                "periods": document.periods or [],
                "query": parameters.get("query", "")
            }

            return analysis_response_id, response_payload

        except Exception as e:
            logger.error(f"Error running analysis for document {document_id}: {str(e)}", exc_info=True)
            raise # Re-raise the exception to be handled by the API layer


    async def _run_tool_based_comprehensive_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis using Claude with tool-based visualization generation.

        Args:
            document: Document to analyze
            parameters: Analysis parameters

        Returns:
            Dictionary containing the analysis results with visualizations
        """
        try:
            logger.info(f"Running comprehensive tool-based analysis for document: {document.id}")

            # Get document text - prioritize raw_text if available
            document_text = document.raw_text
            if not document_text and document.extracted_data and isinstance(document.extracted_data, dict):
                document_text = document.extracted_data.get("raw_text", "")

            if not document_text:
                logger.warning(f"No text content found for document {document.id}, attempting fallback.")
                # Fallback: create minimal text if none exists
                document_text = f"Document ID: {document.id}, Filename: {document.filename}. No text content could be extracted."
                # Consider raising an error if text is absolutely required
                # raise ValueError(f"No text content found in document {document.id}")

            # Get user query from parameters or use default
            user_query = parameters.get("query", "Provide a comprehensive financial analysis of this document, generating relevant charts and tables using the provided tools.")
            logger.info(f"User query: {user_query}")

            # Get knowledge base if available
            knowledge_base = parameters.get("knowledge_base", "")

            # Call the Claude service method that uses tools
            analysis_result = await self.claude_service.analyze_with_visualization_tools(
                document_text=document_text,
                user_query=user_query,
                knowledge_base=knowledge_base
            )

            # analysis_result is expected to contain:
            # {
            #   "analysis_text": "...",
            #   "visualizations": { "charts": [...], "tables": [...] }
            # }

            # Format the result for the analysis repository and API response
            # The structure returned by analyze_with_visualization_tools should already be close
            result_data = {
                "analysis_text": analysis_result.get("analysis_text", ""),
                "visualization_data": analysis_result.get("visualizations", {"charts": [], "tables": []}),
                # Add other fields if the tool-based method returns them (e.g., metrics)
                "metrics": analysis_result.get("metrics", []),
                "ratios": analysis_result.get("ratios", []),
                "insights": analysis_result.get("insights", []),
                "comparative_periods": analysis_result.get("comparative_periods", []),
                "citation_references": analysis_result.get("citation_references", {}),
                # Add metadata
                "document_type": document.document_type.value if document.document_type else "other",
                "periods": document.periods or [],
                "query": user_query
            }

            logger.info(f"Completed tool-based comprehensive analysis for document {document.id}")
            # Log counts for verification
            viz_data = result_data['visualization_data']
            logger.info(f"Charts generated: {len(viz_data.get('charts', []))}")
            logger.info(f"Tables generated: {len(viz_data.get('tables', []))}")
            logger.info(f"Metrics extracted: {len(result_data.get('metrics', []))}")
            logger.info(f"Comparisons extracted: {len(result_data.get('comparative_periods', []))}")


            return result_data

        except Exception as e:
            logger.error(f"Error in tool-based comprehensive analysis: {str(e)}", exc_info=True)
            # Return error information structure
            return {
                "analysis_text": f"Error during comprehensive analysis: {str(e)}",
                "visualization_data": {"charts": [], "tables": []},
                "metrics": [],
                "ratios": [],
                "insights": [f"Error: {str(e)}"],
                "comparative_periods": [],
                "citation_references": {},
                "document_type": document.document_type.value if document.document_type else "other",
                "periods": document.periods or [],
                "query": parameters.get("query", "")
            }

    # --- Keep other analysis methods (_run_financial_ratio_analysis, etc.) if needed ---
    # Mark them as potentially legacy or refactor them to use the tool-based flow if appropriate.

    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get an analysis by ID.

        Args:
            analysis_id: ID of the analysis

        Returns:
            Dictionary containing the analysis
        """
        # Strip any prefix if present
        clean_id = analysis_id
        if analysis_id.startswith('analysis-'):
            clean_id = analysis_id.replace('analysis-', '', 1) # Remove only the first instance

        # Get the analysis from the repository
        analysis = await self.analysis_repository.get_analysis(clean_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        # Format the result data to match the structure expected by the API endpoint
        result_data = analysis.result_data or {}
        visualization_data = result_data.get("visualization_data", {})
        # Ensure visualization_data is a dict
        if visualization_data is None:
             visualization_data = {}

        response_payload = {
            "id": f"analysis-{analysis.id}", # Add prefix back
            "documentIds": [analysis.document_id], # Wrap in list
            "analysisType": analysis.analysis_type,
            "timestamp": analysis.created_at.isoformat(),
            "analysisText": result_data.get("analysis_text", ""),
            "visualizationData": {
                 "charts": visualization_data.get("charts", []),
                 "tables": visualization_data.get("tables", []),
                 # Include other potential keys if they exist
                 **{k: v for k, v in visualization_data.items() if k not in ['charts', 'tables']}
            },
            "metrics": result_data.get("metrics", []),
            "ratios": result_data.get("ratios", []),
            "comparativePeriods": result_data.get("comparative_periods", []),
            "insights": result_data.get("insights", []),
            "citationReferences": result_data.get("citation_references", {}),
            # Add other relevant metadata if stored (or retrieve from document)
        }
        # Fetch document details to add metadata if needed
        document = await self.document_repository.get_document(analysis.document_id)
        if document:
            response_payload["document_type"] = document.document_type.value if document.document_type else "other"
            response_payload["periods"] = document.periods or []
            # Add query if stored (assuming it might be in parameters in result_data)
            response_payload["query"] = result_data.get("query", "")


        return response_payload

    async def list_document_analyses(
        self,
        document_id: str,
        analysis_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List analyses for a document.

        Args:
            document_id: ID of the document
            analysis_type: Optional analysis type to filter by
            limit: Maximum number of analyses to return
            offset: Starting index

        Returns:
            List of analyses summaries
        """
        analyses = await self.analysis_repository.list_document_analyses(
            document_id=document_id,
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )

        # Format the results
        formatted_analyses = []
        for analysis in analyses:
            summary = self._generate_analysis_summary(analysis.result_data or {})
            formatted_analyses.append({
                "id": f"analysis-{analysis.id}", # Add prefix
                "document_id": analysis.document_id,
                "analysis_type": analysis.analysis_type,
                "created_at": analysis.created_at.isoformat(),
                "summary": summary
            })

        return formatted_analyses

    def _generate_analysis_summary(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of analysis results.
        """
        viz_data = result_data.get("visualization_data", {})
        if viz_data is None:
            viz_data = {}

        summary = {
            "insights_count": len(result_data.get("insights", [])),
            "metrics_count": len(result_data.get("metrics", [])),
            "ratios_count": len(result_data.get("ratios", [])),
            "comparisons_count": len(result_data.get("comparative_periods", [])),
            "charts_count": len(viz_data.get("charts", [])),
            "tables_count": len(viz_data.get("tables", [])),
        }

        # Include a sample insight if available
        if result_data.get("insights") and len(result_data["insights"]) > 0:
            summary["sample_insight"] = result_data["insights"][0][:100] + "..." # Truncate

        return summary
```

**4. `backend/app/routes/analysis.py`**

```python
# backend/app/routes/analysis.py
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import re
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel # Import BaseModel

from models.analysis import AnalysisRequest, AnalysisResult as AnalysisResultResponse
from models.analysis import FinancialMetric, FinancialRatio, ComparativePeriod # Import necessary models
from models.api_models import RetryExtractionRequest # Keep if needed elsewhere
from models.visualization import VisualizationData, ChartData, TableData # Import visualization models
from repositories.analysis_repository import AnalysisRepository
from services.analysis_service import AnalysisService
from utils.database import get_db
from utils.response import handle_exception, create_error_response, get_error_type_from_status, add_cors_headers
from utils.dependencies import get_analysis_service, get_analysis_repository # Use dependency functions

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# --- Define Pydantic models for API response ---
# (These could also live in models/api_models.py or models/analysis.py)

class VisualizationDataResponse(BaseModel):
    charts: List[Any] = Field(default_factory=list) # Use Any for now, refine if possible
    tables: List[Any] = Field(default_factory=list) # Use Any for now, refine if possible
    # Include other potential keys from processing if needed
    monetaryValues: Optional[Any] = None
    percentages: Optional[Any] = None
    keywordFrequency: Optional[Any] = None

class AnalysisApiResponse(BaseModel):
    id: str
    documentIds: List[str]
    analysisType: str
    timestamp: str # Use string for ISO format
    analysisText: Optional[str] = None
    visualizationData: VisualizationDataResponse
    metrics: List[FinancialMetric] = Field(default_factory=list)
    ratios: List[FinancialRatio] = Field(default_factory=list)
    comparativePeriods: List[ComparativePeriod] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    citationReferences: Dict[str, str] = Field(default_factory=dict)
    document_type: Optional[str] = None
    periods: List[str] = Field(default_factory=list)
    query: Optional[str] = None

# --- API Endpoints ---

@router.post("/run", response_model=AnalysisApiResponse)
async def run_analysis_endpoint(
    analysis_request: AnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Run an analysis on document(s). This endpoint now routes to the
    appropriate analysis logic, primarily the tool-based comprehensive analysis.
    """
    try:
        logger.info(f"API Request - Run Analysis: Type='{analysis_request.analysisType}', Docs='{analysis_request.documentIds}', Query='{analysis_request.query}'")

        # Call the analysis service
        analysis_id, result_data = await analysis_service.run_analysis(
            document_ids=[str(doc_id) for doc_id in analysis_request.documentIds],
            analysis_type=analysis_request.analysisType,
            parameters=analysis_request.parameters or {}
        )

        # Log the structure of the result_data before validation
        logger.debug(f"Raw result_data from service: {result_data}")

        # Validate and return the response using the Pydantic model
        # The service now returns the correctly structured payload
        # Make sure the keys match exactly (camelCase vs snake_case)
        api_response = AnalysisApiResponse(
            id=result_data.get("id", analysis_id),
            documentIds=result_data.get("documentIds", analysis_request.documentIds),
            analysisType=result_data.get("analysisType", analysis_request.analysisType),
            timestamp=result_data.get("timestamp", datetime.now().isoformat()),
            analysisText=result_data.get("analysisText"),
            visualizationData=VisualizationDataResponse(
                 charts=result_data.get("visualizationData", {}).get("charts", []),
                 tables=result_data.get("visualizationData", {}).get("tables", []),
                 # Pass through other keys if they exist
                 **{k: v for k, v in result_data.get("visualizationData", {}).items() if k not in ['charts', 'tables']}
            ),
            metrics=result_data.get("metrics", []),
            ratios=result_data.get("ratios", []),
            comparativePeriods=result_data.get("comparativePeriods", []),
            insights=result_data.get("insights", []),
            citationReferences=result_data.get("citationReferences", {}),
            document_type=result_data.get("document_type"),
            periods=result_data.get("periods", []),
            query=result_data.get("query")
        )

        logger.info(f"API Response - Analysis successful: ID='{api_response.id}'")
        # Log counts for verification
        logger.info(f"Charts: {len(api_response.visualizationData.charts)}, Tables: {len(api_response.visualizationData.tables)}")
        logger.info(f"Metrics: {len(api_response.metrics)}, Ratios: {len(api_response.ratios)}, Comparisons: {len(api_response.comparativePeriods)}")

        return api_response

    except ValueError as ve:
        logger.warning(f"Value error during analysis run: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unhandled error during analysis run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run analysis: {str(e)}")

# Keep the GET endpoint for retrieving results
@router.get("/{analysis_id}", response_model=AnalysisApiResponse)
async def get_analysis_result(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Retrieve analysis results along with linked citation references.
    """
    try:
        result_data = await analysis_service.get_analysis(analysis_id)

        # Validate and return the response using the Pydantic model
        api_response = AnalysisApiResponse(
            id=result_data.get("id", analysis_id),
            documentIds=result_data.get("documentIds", []),
            analysisType=result_data.get("analysisType", "unknown"),
            timestamp=result_data.get("timestamp", datetime.now().isoformat()),
            analysisText=result_data.get("analysisText"),
            visualizationData=VisualizationDataResponse(
                 charts=result_data.get("visualizationData", {}).get("charts", []),
                 tables=result_data.get("visualizationData", {}).get("tables", []),
                  # Pass through other keys if they exist
                 **{k: v for k, v in result_data.get("visualizationData", {}).items() if k not in ['charts', 'tables']}
            ),
            metrics=result_data.get("metrics", []),
            ratios=result_data.get("ratios", []),
            comparativePeriods=result_data.get("comparativePeriods", []),
            insights=result_data.get("insights", []),
            citationReferences=result_data.get("citationReferences", {}),
            document_type=result_data.get("document_type"),
            periods=result_data.get("periods", []),
            query=result_data.get("query")
        )
        return api_response

    except ValueError as ve:
        logger.warning(f"Analysis not found: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error retrieving analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")


# --- Keep other endpoints like list_document_analyses, delete_analysis if needed ---
# Example for list_document_analyses (modify response if needed)
@router.get("/document/{document_id}", response_model=List[Dict[str, Any]])
async def list_document_analyses(
    document_id: str,
    analysis_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    List analyses summaries for a document.
    """
    try:
        analyses = await analysis_service.list_document_analyses(
            document_id=document_id,
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )
        return analyses
    except Exception as e:
        logger.error(f"Error listing analyses for document {document_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")

# Example for delete_analysis
@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository) # Use repository directly for delete
):
    """
    Delete an analysis.
    """
    # Strip prefix for DB lookup
    clean_id = analysis_id.replace('analysis-', '', 1)

    try:
        analysis = await analysis_repository.get_analysis(clean_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

        success = await analysis_repository.delete_analysis(clean_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete analysis")

        return {"message": f"Analysis {analysis_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")

```

**Phase 2: Frontend Refactoring**

**5. `nextjs-fdas/src/types/visualization.ts`**

```typescript
// nextjs-fdas/src/types/visualization.ts

/**
 * TypeScript interfaces for visualization data matching backend tool schemas.
 */

// Supported chart types
export type ChartType = 'line' | 'bar' | 'area' | 'pie' | 'multiBar' | 'scatter' | 'stackedArea';

// Supported table types
export type TableType = 'simple' | 'matrix' | 'comparison' | 'detailed';

// Format types for table columns
export type FormatType = 'number' | 'currency' | 'percentage' | 'text' | 'date';

// Configuration for individual metrics in charts
export interface MetricConfig {
  label: string;
  color?: string;
  unit?: string;      // Unit (e.g., '$', '%')
  formatter?: string; // Formatting type ('currency', 'percent', 'compact', 'number')
  precision?: number; // Decimal places
}

// Configuration for charts
export interface ChartConfig {
  title: string;
  description?: string;
  subtitle?: string;     // Optional subtitle
  xAxisKey: string;     // Key for x-axis in data objects (mandatory for most charts)
  yAxisKey?: string;    // Key for y-axis (mainly for single-series charts)
  xAxisLabel?: string;  // Label for the x-axis
  yAxisLabel?: string;  // Label for the y-axis
  showLegend?: boolean;
  legendPosition?: 'top' | 'bottom' | 'left' | 'right';
  showGrid?: boolean;
  stack?: boolean;       // For stacked bar/area charts
  colors?: string[];     // Optional list of colors
  footer?: string;       // Optional footer text
  totalLabel?: string;   // Optional label for total (e.g., in pie charts)
}

// Chart data structure
export interface ChartData {
  chartType: ChartType;
  config: ChartConfig;
  // Data is an array of objects. Keys should match xAxisKey and keys in chartConfig.
  // Example for bar/line: [{ "period": "Q1", "revenue": 100, "profit": 20 }]
  // Example for pie: [{ "name": "Segment A", "value": 50 }]
  data: Array<Record<string, any>>;
  // chartConfig maps data keys (e.g., "revenue", "profit") to their display config
  chartConfig: Record<string, MetricConfig>;
}

// Table column configuration
export interface TableColumnConfig {
  key: string;         // Key in the data objects for this column
  label: string;       // Display label for the column header
  header?: string;      // Alternative header text (often same as label)
  format?: FormatType; // Data formatting type
  width?: number;      // Optional column width
  align?: 'left' | 'center' | 'right'; // Text alignment
}

// Table configuration
export interface TableConfig {
  title: string;
  description?: string;
  subtitle?: string;    // Optional subtitle
  footer?: string;      // Optional footer text
  columns: TableColumnConfig[]; // Column definitions
  showRowNumbers?: boolean;
  sortable?: boolean;
  pagination?: boolean;
  pageSize?: number;
}

// Table data structure
export interface TableData {
  tableType: TableType;
  config: TableConfig;
  // Data is an array of objects. Keys must match 'key' in config.columns.
  data: Array<Record<string, any>>;
}

// Combined visualization data structure (received from backend)
export interface VisualizationData {
  charts: ChartData[];
  tables: TableData[];
  // Include other potential visualization types if added later
}

// Financial metric structure (often used alongside visualizations)
export interface FinancialMetric {
  category?: string;
  name: string;
  period?: string;
  value: number;
  unit?: string;
  isEstimated?: boolean;
  previousValue?: number;
  percentChange?: number;
  trend?: 'up' | 'down' | 'neutral';
  description?: string;
  highlight?: boolean;
}
```

**6. `nextjs-fdas/src/types/index.ts`** (Ensure `AnalysisResult` matches the API response)

```typescript
// nextjs-fdas/src/types/index.ts
import { ChartData, TableData, FinancialMetric, FinancialRatio, ComparativePeriod } from './analysis'; // Assuming these are defined here or imported
import { VisualizationData } from './visualization'; // Import the refined structure

// Existing interfaces (DocumentMetadata, ProcessedDocument, Citation, Message, etc.) remain largely the same.
// Adjust if backend DB models changed significantly, but focus on AnalysisResult for now.

export interface DocumentMetadata {
  id: string;
  filename: string;
  uploadTimestamp: string;
  fileSize: number;
  mimeType: string;
  userId: string;
  citationLinks?: string[];
}

export interface ProcessedDocument {
  metadata: DocumentMetadata;
  contentType: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'notes' | 'other';
  extractionTimestamp: string;
  periods: string[];
  extractedData: Record<string, any>;
  confidenceScore: number;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
  citations?: Array<Citation>;
  // Add raw_text if it's expected from backend
  raw_text?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface CitationRect {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
}

export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<CitationRect>;
  messageId?: string;
  analysisId?: string;
}

export interface Message {
  id: string;
  sessionId: string;
  timestamp: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  referencedDocuments?: string[]; // Ensure consistency with backend naming
  referencedAnalyses?: string[];  // Ensure consistency with backend naming
  citations?: Array<Citation>;    // Ensure consistency with backend naming
}

// --- UPDATED AnalysisResult ---
export interface AnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string; // ISO string format
  analysisText?: string; // Text analysis from Claude
  visualizationData: VisualizationData; // Contains charts and tables
  metrics: FinancialMetric[];
  ratios: FinancialRatio[];
  comparativePeriods?: ComparativePeriod[]; // Optional based on backend
  insights: string[]; // Or potentially a more structured insight type
  citationReferences?: Record<string, string>;
  // Optional metadata from backend
  document_type?: string;
  periods?: string[];
  query?: string;
}

// Type for FinancialRatio (if needed, define based on backend `models/analysis.py`)
export interface FinancialRatio {
  name: string;
  value: number;
  description: string;
  benchmark?: number;
  trend?: number;
}

// Type for ComparativePeriod (if needed, define based on backend `models/analysis.py`)
export interface ComparativePeriod {
    metric: string;
    currentPeriod: string;
    previousPeriod: string;
    currentValue: number;
    previousValue: number;
    change: number;
    percentChange: number;
    trend: "positive" | "negative" | "neutral";
}


// Other existing types...
// Add ClaudeCitation type if needed for raw citation data
export interface ClaudeCitation {
    type: string;
    cited_text: string;
    document_title: string;
    start_page_number?: number;
    end_page_number?: number;
    // Add other fields based on backend `models/citation.py` if necessary
}

export interface ConversationMetadata {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  documentIds: string[];
  messageCount: number;
  session_id?: string;
}
```

**7. `nextjs-fdas/src/components/charts/ChartRenderer.tsx`**

```typescript
// nextjs-fdas/src/components/charts/ChartRenderer.tsx
'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ChartData } from '@/types/visualization'; // Use the updated type

// Import specific chart components
import BarChartComponent from './BarChart'; // Assuming BarChart.tsx exports default
import LineChartComponent from './LineChart'; // Assuming LineChart.tsx exports default
import AreaChartComponent from './AreaChart'; // Assuming AreaChart.tsx exports default
import PieChartComponent from './PieChart';   // Assuming PieChart.tsx exports default
import MultiBarChartComponent from './MultiBarChart'; // Assuming MultiBarChart.tsx exports default
import ScatterChartComponent from './ScatterChart'; // Assuming ScatterChart.tsx exports default
// Import StackedArea if you have a specific component or handle it within AreaChart

interface ChartRendererProps {
  data: ChartData;
  className?: string;
  onDataPointClick?: (dataPoint: any) => void; // Optional callback for clicks
}

/**
 * ChartRenderer component acts as a dispatcher for different chart types
 * It renders the appropriate chart component based on the chartType in the data.
 */
export const ChartRenderer: React.FC<ChartRendererProps> = ({
  data,
  className = '',
  onDataPointClick
}) => {
  const { config, data: chartData, chartType, chartConfig } = data;

  // Centralize data point click handling
  const handleDataPointClick = (payload: any, index: number) => {
    if (onDataPointClick) {
      // Pass the relevant payload information
      const dataPoint = payload?.payload ? payload.payload : payload; // Adapt based on recharts event structure
      onDataPointClick(dataPoint);
    }
  };

  const renderChart = () => {
    // Pass the entire 'data' object which contains config, data, chartConfig
    // The specific components will destructure what they need.
    switch (chartType) {
      case 'bar':
        return <BarChartComponent data={data} />;
      case 'multiBar':
         // Assuming MultiBarChart handles grouped bars
        return <MultiBarChartComponent data={data} />;
      case 'line':
        return <LineChartComponent data={data} />;
      case 'area':
      case 'stackedArea': // Handle stacked area within the AreaChartComponent based on config.stack
        return <AreaChartComponent data={data} />;
      case 'pie':
        return <PieChartComponent data={data} />;
      case 'scatter':
        return <ScatterChartComponent data={data} />;
      default:
        console.warn(`Unsupported chart type: ${chartType}`);
        return <div className="text-red-500">Unsupported chart type: {chartType}</div>;
    }
  };

  return (
    <Card className={`overflow-hidden ${className}`}>
      <CardHeader>
        {config.title && <CardTitle>{config.title}</CardTitle>}
        {config.description && <CardDescription>{config.description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {chartData && chartData.length > 0 ? (
          <div className="h-[300px] w-full"> {/* Ensure container has height */}
             {/*
               Note: We pass the *entire* data object down.
               Individual chart components should be updated to accept `data: ChartData`
               and destructure `config`, `data` (as chartData), and `chartConfig` internally.
               This simplifies the renderer.
             */}
            {renderChart()}
          </div>
        ) : (
          <div className="h-[300px] w-full flex items-center justify-center text-gray-500">
            No data available for this chart.
          </div>
        )}
        {config.footer && (
          <p className="text-xs text-muted-foreground mt-2">{config.footer}</p>
        )}
      </CardContent>
    </Card>
  );
};

export default ChartRenderer; // Default export if preferred
```

**8. `nextjs-fdas/src/components/charts/*.tsx` (Example: `BarChart.tsx`)**

   *Modify each specific chart component (`BarChart.tsx`, `LineChart.tsx`, etc.) to accept the `data: ChartData` prop and use its contents.*

```typescript
// nextjs-fdas/src/components/charts/BarChart.tsx
'use client'; // Ensure client-side rendering

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from 'recharts';
import { ChartData, MetricConfig } from '@/types/visualization'; // Use updated types
import { formatValue } from '@/utils/formatters';
import { CitationTooltip, CHART_COLORS } from '../visualization/EnhancedChart'; // Import shared tooltip and colors

interface BarChartProps {
  data: ChartData; // Accept the full ChartData object
  // Remove height/width props if managed by parent or ResponsiveContainer
}

/**
 * BarChart component updated to accept ChartData structure.
 */
export default function BarChartComponent({ data }: BarChartProps) {
  // Destructure the necessary parts from the data prop
  const { config, data: chartData, chartConfig } = data;

  // Ensure chartData is valid
  if (!chartData || chartData.length === 0) {
    return <div className="text-gray-500">No data for Bar Chart.</div>;
  }

  // Determine category key (x-axis) and metric keys (bars)
  const categoryKey = config.xAxisKey || 'name'; // Default to 'name' if not specified
  const metricKeys = Object.keys(chartConfig || {}).filter(key => key !== categoryKey);

  // If chartConfig is missing or empty, try to infer metric keys from data
  if (metricKeys.length === 0 && chartData.length > 0) {
      const firstDataItem = chartData[0];
      Object.keys(firstDataItem).forEach(key => {
          if (key !== categoryKey && typeof firstDataItem[key] === 'number') {
              metricKeys.push(key);
              // Add default chartConfig if missing
              if (!chartConfig[key]) {
                  chartConfig[key] = { label: key.charAt(0).toUpperCase() + key.slice(1) };
              }
          }
      });
      console.warn("BarChart: chartConfig was missing or empty. Inferred metric keys:", metricKeys);
  }

  if (metricKeys.length === 0) {
      return <div className="text-red-500">BarChart Error: Could not determine data keys to plot. Check 'chartConfig'.</div>;
  }


  // Generate bars for each metric
  const bars = metricKeys.map((key, index) => {
    const metricConf: MetricConfig = chartConfig[key] || { label: key }; // Fallback label
    return (
      <Bar
        key={key}
        dataKey={key}
        name={metricConf.label}
        fill={metricConf.color || CHART_COLORS[index % CHART_COLORS.length]}
        stackId={config.stack ? 'a' : undefined} // Use stackId if config.stack is true
        radius={[4, 4, 0, 0]} // Optional: rounded corners
        // Add onClick handler if needed
        // onClick={(payload) => handleDataPointClick(payload, index)}
      />
    );
  });

  // Custom tooltip formatter
  const formatTooltip = (value: number, name: string) => {
    const metricKey = metricKeys.find(key => (chartConfig[key]?.label || key) === name);
    if (metricKey && chartConfig[metricKey]) {
      const metric = chartConfig[metricKey];
      return [formatValue(value, metric.formatter, metric.precision), metric.unit || ''];
    }
    // Fallback formatting
    return [value.toLocaleString(), ''];
  };

  return (
    // ResponsiveContainer handles height/width
    <ResponsiveContainer width="100%" height="100%">
      <RechartsBarChart
        data={chartData}
        margin={{ top: 5, right: 5, left: 5, bottom: 5 }} // Adjust margins as needed
      >
        {config.showGrid !== false && <CartesianGrid strokeDasharray="3 3" vertical={false} />}

        <XAxis
          dataKey={categoryKey}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          // Add Label if xAxisLabel is present in config
          //{config.xAxisLabel && <Label value={config.xAxisLabel} offset={0} position="insideBottom" />}
        />

        <YAxis
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => {
            // Format Y-axis ticks based on the first metric's config
            if (metricKeys.length > 0 && chartConfig[metricKeys[0]]) {
              const firstMetric = chartConfig[metricKeys[0]];
              // Use compact formatter for Y-axis to save space
              return formatValue(value, 'compact', firstMetric.precision ?? 1);
            }
            return value.toLocaleString();
          }}
          // Add Label if yAxisLabel is present in config
          //{config.yAxisLabel && <Label value={config.yAxisLabel} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />}
        />

        <Tooltip
            formatter={formatTooltip}
            cursor={{ fill: 'rgba(200, 200, 200, 0.2)' }}
            content={<CitationTooltip />} // Use shared tooltip component
        />

        {config.showLegend !== false && (
          <Legend
            verticalAlign={config.legendPosition === 'top' ? 'top' : 'bottom'}
            align={config.legendPosition === 'left' ? 'left' : config.legendPosition === 'right' ? 'right' : 'center'}
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
        )}

        {bars}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}

// --- Repeat similar updates for LineChart.tsx, AreaChart.tsx, PieChart.tsx, etc. ---
// Ensure they all accept `data: ChartData` and use `config`, `chartData`, `chartConfig`.
```

**9. `nextjs-fdas/src/components/tables/TableRenderer.tsx`** (New File)

```typescript
// nextjs-fdas/src/components/tables/TableRenderer.tsx
'use client';

import React, { useState } from 'react';
import { TableData, TableColumnConfig } from '@/types/visualization'; // Use the updated types
import { formatValue } from '@/utils/formatters';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface TableRendererProps {
  data: TableData;
  className?: string;
  // Removed height/width, let the container manage size
}

/**
 * TableRenderer component for displaying structured tabular data.
 */
export default function TableRenderer({ data, className = '' }: TableRendererProps) {
  const { config, data: tableData } = data;
  const [currentPage, setCurrentPage] = useState(0);

  // Ensure data is valid
  if (!tableData) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{config?.title || 'Table'}</CardTitle>
          {config?.description && <CardDescription>{config.description}</CardDescription>}
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-4">No table data available.</p>
        </CardContent>
      </Card>
    );
  }

  const columns: TableColumnConfig[] = config?.columns || [];
  const rowsPerPage = config?.pageSize || 10;
  const showPagination = config?.pagination !== false && tableData.length > rowsPerPage;
  const totalPages = showPagination ? Math.ceil(tableData.length / rowsPerPage) : 1;

  const currentRows = showPagination
    ? tableData.slice(currentPage * rowsPerPage, (currentPage + 1) * rowsPerPage)
    : tableData;

  const goToNextPage = () => setCurrentPage(prev => Math.min(prev + 1, totalPages - 1));
  const goToPrevPage = () => setCurrentPage(prev => Math.max(prev - 1, 0));

  const formatCell = (value: any, column: TableColumnConfig) => {
    if (value === undefined || value === null || value === '') {
      return '—'; // Use em dash for empty cells
    }
    return formatValue(value, column.format, column.format === 'currency' || column.format === 'number' ? 2 : undefined);
  };

  return (
    <Card className={`overflow-hidden ${className}`}>
      <CardHeader>
        {config?.title && <CardTitle>{config.title}</CardTitle>}
        {config?.description && <CardDescription>{config.description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                {config?.showRowNumbers && (
                  <th scope="col" className="px-3 py-3 text-left font-medium text-gray-500 uppercase tracking-wider w-12">#</th>
                )}
                {columns.map((column) => (
                  <th
                    key={column.key}
                    scope="col"
                    className={`px-3 py-3 text-${column.align || 'left'} font-medium text-gray-500 uppercase tracking-wider`}
                    style={{ width: column.width ? `${column.width}px` : 'auto' }}
                  >
                    {column.header || column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentRows.length > 0 ? (
                currentRows.map((row, rowIndex) => (
                  <tr key={`row-${rowIndex}`} className="hover:bg-gray-50">
                    {config?.showRowNumbers && (
                      <td className="px-3 py-2 whitespace-nowrap text-gray-500">
                        {currentPage * rowsPerPage + rowIndex + 1}
                      </td>
                    )}
                    {columns.map((column) => (
                      <td
                        key={`cell-${rowIndex}-${column.key}`}
                        className={`px-3 py-2 whitespace-nowrap text-gray-700 text-${column.align || 'left'}`}
                      >
                        {formatCell(row[column.key], column)}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={columns.length + (config?.showRowNumbers ? 1 : 0)}
                    className="px-3 py-4 text-center text-gray-500"
                  >
                    No data available for this table.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        {showPagination && (
          <div className="flex items-center justify-between border-t border-gray-200 pt-3 mt-4">
            <div className="text-xs text-gray-600">
              Page {currentPage + 1} of {totalPages} ({tableData.length} rows total)
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={goToPrevPage}
                disabled={currentPage === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-1" /> Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={goToNextPage}
                disabled={currentPage === totalPages - 1}
              >
                Next <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}

        {config?.footer && (
          <p className="text-xs text-muted-foreground mt-3 pt-3 border-t">{config.footer}</p>
        )}
      </CardContent>
    </Card>
  );
}
```

**10. `nextjs-fdas/src/components/visualization/Canvas.tsx`**

```typescript
// nextjs-fdas/src/components/visualization/Canvas.tsx
'use client';

import React from 'react';
import { AnalysisResult } from '@/types'; // Ensure this uses the updated structure
import { ChartData, TableData } from '@/types/visualization'; // Use updated types
import ChartRenderer from '../charts/ChartRenderer'; // Use the new dispatcher
import TableRenderer from '../tables/TableRenderer'; // Use the new table renderer
import MetricGrid from '../metrics/MetricGrid';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart2, Table, TrendingUp, Info } from 'lucide-react';
import { AnalysisBlock } from '../analysis/AnalysisBlock'; // Reuse AnalysisBlock for insights/text

interface CanvasProps {
  analysisResults: AnalysisResult[]; // Expect potentially multiple results, use the latest one
  messages?: any[]; // Keep messages if needed for context, but primary data is analysisResults
  loading?: boolean;
  error?: Error | string | null; // Allow null for error state
  onCitationClick?: (highlightId: string) => void; // Keep citation click handler
}

/**
 * Canvas component updated to render structured visualization data.
 */
const Canvas: React.FC<CanvasProps> = ({
  analysisResults,
  messages = [],
  loading,
  error,
  onCitationClick
}) => {
  // Use the latest analysis result
  const latestAnalysis = analysisResults && analysisResults.length > 0
    ? analysisResults[analysisResults.length - 1]
    : null;

  // Extract visualization data directly from the latest analysis result
  const visualizationData = latestAnalysis?.visualizationData;
  const analysisText = latestAnalysis?.analysisText;
  const metrics = latestAnalysis?.metrics || [];
  const insights = latestAnalysis?.insights || []; // Assuming insights are strings for now

  const charts = visualizationData?.charts || [];
  const tables = visualizationData?.tables || [];

  // Loading state
  if (loading) {
    return (
      <div role="status" aria-label="Loading visualizations" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 w-40 bg-gray-200 rounded mb-4" />
          <div className="h-80 w-full bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div role="alert" className="flex items-center justify-center p-8 bg-red-50 rounded-lg min-h-[600px]">
        <div className="text-red-500 text-center">
          <h3 className="font-semibold mb-2">Error loading analysis</h3>
          <p className="text-sm">{error.toString()}</p>
        </div>
      </div>
    );
  }

  // No analysis data available state
  if (!latestAnalysis) {
    return (
      <div role="status" aria-label="No analysis data" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <p className="text-gray-500">No analysis data available. Run an analysis or ask a question.</p>
      </div>
    );
  }

  // Determine if there's anything to display
  const hasVisualizations = charts.length > 0 || tables.length > 0;
  const hasMetrics = metrics.length > 0;
  const hasInsights = insights.length > 0;
  const hasAnalysisText = analysisText && analysisText.trim().length > 0;

  return (
    <div role="main" className="w-full h-full overflow-y-auto p-4 space-y-6 bg-gray-50">

      {/* Display Analysis Text if available */}
      {hasAnalysisText && (
        <AnalysisBlock
          block={{
            id: `text-${latestAnalysis.id}`,
            title: "Analysis Summary",
            description: `Generated based on query: "${latestAnalysis.query || 'N/A'}"`,
            chartType: 'none', // Indicate no chart
            chartData: [],
            insights: [], // Insights are handled separately below
            timestamp: latestAnalysis.timestamp,
            // Assume text content is here, maybe format it?
            analysisText: analysisText
          }}
          showCitations={false} // Citations are usually within the text itself
        />
      )}

      {/* Display Key Metrics */}
      {hasMetrics && (
        <MetricGrid
          metrics={metrics}
          title="Key Financial Metrics"
        />
      )}

       {/* Display Key Insights */}
      {hasInsights && (
         <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center mb-3">
                <Info className="h-5 w-5 mr-2 text-indigo-600"/> Key Insights
            </h3>
            <ul className="space-y-2">
              {insights.map((insight, index) => (
                <li key={`insight-${index}`} className="text-sm text-gray-700 bg-indigo-50 p-2 rounded border-l-4 border-indigo-400">
                  {insight}
                </li>
              ))}
            </ul>
         </div>
      )}

      {/* Display Visualizations (Charts and Tables) */}
      {hasVisualizations ? (
        <Tabs defaultValue="charts" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="charts" disabled={charts.length === 0}>
              <BarChart2 className="h-4 w-4 mr-2"/> Charts ({charts.length})
            </TabsTrigger>
            <TabsTrigger value="tables" disabled={tables.length === 0}>
              <Table className="h-4 w-4 mr-2"/> Tables ({tables.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="charts" className="mt-4">
            {charts.length > 0 ? (
              <div className="grid grid-cols-1 gap-4">
                {charts.map((chart, index) => (
                  <ChartRenderer
                    key={`chart-${index}-${chart.config.title}`}
                    data={chart}
                    // Pass onCitationClick if needed by tooltip or interactions
                    // onDataPointClick={(dataPoint) => onCitationClick?.(dataPoint?.citation?.highlightId)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">No charts generated for this analysis.</div>
            )}
          </TabsContent>

          <TabsContent value="tables" className="mt-4">
            {tables.length > 0 ? (
              <div className="space-y-4">
                {tables.map((table, index) => (
                  <TableRenderer
                    key={`table-${index}-${table.config.title}`}
                    data={table}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">No tables generated for this analysis.</div>
            )}
          </TabsContent>
        </Tabs>
      ) : (
         // If no visualizations but we have text/metrics/insights, show a message
         (hasAnalysisText || hasMetrics || hasInsights) && (
           <div className="text-center text-gray-500 py-8">No specific charts or tables were generated for this analysis.</div>
         )
      )}

      {/* Fallback if nothing was generated at all */}
      {!hasAnalysisText && !hasMetrics && !hasInsights && !hasVisualizations && (
         <div className="text-center text-gray-500 py-8">No analysis results available.</div>
      )}
    </div>
  );
};

export default Canvas;
```

**11. `nextjs-fdas/src/app/workspace/page.tsx`** (Focus on state & API call)

```typescript
// nextjs-fdas/src/app/workspace/page.tsx
'use client'

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'; // Corrected import path
import { FileText, BarChart2, Upload, FileUp, Zap, ChevronRight, FileSearch } from 'lucide-react';
import { ChatInterface } from '@/components/chat/ChatInterface'; // Corrected import path
import { UploadForm } from '@/components/document/UploadForm'; // Corrected import path
import dynamic from 'next/dynamic';
import { ProcessedDocument, AnalysisResult, Message, Citation } from '@/types'; // Use updated AnalysisResult
import { conversationApi } from '@/lib/api/conversation';
import { analysisApi } from '@/lib/api/analysis'; // Use updated analysis API
import Canvas from '@/components/visualization/Canvas'; // Use updated Canvas
import { AnalysisControls } from '@/components/analysis/AnalysisControls'; // Corrected import path
import { useSearchParams } from 'next/navigation'; // Import useSearchParams

// Import PDFViewer component with dynamic import
const PDFViewer = dynamic(
  () => import('../../components/document/PDFViewer').then(mod => mod.PDFViewer),
  { ssr: false }
);

export default function Workspace() {
  const searchParams = useSearchParams(); // Get search params

  const [activeTab, setActiveTab] = useState<'document' | 'analysis'>('document');
  const [messages, setMessages] = useState<Message[]>([]); // Use Message type
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isChatLoading, setIsChatLoading] = useState(false); // Separate loading state for chat
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]); // Use updated AnalysisResult type
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState<boolean>(false);
  const [highlightId, setHighlightId] = useState<string | null>(null);

  // Initialize conversation session
  useEffect(() => {
    let mounted = true;
    const initSession = async () => {
      if (!sessionId) {
        try {
          setIsChatLoading(true);
          const response = await conversationsApi.createConversation({ title: 'New Analysis Session' });
          if (mounted) {
            setSessionId(response); // Assuming createConversation returns just the ID now
            console.log('Created conversation session:', response);
          }
        } catch (error) {
          console.error('Error initializing session:', error);
          if (mounted) {
            // Add error message to chat state
            const errorMsg: Message = {
              id: `system-${Date.now()}`, role: 'system', content: `Error initializing chat: ${error instanceof Error ? error.message : 'Unknown error'}`,
              timestamp: new Date().toISOString(), sessionId: 'error-session'
            };
            setMessages(prev => [...prev, errorMsg]);
          }
        } finally {
          if (mounted) setIsChatLoading(false);
        }
      }
    };
    initSession();
    return () => { mounted = false; };
  }, [sessionId]); // Keep sessionId dependency to prevent re-running if already set


  // Load initial document if specified in URL
  useEffect(() => {
    const docId = searchParams.get('document');
    const shouldAnalyze = searchParams.get('analyze') === 'true';

    if (docId && !selectedDocument) {
      const fetchInitialDocument = async () => {
        try {
          console.log(`Fetching initial document: ${docId}`);
          // Fetch the full document data including text needed for analysis
          const doc = await documentsApi.getDocument(docId);
          setSelectedDocument(doc);
          console.log(`Initial document loaded: ${doc.metadata.filename}`);
          if (shouldAnalyze) {
             // Automatically trigger initial analysis if analyze=true
             await runAnalysis(doc.metadata.id, 'comprehensive_tools', undefined, "Provide a comprehensive financial analysis");
          }
        } catch (error) {
          console.error(`Error fetching initial document ${docId}:`, error);
           setAnalysisError(`Failed to load document ${docId}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      };
      fetchInitialDocument();
    }
  }, [searchParams, selectedDocument]); // Re-run if searchParams change


  const runAnalysis = async (
      documentId: string,
      analysisType: string = 'comprehensive_tools', // Default to tool-based
      knowledgeBase?: string,
      userQuery?: string
  ) => {
      if (!documentId) return;

      setAnalysisLoading(true);
      setAnalysisError(null);

      try {
          const parameters: Record<string, any> = {};
          if (knowledgeBase) parameters.knowledge_base = knowledgeBase;
          // Pass the query within parameters as expected by backend model
          if (userQuery) parameters.query = userQuery;

          console.log(`Running analysis type '${analysisType}' for doc ${documentId} with query: "${userQuery || 'Default'}"`);

          // Use the updated analysis API method
          const result: AnalysisResult = await analysisApi.runAnalysis({
              documentIds: [documentId],
              analysisType: analysisType,
              parameters: parameters, // Pass parameters here
              query: userQuery // Pass query directly if analysisApi expects it
          });

          setAnalysisResults(prev => [...prev, result]); // Add new result

          // Add system message about analysis completion
          const analysisCompletionMessage: Message = {
              id: `msg-${Date.now()}`, role: 'system',
              content: `I've completed the ${analysisType} analysis${userQuery ? ` for: "${userQuery}"` : ''}. Results are in the Analysis tab.`,
              timestamp: new Date().toISOString(), sessionId: sessionId || 'unknown-session',
              referencedDocuments: [documentId], referencedAnalyses: [result.id]
          };
          setMessages(prev => [...prev, analysisCompletionMessage]);

          setActiveTab('analysis'); // Switch to analysis tab

      } catch (error) {
          console.error('Error running analysis:', error);
          const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred during analysis';
          setAnalysisError(errorMsg);

          // Add error message to chat
          const analysisErrorMessage: Message = {
              id: `msg-${Date.now()}`, role: 'system',
              content: `Error performing analysis: ${errorMsg}`,
              timestamp: new Date().toISOString(), sessionId: sessionId || 'unknown-session',
              referencedDocuments: [documentId], referencedAnalyses: []
          };
          setMessages(prev => [...prev, analysisErrorMessage]);
      } finally {
          setAnalysisLoading(false);
      }
  };

  // Automatically run analysis when a new document is selected
  useEffect(() => {
    if (selectedDocument && !analysisResults.some(r => r.documentIds.includes(selectedDocument.metadata.id))) {
      console.log(`New document selected (${selectedDocument.metadata.filename}), running initial analysis...`);
      // Use the updated runAnalysis function
      runAnalysis(selectedDocument.metadata.id, 'comprehensive_tools', undefined, "Provide a comprehensive financial analysis of this document.");
    }
  }, [selectedDocument]); // Depend only on selectedDocument

  const handleSendMessage = async (messageText: string) => {
    if (!sessionId) {
      console.error("No valid session ID available");
      // Add error message to chat
      const errorMsg: Message = {
          id: `system-${Date.now()}`, role: 'system', content: 'Error: No active session. Please refresh.',
          timestamp: new Date().toISOString(), sessionId: 'error-session'
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }

    try {
      setIsChatLoading(true); // Use chat-specific loading state

      const userMessage: Message = {
        id: `user-${Date.now()}`, role: 'user', content: messageText,
        timestamp: new Date().toISOString(), sessionId: sessionId,
        referencedDocuments: selectedDocument ? [selectedDocument.metadata.id] : []
      };
      setMessages(prev => [...prev, userMessage]);

      // Use the updated API call from conversationsApi
      const response = await conversationsApi.sendMessage(
        messageText,
        sessionId,
        selectedDocument ? [selectedDocument.metadata.id] : []
        // Pass citations if needed: message.citations
      );

      // Add AI response
      setMessages(prev => [...prev, response]);

    } catch (error) {
      console.error("Error sending message:", error);
      // Add error message to chat
      const errorMsg: Message = {
          id: `system-${Date.now()}`, role: 'system', content: `Error sending message: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date().toISOString(), sessionId: sessionId
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleUploadSuccess = async (document: ProcessedDocument) => {
      setSelectedDocument(document);
      setShowUploadForm(false);

      // Add system message about successful upload
      const uploadMsg: Message = {
          id: `system-${Date.now()}`, role: 'system',
          content: `Successfully uploaded: ${document.metadata.filename}`,
          timestamp: new Date().toISOString(), sessionId: sessionId || 'unknown-session',
          referencedDocuments: [document.metadata.id]
      };
      setMessages((prev: any) => [...prev, uploadMsg]);

      // Automatically associate with conversation if session exists
      if (sessionId) {
          try {
              await conversationsApi.addDocumentToConversation(sessionId, document.metadata.id);
              console.log(`Associated document ${document.metadata.id} with session ${sessionId}`);
          } catch (error) {
              console.error(`Failed to associate document with session:`, error);
              // Add error message to chat
              const assocErrorMsg: Message = {
                  id: `system-${Date.now()}`, role: 'system', content: `Error associating document with session: ${error instanceof Error ? error.message : 'Unknown error'}`,
                  timestamp: new Date().toISOString(), sessionId: sessionId
              };
              setMessages(prev => [...prev, assocErrorMsg]);
          }
      }
      // The useEffect for selectedDocument will trigger the analysis
  };


  const handleUploadError = (error: Error) => {
      setAnalysisError(`Upload failed: ${error.message}`);
      const errorMsg: Message = {
          id: `system-${Date.now()}`, role: 'system', content: `Error uploading document: ${error.message}`,
          timestamp: new Date().toISOString(), sessionId: sessionId || 'unknown-session'
      };
      setMessages((prev: any) => [...prev, errorMsg]);
  };

  const handleCitationClick = (highlightId: string) => {
    console.log(`Citation clicked, highlight ID: ${highlightId}`);
    setHighlightId(highlightId);
    setActiveTab('document');
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-indigo-50 to-white">
      {/* Header remains the same */}
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-indigo-700 mb-2">Analysis Workspace</h1>
        <p className="text-gray-600 mb-6">
          Upload financial documents, ask questions, and analyze the data.
        </p>
      </div>

      {/* Main workspace area */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 px-4 pb-6 min-h-0"> {/* Added min-h-0 */}
        {/* Left side: Chat Interface */}
        <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden h-[calc(100vh-220px)]"> {/* Adjusted height */}
          {/* Chat Header */}
          <div className="p-4 border-b border-gray-100 bg-gray-50 rounded-t-xl flex-shrink-0">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center">
                  <FileSearch className="h-5 w-5 mr-2 text-indigo-600" />
                  Interactive Chat
              </h2>
          </div>
          {/* Chat Messages and Input */}
          <div className="flex-1 overflow-hidden"> {/* Let ChatInterface manage internal scroll */}
              <ChatInterface
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  activeDocuments={selectedDocument ? [selectedDocument.metadata.id] : []}
                  isLoading={isChatLoading} // Use chat-specific loading
                  onCitationClick={(citation: Citation) => handleCitationClick(citation.highlightId)}
                  // Pass onNavigateToHighlight if PDFViewer supports it
              />
          </div>
        </div>


        {/* Right side: Document View / Analysis */}
        <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden h-[calc(100vh-220px)]"> {/* Adjusted height */}
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'document' | 'analysis')} className="flex flex-col h-full">
            {/* Tab List */}
            <TabsList className="grid grid-cols-2 p-1 bg-gray-100 rounded-t-xl flex-shrink-0">
              <TabsTrigger value="document">
                  <FileText className="h-4 w-4 mr-1.5" /> Document
              </TabsTrigger>
              <TabsTrigger value="analysis">
                  <BarChart2 className="h-4 w-4 mr-1.5" /> Analysis
              </TabsTrigger>
            </TabsList>

            {/* Document Tab */}
            <TabsContent value="document" className="flex-1 overflow-y-auto p-0 m-0"> {/* Let content scroll */}
                {showUploadForm ? (
                    <div className="p-6">
                        <h2 className="text-xl font-semibold text-indigo-700 mb-4">Upload Document</h2>
                        <UploadForm
                            onUploadSuccess={handleUploadSuccess}
                            onUploadError={handleUploadError}
                            sessionId={sessionId || undefined}
                        />
                        <Button variant="outline" onClick={() => setShowUploadForm(false)} className="mt-4">Cancel</Button>
                    </div>
                ) : selectedDocument ? (
                    // PDFViewer needs to be wrapped in a container that allows scrolling if needed
                    <div className="h-full w-full">
                        <PDFViewer
                            document={selectedDocument}
                            highlightId={highlightId}
                            // Pass callbacks if implemented
                        />
                    </div>
                ) : (
                    <div className="h-full flex items-center justify-center p-6">
                        <div className="text-center max-w-md">
                            <div className="bg-indigo-100 p-3 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                                <FileUp className="h-8 w-8 text-indigo-600" />
                            </div>
                            <h3 className="text-lg font-semibold text-indigo-700 mb-2">No document selected</h3>
                            <p className="text-gray-600 mb-6">Upload a document to view it here and start analysis.</p>
                            <Button onClick={() => setShowUploadForm(true)}>
                                <Upload className="h-5 w-5 mr-2" /> Upload Document
                            </Button>
                        </div>
                    </div>
                )}
            </TabsContent>

            {/* Analysis Tab */}
            <TabsContent value="analysis" className="flex-1 overflow-y-auto p-0 m-0"> {/* Let content scroll */}
                {selectedDocument && (
                    <div className="p-4 border-b sticky top-0 bg-white z-10">
                        <AnalysisControls
                            isLoading={analysisLoading}
                            onRunAnalysis={(analysisType, knowledgeBase, userQuery) => {
                                runAnalysis(selectedDocument.metadata.id, analysisType, knowledgeBase, userQuery);
                            }}
                        />
                    </div>
                )}
                 {/* Pass the full analysisResults array to Canvas */}
                <div className="p-4">
                    <Canvas
                        analysisResults={analysisResults}
                        error={analysisError}
                        loading={analysisLoading}
                        onCitationClick={handleCitationClick}
                        messages={messages} // Pass messages if Canvas needs them
                    />
                </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
```

**12. `nextjs-fdas/src/lib/api/analysis.ts`**

```typescript
// nextjs-fdas/src/lib/api/analysis.ts
import { AnalysisResult } from '@/types'; // Use updated type
import { apiService } from './apiService';
import { AnalysisResultSchema } from '@/validation/schemas'; // Use backend schema for validation if needed

// Function to handle API errors (keep existing or refine)
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error instanceof Error) {
      throw error; // Re-throw ApiError instances or standard Errors
  }
  // Fallback for unknown error types
  throw new Error('An error occurred while communicating with the server');
};

interface RunAnalysisRequest {
  documentIds: string[];
  analysisType: string;
  parameters?: Record<string, any>;
  query?: string; // Add query directly if needed by the API model
}

export const analysisApi = {
  /**
   * Run financial analysis on document(s). Uses the new tool-based endpoint.
   */
  async runAnalysis(requestData: RunAnalysisRequest): Promise<AnalysisResult> {
    try {
      console.log(`API Call - runAnalysis: Type='${requestData.analysisType}', Docs='${requestData.documentIds}', Query='${requestData.query}'`);

      // Call the appropriate endpoint - assuming /api/analysis/run handles tool-based requests now
      // The backend router might need adjustment if you used a different path like /run-with-tools
      const response = await apiService.post<AnalysisResult>(
        '/api/analysis/run', // Use the primary endpoint, assuming it handles tools
        requestData, // Send the full request data including query and parameters
        AnalysisResultSchema // Validate against the Pydantic schema if needed
      );

      console.log(`API Response - runAnalysis successful for ID: ${response.id}`);
      return response;
    } catch (error) {
      console.error('API Error during runAnalysis:', error);
      throw handleApiError(error); // Rethrow standardized error
    }
  },

  /**
   * Get a specific analysis result by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    try {
      // Ensure the analysis ID includes the prefix if needed by the backend
      const correctedAnalysisId = analysisId.startsWith('analysis-') ? analysisId : `analysis-${analysisId}`;
      console.log(`API Call - getAnalysis: ID='${correctedAnalysisId}'`);

      const response = await apiService.get<AnalysisResult>(
        `/api/analysis/${correctedAnalysisId}`, // Use the ID with prefix
        AnalysisResultSchema // Validate against schema
      );

      console.log(`API Response - getAnalysis successful for ID: ${response.id}`);
      return response;
    } catch (error) {
      console.error(`API Error during getAnalysis for ID ${analysisId}:`, error);
      throw handleApiError(error);
    }
  },

  // --- Keep other methods like getChartData, getEnhancedAnalysis if they are still relevant ---
  // Adjust them as needed to match any backend changes.
  // async getChartData(...) { ... }
  // async getEnhancedAnalysis(...) { ... }
};
```

**Summary of Changes:**

1.  **Backend:**
    *   Defined precise tool schemas (`models/tools.py`).
    *   Updated Claude system prompt for mandatory tool use (`pdf_processing/claude_service.py`).
    *   Implemented `analyze_with_visualization_tools` and `_process_tool_calls` in `claude_service.py` to handle tool interactions.
    *   Refactored `analysis_service.py` to call the new Claude method and structure the response.
    *   Updated the `/api/analysis/run` endpoint in `app/routes/analysis.py` to handle the tool-based flow and return the structured `AnalysisApiResponse`.
2.  **Frontend:**
    *   Aligned TypeScript types (`types/visualization.ts`, `types/index.ts`) with the backend's tool schemas and API response.
    *   Implemented `ChartRenderer.tsx` to dispatch to specific chart components.
    *   Updated specific chart components (like `BarChart.tsx`) to accept the unified `ChartData` prop.
    *   Created `TableRenderer.tsx` to display table data.
    *   Refactored `Canvas.tsx` to fetch data from the updated API and use the new renderers.
    *   Updated `workspace/page.tsx` to manage state and API calls for the new flow.
    *   Updated `lib/api/analysis.ts` to call the correct endpoint and expect the new structured response.

This implementation provides the full code for the key files involved in the migration. Remember to install any new dependencies (`pip install ...` or `npm install ...`) if required, restart your backend and frontend servers, and test thoroughly.
</Detailed_Code_Changes>