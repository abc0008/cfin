import os
import logging
from typing import Dict, List, Any, Optional, Tuple, TypedDict, Annotated
from enum import Enum
import json
import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool, BaseTool, ToolException
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.graph.message import add_messages

from models.document import Citation

logger = logging.getLogger(__name__)

# Define state and data structures
class AgentState(TypedDict):
    """State definition for financial analysis agent."""
    messages: List[Any]  # The message history
    documents: Dict[str, Any]  # Document metadata and content
    citations: List[Dict[str, Any]]  # Citations extracted from documents
    financial_data: Dict[str, Any]  # Structured financial data
    analysis_results: Dict[str, Any]  # Results of financial analysis
    tools_results: List[Dict[str, Any]]  # Results from tool executions
    chart_data: Optional[Dict[str, Any]]  # Data for visualization
    current_task: Optional[str]  # Current task being performed

class ChartType(str, Enum):
    """Types of financial charts."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"

# Tool definitions
class FinancialTools:
    """Tools for financial analysis."""
    
    @tool("calculate_financial_ratio")
    def calculate_financial_ratio(self, ratio_name: str, numerator_value: float, denominator_value: float, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate a financial ratio from numerator and denominator values.
        Provides ratio result and interpretation.
        
        Args:
            ratio_name: Name of the ratio to calculate (e.g., 'Current Ratio', 'Debt-to-Equity')
            numerator_value: Value for the numerator
            denominator_value: Value for the denominator
            description: Description of what this ratio represents (optional)
            
        Returns:
            Dictionary containing ratio calculation results and interpretation
        """
        try:
            ratio_value = numerator_value / denominator_value
            
            # Default description if none provided
            description = description
            if not description:
                if "current" in ratio_name.lower():
                    description = "Measures the company's ability to pay short-term obligations"
                elif "debt" in ratio_name.lower() and "equity" in ratio_name.lower():
                    description = "Measures the company's financial leverage"
                elif "profit" in ratio_name.lower() or "margin" in ratio_name.lower():
                    description = "Measures the company's profitability as a percentage of revenue"
                else:
                    description = f"The {ratio_name} financial metric"
            
            # Simple interpretation based on common ratios
            interpretation = ""
            if "current" in ratio_name.lower():
                if ratio_value < 1:
                    interpretation = "Current ratio below 1 indicates potential liquidity issues."
                elif ratio_value < 2:
                    interpretation = "Current ratio between 1-2 is generally acceptable but could be better."
                else:
                    interpretation = "Current ratio above 2 indicates strong liquidity position."
            elif "debt" in ratio_name.lower() and "equity" in ratio_name.lower():
                if ratio_value < 0.5:
                    interpretation = "Low debt-to-equity ratio indicates conservative financing."
                elif ratio_value < 1.5:
                    interpretation = "Moderate debt-to-equity ratio indicating balanced financing."
                else:
                    interpretation = "High debt-to-equity ratio indicates higher financial risk."
            elif "profit" in ratio_name.lower() or "margin" in ratio_name.lower():
                if ratio_value < 0.05:
                    interpretation = "Low profit margin indicating potential profitability issues."
                elif ratio_value < 0.15:
                    interpretation = "Moderate profit margin in line with many industries."
                else:
                    interpretation = "High profit margin indicating strong profitability."
            
            return {
                "ratio_name": ratio_name,
                "value": round(ratio_value, 4),
                "description": description,
                "interpretation": interpretation,
                "numerator": numerator_value,
                "denominator": denominator_value
            }
        except ZeroDivisionError:
            raise ToolException(f"Cannot calculate {ratio_name}: division by zero")
        except Exception as e:
            raise ToolException(f"Error calculating ratio: {str(e)}")
    
    @tool("generate_chart_data")
    def generate_chart_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for financial charts and visualizations.
        Returns structured data that can be used by charting libraries.
        """
        try:
            chart_data = {
                "type": input_data["chart_type"],
                "title": input_data["title"],
                "x_axis": input_data["x_axis_label"],
                "y_axis": input_data["y_axis_label"],
                "data": input_data["data_series"]
            }
            
            # Add chart-specific properties
            if input_data["chart_type"] == ChartType.PIE:
                chart_data["total"] = sum(item.get("value", 0) for item in input_data["data_series"])
                chart_data["data"] = [
                    {
                        "name": item.get("name", ""),
                        "value": item.get("value", 0),
                        "percentage": (item.get("value", 0) / chart_data["total"]) * 100 if chart_data["total"] > 0 else 0
                    }
                    for item in input_data["data_series"]
                ]
            
            if input_data["chart_type"] in [ChartType.LINE, ChartType.BAR, ChartType.AREA]:
                # Organize time series data
                periods = sorted(set(item.get("period") for item in input_data["data_series"] if "period" in item))
                series_names = sorted(set(item.get("series") for item in input_data["data_series"] if "series" in item))
                
                if periods and series_names:
                    formatted_data = []
                    for period in periods:
                        entry = {"period": period}
                        for series in series_names:
                            value = next(
                                (item.get("value", 0) for item in input_data["data_series"] 
                                 if item.get("period") == period and item.get("series") == series), 
                                0
                            )
                            entry[series] = value
                        formatted_data.append(entry)
                    
                    chart_data["data"] = formatted_data
                    chart_data["series"] = series_names
            
            return chart_data
        except Exception as e:
            raise ToolException(f"Error generating chart data: {str(e)}")
    
    @tool("analyze_financial_trend")
    def analyze_financial_trend(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends in financial data over time.
        Determines growth rate and trend direction.
        """
        try:
            if not data or len(data) < 2:
                raise ToolException("Need at least two data points to analyze trend")
            
            # Sort data by period
            sorted_data = sorted(data, key=lambda x: x.get("period", ""))
            
            metric = sorted_data[0].get("metric", "Financial Metric")
            periods = [item.get("period", f"Period {i+1}") for i, item in enumerate(sorted_data)]
            values = [item.get("value", 0) for item in sorted_data]
            
            # Calculate growth rate
            if values[0] == 0:
                growth_rate = 0
            else:
                growth_rate = (values[-1] - values[0]) / values[0]
            
            # Determine trend direction
            if growth_rate > 0.05:  # 5% threshold for upward trend
                trend_direction = "up"
            elif growth_rate < -0.05:  # -5% threshold for downward trend
                trend_direction = "down"
            else:
                trend_direction = "stable"
            
            return {
                "metric": metric,
                "values": values,
                "periods": periods,
                "growth_rate": round(growth_rate, 4),
                "trend_direction": trend_direction
            }
        except Exception as e:
            if isinstance(e, ToolException):
                raise e
            raise ToolException(f"Error analyzing financial trend: {str(e)}")
    
    @tool("extract_financial_fact")
    def extract_financial_fact(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract specific financial facts from the document.
        Returns facts related to a specific financial topic.
        """
        # This is a placeholder implementation that would normally access document data
        # In a real application, this would search through document content
        facts = {
            "revenue": [
                {"fact": "Revenue increased by 12.5% year-over-year", "confidence": 0.95},
                {"fact": "Q4 revenue was $24.5M", "confidence": 0.98},
                {"fact": "Recurring revenue represents 72% of total revenue", "confidence": 0.93}
            ],
            "expenses": [
                {"fact": "Operating expenses grew 8% year-over-year", "confidence": 0.94},
                {"fact": "R&D expenses represent 18% of total expenses", "confidence": 0.92},
                {"fact": "Sales & Marketing is the largest expense category", "confidence": 0.91}
            ],
            "profitability": [
                {"fact": "Gross margin improved to 68% in Q4", "confidence": 0.97},
                {"fact": "Net profit margin was 12.4%", "confidence": 0.95},
                {"fact": "EBITDA grew 15% year-over-year", "confidence": 0.92}
            ]
        }
        
        topic = input_data.get("topic", "").lower()
        
        if topic in facts:
            result = {"topic": input_data.get("topic", ""), "facts": facts[topic]}
            if input_data.get("time_period"):
                # Filter facts by time period (in a real implementation)
                result["time_period"] = input_data.get("time_period")
            return result
        else:
            return {"topic": input_data.get("topic", ""), "facts": []}

# Financial analysis agent
class FinancialAnalysisAgent:
    """Financial analysis agent using LangGraph."""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        # Initialize LLM
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-latest")
        self.llm = ChatAnthropic(
            model=self.model,
            temperature=0.1,
            anthropic_api_key=api_key
        )
        
        # Initialize tools
        self.tools = FinancialTools()
        self.tool_list = [
            self.tools.calculate_financial_ratio,
            self.tools.generate_chart_data,
            self.tools.analyze_financial_trend,
            self.tools.extract_financial_fact
        ]
        self.tool_executor = ToolExecutor(self.tool_list)
        
        # Initialize system prompts
        self._init_system_prompts()
        
        # Build agent graph
        self.workflow = self._build_workflow()
    
    def _init_system_prompts(self):
        """Initialize system prompts for the agent."""
        
        self.orchestrator_prompt = """You are a Financial Analysis Orchestrator that helps analyze financial documents.
Your job is to determine the user's intent and route to the appropriate financial analysis function.

Choose from the following functions based on the user's request:
1. "analyze_financial_metrics" - Calculate and analyze key financial metrics (like revenue growth, profit margins)
2. "generate_visualization" - Create data visualization for financial trends
3. "extract_document_insights" - Extract key insights from documents
4. "answer_question" - Directly answer the user's question if sufficient information is available

Based on the user's message, choose the most appropriate function.
Return ONLY the function name, nothing else."""
        
        self.metrics_analysis_prompt = """You are a Financial Metrics Analyst specialized in analyzing financial metrics from documents.
Use the available financial data and documents to perform detailed metric analysis.

You have access to the following tools:
- calculate_financial_ratio: Calculate financial ratios and get interpretations
- analyze_financial_trend: Analyze trends in financial metrics over time
- extract_financial_fact: Extract specific facts about financial metrics

Think carefully about which financial metrics would be most relevant for the user's question.
When using tools, provide clear rationale for the metrics you're calculating and analyzing.
Always cite sources from the original documents when possible."""
        
        self.visualization_prompt = """You are a Financial Data Visualization expert specialized in creating meaningful charts.
Use the available financial data to create appropriate visualizations.

You have access to the following tools:
- generate_chart_data: Create data for charts based on financial metrics
- analyze_financial_trend: Analyze trends in financial metrics to determine what to visualize

Think carefully about the most appropriate chart type for the financial data:
- Bar charts: Good for comparing categorical data
- Line charts: Best for showing trends over time
- Pie charts: Useful for showing composition of a whole
- Area charts: Effective for showing cumulative totals over time
- Scatter plots: Good for showing relationships between variables

Choose appropriate labels, titles, and data points to make the visualization informative."""
        
        self.insights_prompt = """You are a Financial Insights Analyst specialized in extracting key insights from financial documents.
Your job is to extract the most important insights from financial documents and provide context.

You have access to the following tools:
- extract_financial_fact: Extract specific facts about financial topics
- analyze_financial_trend: Analyze trends in financial metrics

Think about what the most important insights are based on the user's question.
Focus on extracting insights that are:
1. Directly relevant to the user's question
2. Supported by data in the documents
3. Insightful and not just repetitions of raw numbers
4. Properly contextualized with industry benchmarks when available

Always cite the specific parts of the document where your insights come from."""
        
        self.final_response_prompt = """You are a Financial Analysis Assistant that provides comprehensive answers to questions about financial documents.
Now that analysis has been performed, provide a complete, well-structured response to the user's question.

Your response should:
1. Directly address the user's question
2. Incorporate all relevant financial metrics, visualizations, and insights
3. Present information in a clear, logical structure
4. Cite specific parts of the original documents
5. Add context and interpretation to make the information actionable

If charts or visualizations were created, describe what they show and what insights can be drawn from them.
Be thorough but concise, and focus on the most important information relevant to the user's question."""
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow for financial analysis."""
        # Create the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("orchestrator", self.route_intent)
        workflow.add_node("analyze_financial_metrics", self.analyze_financial_metrics)
        workflow.add_node("generate_visualization", self.generate_visualization)
        workflow.add_node("extract_document_insights", self.extract_document_insights)
        workflow.add_node("answer_question", self.answer_question)
        
        # Add edges
        workflow.add_conditional_edges(
            "orchestrator",
            self.get_next_step,
            {
                "analyze_financial_metrics": "analyze_financial_metrics",
                "generate_visualization": "generate_visualization",
                "extract_document_insights": "extract_document_insights",
                "answer_question": "answer_question",
                END: END
            }
        )
        
        workflow.add_edge("analyze_financial_metrics", "generate_visualization")
        workflow.add_edge("generate_visualization", "extract_document_insights")
        workflow.add_edge("extract_document_insights", "answer_question")
        workflow.add_edge("answer_question", END)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Compile the workflow
        return workflow.compile()
    
    def route_intent(self, state: AgentState) -> AgentState:
        """Route to the appropriate next step based on user intent."""
        # Get the last user message
        messages = state["messages"]
        last_user_message = None
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                last_user_message = message.content
                break
        
        if not last_user_message:
            # Default to answering directly if no user message found
            new_state = state.copy()
            new_state["current_task"] = "answer_question"
            return new_state
        
        # Prepare the orchestrator prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.orchestrator_prompt),
            ("human", f"User request: {last_user_message}\n\nWhat financial analysis function should I use to address this request?")
        ])
        
        # Get routing decision from the LLM
        chain = prompt | self.llm | StrOutputParser()
        route = chain.invoke({})
        
        # Clean up the response
        route = route.strip().lower()
        if "analyze_financial_metrics" in route:
            task = "analyze_financial_metrics"
        elif "generate_visualization" in route:
            task = "generate_visualization"
        elif "extract_document_insights" in route:
            task = "extract_document_insights"
        else:
            task = "answer_question"
        
        # Update the state with the current task
        new_state = state.copy()
        new_state["current_task"] = task
        return new_state
    
    def get_next_step(self, state: AgentState) -> Dict[str, Any]:
        """Determine the next step in the workflow."""
        current_task = state.get("current_task")
        
        if current_task == "analyze_financial_metrics":
            return {"next": "analyze_financial_metrics"}
        elif current_task == "generate_visualization":
            return {"next": "generate_visualization"}
        elif current_task == "extract_document_insights":
            return {"next": "extract_document_insights"}
        elif current_task == "answer_question":
            return {"next": "answer_question"}
        else:
            # Default to answering the question
            return {"next": "answer_question"}
    
    def analyze_financial_metrics(self, state: AgentState) -> AgentState:
        """Analyze financial metrics using the metrics analysis tools."""
        # Create a system message with the metrics analysis prompt
        messages = state["messages"]
        system_message = SystemMessage(content=self.metrics_analysis_prompt)
        
        # Add context about available documents and financial data
        documents_info = "Available financial documents:\n"
        for doc_id, doc in state.get("documents", {}).items():
            documents_info += f"- {doc.get('filename', 'Unnamed document')}\n"
        
        financial_data_info = "Available financial data:\n"
        for category, data in state.get("financial_data", {}).items():
            financial_data_info += f"- {category.capitalize()}: {data}\n"
        
        context_message = SystemMessage(content=f"{documents_info}\n{financial_data_info}")
        
        # Get tools description
        tools_description = "You have access to the following tools:\n"
        for tool in self.tool_list:
            tools_description += f"- {tool.name}: {tool.description}\n"
        
        tools_message = SystemMessage(content=tools_description)
        
        # Combine messages for the LLM
        combined_messages = [system_message, context_message, tools_message] + messages
        
        # Get the analysis steps from the LLM
        tool_message = self.llm.invoke(combined_messages)
        
        # Parse the tools to use
        parsed_tools = []
        try:
            import re
            # Look for tool calls in the format: calculate_financial_ratio({"ratio_name": "...", ...})
            tool_calls = re.finditer(r'(\w+)\(({[^}]+})\)', tool_message.content)
            
            for match in tool_calls:
                tool_name = match.group(1)
                tool_args = json.loads(match.group(2))
                parsed_tools.append({"name": tool_name, "arguments": tool_args})
        except Exception as e:
            logger.error(f"Error parsing tool calls: {str(e)}")
        
        # Execute the tools
        tools_results = []
        for tool in parsed_tools:
            try:
                result = self.tool_executor.execute(
                    tool["name"], 
                    tool["arguments"]
                )
                tools_results.append({
                    "tool": tool["name"],
                    "arguments": tool["arguments"],
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error executing tool {tool['name']}: {str(e)}")
                tools_results.append({
                    "tool": tool["name"],
                    "arguments": tool["arguments"],
                    "error": str(e)
                })
        
        # Update the state with the current task
        new_state = state.copy()
        new_state["tools_results"] = state.get("tools_results", []) + tools_results
        
        # Analyze the results to extract financial metrics
        analysis_results = {}
        for tool_result in tools_results:
            if tool_result.get("tool") == "calculate_financial_ratio" and "result" in tool_result:
                result = tool_result["result"]
                if "ratio_name" in result and "value" in result:
                    if "ratios" not in analysis_results:
                        analysis_results["ratios"] = []
                    analysis_results["ratios"].append(result)
            
            elif tool_result.get("tool") == "analyze_financial_trend" and "result" in tool_result:
                result = tool_result["result"]
                if "trends" not in analysis_results:
                    analysis_results["trends"] = []
                analysis_results["trends"].append(result)
            
            elif tool_result.get("tool") == "extract_financial_fact" and "result" in tool_result:
                result = tool_result["result"]
                if "facts" not in analysis_results:
                    analysis_results["facts"] = []
                analysis_results["facts"].extend(result.get("facts", []))
        
        new_state["analysis_results"] = analysis_results
        
        # Add to message history
        new_state["messages"] = add_messages(
            new_state["messages"],
            AIMessage(content=f"I've analyzed the financial metrics and found {len(tools_results)} relevant results. Now I'll prepare visualizations based on these metrics.")
        )
        
        return new_state
    
    def generate_visualization(self, state: AgentState) -> AgentState:
        """Generate financial visualizations based on the financial data and analysis results."""
        # Create a system message with the visualization prompt
        system_message = SystemMessage(content=self.visualization_prompt)
        
        # Get tools description
        tools_description = "You have access to the following tools:\n"
        for tool in self.tool_list:
            if tool.name in ["generate_chart_data", "analyze_financial_trend"]:
                tools_description += f"- {tool.name}: {tool.description}\n"
        
        tools_message = SystemMessage(content=tools_description)
        
        # Add context about available analysis results
        analysis_results = state.get("analysis_results", {})
        chart_data = state.get("chart_data")
        
        context = "Financial Analysis Results:\n"
        
        if "ratios" in analysis_results:
            context += "\nFinancial Ratios:\n"
            for ratio in analysis_results["ratios"]:
                context += f"- {ratio.get('ratio_name', 'Unnamed ratio')}: {ratio.get('value', 'N/A')}\n"
        
        if "trends" in analysis_results:
            context += "\nFinancial Trends:\n"
            for trend in analysis_results["trends"]:
                context += f"- {trend.get('metric', 'Unnamed metric')}: {trend.get('trend_direction', 'N/A')} trend with {trend.get('growth_rate', 'N/A')} growth rate\n"
        
        context_message = SystemMessage(content=context)
        
        # Combine messages for the LLM
        combined_messages = [system_message, tools_message, context_message] + state["messages"]
        
        # Get visualization suggestion from the LLM
        vis_message = self.llm.invoke(combined_messages)
        
        # Update the state
        new_state = state.copy()
        
        # Parse the visualization tools to use
        parsed_tools = []
        try:
            import re
            # Look for tool calls in the format: generate_chart_data({"chart_type": "...", ...})
            tool_calls = re.finditer(r'(\w+)\(({[^}]+})\)', vis_message.content)
            
            for match in tool_calls:
                tool_name = match.group(1)
                if tool_name == "generate_chart_data":
                    tool_args = json.loads(match.group(2))
                    parsed_tools.append({"name": tool_name, "arguments": tool_args})
        except Exception as e:
            logger.error(f"Error parsing visualization tool calls: {str(e)}")
        
        # Execute the visualization tools
        chart_data = None
        for tool in parsed_tools:
            try:
                result = self.tool_executor.execute(
                    tool["name"], 
                    tool["arguments"]
                )
                
                if tool["name"] == "generate_chart_data":
                    chart_data = result
                    break  # Use the first successful chart
            except Exception as e:
                logger.error(f"Error generating chart data: {str(e)}")
        
        # If no charts were generated, create a default chart
        if not chart_data and "ratios" in analysis_results:
            try:
                # Create a default bar chart for ratios
                ratios = analysis_results["ratios"]
                chart_data = self.tool_executor.execute(
                    "generate_chart_data",
                    {
                        "chart_type": "bar",
                        "x_axis_label": "Ratio",
                        "y_axis_label": "Value",
                        "data_series": [
                            {"name": ratio.get("ratio_name", f"Ratio {i}"), "value": ratio.get("value", 0)}
                            for i, ratio in enumerate(ratios)
                        ],
                        "title": "Financial Ratios"
                    }
                )
            except Exception as e:
                logger.error(f"Error generating default chart: {str(e)}")
        
        # Update the state
        new_state["chart_data"] = chart_data
        
        # Add to message history
        chart_message = "I've prepared a visualization based on the financial analysis."
        if chart_data:
            chart_message += f" Generated a {chart_data.get('type', 'chart')} chart titled '{chart_data.get('title', 'Financial Data')}'."
        new_state["messages"] = add_messages(
            new_state["messages"],
            AIMessage(content=chart_message)
        )
        
        return new_state
    
    def extract_document_insights(self, state: AgentState) -> AgentState:
        """Extract key insights from financial documents."""
        # Create a system message with the insights prompt
        system_message = SystemMessage(content=self.insights_prompt)
        
        # Add context about available citations
        citations = state.get("citations", [])
        citations_info = "Available citations from documents:\n"
        for i, citation in enumerate(citations[:10]):  # Limit to first 10 citations
            citations_info += f"{i+1}. {citation.get('text', 'No text')} (Page {citation.get('page', 'N/A')})\n"
        
        if len(citations) > 10:
            citations_info += f"... and {len(citations) - 10} more citations\n"
        
        context_message = SystemMessage(content=citations_info)
        
        # Combine messages for the LLM
        combined_messages = [system_message, context_message] + state["messages"]
        
        # Get insights from the LLM
        insights_message = self.llm.invoke(combined_messages)
        
        # Update the state
        new_state = state.copy()
        
        # Parse insights and add to analysis results
        if "analysis_results" not in new_state:
            new_state["analysis_results"] = {}
        
        # Extract insights from the message
        insights = []
        
        # Simple parsing - in a real app we'd use a more robust approach
        lines = insights_message.content.split("\n")
        current_insight = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                if current_insight:
                    insights.append(current_insight)
                current_insight = line[1:].strip()
            elif current_insight and line:
                current_insight += " " + line
        
        if current_insight:
            insights.append(current_insight)
        
        # If no insights were extracted, use the whole message
        if not insights and insights_message.content.strip():
            insights = [insights_message.content.strip()]
        
        # Add insights to analysis results
        new_state["analysis_results"]["insights"] = insights
        
        # Add to message history
        insight_summary = f"I've extracted {len(insights)} key insights from the documents."
        new_state["messages"] = add_messages(
            new_state["messages"],
            AIMessage(content=insight_summary)
        )
        
        return new_state
    
    def answer_question(self, state: AgentState) -> AgentState:
        """Generate the final response to the user's question."""
        # Create a system message with the final response prompt
        system_message = SystemMessage(content=self.final_response_prompt)
        
        # Add context about analysis results
        analysis_results = state.get("analysis_results", {})
        chart_data = state.get("chart_data")
        
        context = "Financial Analysis Results:\n"
        
        if "ratios" in analysis_results:
            context += "\nFinancial Ratios:\n"
            for ratio in analysis_results["ratios"]:
                context += f"- {ratio.get('ratio_name', 'Unnamed ratio')}: {ratio.get('value', 'N/A')}"
                if "interpretation" in ratio:
                    context += f" ({ratio['interpretation']})"
                context += "\n"
        
        if "trends" in analysis_results:
            context += "\nFinancial Trends:\n"
            for trend in analysis_results["trends"]:
                context += f"- {trend.get('metric', 'Unnamed metric')}: {trend.get('trend_direction', 'N/A')} trend with {trend.get('growth_rate', 'N/A')} growth rate\n"
        
        if "insights" in analysis_results:
            context += "\nKey Insights:\n"
            for i, insight in enumerate(analysis_results["insights"]):
                context += f"{i+1}. {insight}\n"
        
        if chart_data:
            context += f"\nVisualization Generated:\n- Type: {chart_data.get('type', 'Chart')}\n- Title: {chart_data.get('title', 'Financial Data')}\n"
        
        context_message = SystemMessage(content=context)
        
        # Combine messages for the LLM
        combined_messages = [system_message, context_message] + state["messages"]
        
        # Generate the final response
        final_response = self.llm.invoke(combined_messages)
        
        # Update the state
        new_state = state.copy()
        new_state["messages"] = add_messages(
            new_state["messages"],
            final_response
        )
        
        return new_state
    
    async def process_financial_query(
        self, 
        query: str,
        documents: Dict[str, Any],
        citations: List[Dict[str, Any]],
        financial_data: Dict[str, Any],
        history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a financial query through the agent workflow.
        
        Args:
            query: User's financial question
            documents: Document metadata and content
            citations: Citations extracted from documents
            financial_data: Structured financial data
            history: Previous conversation history
            
        Returns:
            Dictionary with the response and additional information
        """
        if history is None:
            history = []
            
        # Convert history to message format
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Set up initial state
        initial_state = {
            "messages": messages,
            "documents": documents,
            "citations": citations,
            "financial_data": financial_data,
            "analysis_results": {},
            "tools_results": [],
            "chart_data": None,
            "current_task": None
        }
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Extract the final assistant message
            final_message = None
            for msg in reversed(final_state["messages"]):
                if isinstance(msg, AIMessage):
                    final_message = msg
                    break
            
            if not final_message:
                return {
                    "error": "Failed to generate a response",
                    "content": "I couldn't generate a proper analysis at this time."
                }
            
            # Return the response and additional data
            return {
                "content": final_message.content,
                "analysis_results": final_state["analysis_results"],
                "chart_data": final_state["chart_data"],
                "citations_used": final_state.get("citations_used", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing financial query: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "content": "I encountered an error while analyzing the financial data. Please try again with a different question."
            }