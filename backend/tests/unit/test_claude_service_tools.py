import pytest
import base64
import json
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from typing import Dict, List, Any

import asyncio
from pdf_processing.claude_service import ClaudeService
from models.document import ProcessedDocument, DocumentContentType, DocumentMetadata, ProcessingStatus
from models.tools import ChartGenerationTool, TableGenerationTool


# Helper class to simulate Anthropic content blocks for tool use
class ToolUseBlock:
    def __init__(self, id, name, input_data):
        self.type = "tool_use"
        self.id = id
        self.name = name
        self.input = input_data


# Helper class to simulate Anthropic text content blocks
class TextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text
        self.citations = []


@pytest.fixture
def sample_pdf_data():
    """Create mock PDF data for testing"""
    return b"%PDF-1.5\nSample PDF content for testing"


@pytest.fixture
def mock_tool_response():
    """Create a mock response with tool use"""
    text_block = TextBlock(
        text="I've analyzed the financial document and extracted the following data."
    )
    
    # Chart tool use
    chart_data = {
        "chartType": "bar",
        "config": {
            "title": "Revenue by Year",
            "description": "Annual revenue trends",
            "xAxisKey": "year"
        },
        "data": [
            {"year": "2021", "value": 1000000},
            {"year": "2022", "value": 1200000},
            {"year": "2023", "value": 1500000}
        ],
        "chartConfig": {
            "value": {
                "label": "Revenue",
                "color": "#0066CC"
            }
        }
    }
    
    chart_tool = ToolUseBlock(
        id="tool_1",
        name="generate_graph_data",
        input_data=chart_data
    )
    
    # Table tool use
    table_data = {
        "tableType": "simple",
        "config": {
            "title": "Financial Metrics",
            "description": "Key financial metrics",
            "columns": [
                {"key": "metric", "label": "Metric"},
                {"key": "value", "label": "Value", "format": "currency"}
            ]
        },
        "data": [
            {"metric": "Total Revenue", "value": 1500000},
            {"metric": "Net Income", "value": 350000}
        ]
    }
    
    table_tool = ToolUseBlock(
        id="tool_2",
        name="generate_table_data",
        input_data=table_data
    )
    
    # Create the mock response
    response = Mock()
    response.content = [text_block, chart_tool, table_tool]
    return response


class TestClaudeServiceTools:
    """Test suite for Claude API tool use methods"""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Setup environment and mocks for each test"""
        # Ensure the ANTHROPIC_API_KEY is set for tests
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")
        
        # Create the service
        self.service = ClaudeService()
        
        # Setup the AsyncAnthropic client mock
        self.mock_client = AsyncMock()
        self.service.client = self.mock_client
        
        # Patch the tools support to be True for testing
        monkeypatch.setattr("pdf_processing.claude_service.TOOLS_SUPPORT", True)

    @pytest.mark.asyncio
    async def test_generate_response_with_tools(self, mock_tool_response):
        """Test generating a response with tools"""
        # Setup
        self.mock_client.messages.create = AsyncMock(return_value=mock_tool_response)
        
        # Execute
        response = await self.service.generate_response_with_tools(
            system_prompt="You are a financial analysis assistant.",
            messages=[{"role": "user", "content": "Analyze this financial data"}],
            tools=[ChartGenerationTool(), TableGenerationTool()]
        )
        
        # Verify
        assert self.mock_client.messages.create.called
        
        # Use a more robust way to check for tool use in call args
        call_args = self.mock_client.messages.create.call_args[1]
        assert "tools" in call_args
        
        assert "I've analyzed" in response["content"]
        assert len(response["tool_uses"]) == 2
        assert response["tool_uses"][0]["name"] == "generate_graph_data"
        assert response["tool_uses"][1]["name"] == "generate_table_data"
        
    @pytest.mark.asyncio
    async def test_generate_response_with_tools_no_tools_support(self, monkeypatch):
        """Test fallback when tools support is not available"""
        # Setup - TOOLS_SUPPORT is False
        monkeypatch.setattr("pdf_processing.claude_service.TOOLS_SUPPORT", False)
        
        # Mock regular response method
        original_generate_response = self.service.generate_response
        self.service.generate_response = AsyncMock(return_value="Regular response without tools")
        
        # Execute
        response = await self.service.generate_response_with_tools(
            system_prompt="You are a financial analysis assistant.",
            messages=[{"role": "user", "content": "Analyze this financial data"}],
            tools=[ChartGenerationTool(), TableGenerationTool()]
        )
        
        # Verify
        assert response == "Regular response without tools"
        assert self.service.generate_response.called
        
        # Restore original method
        self.service.generate_response = original_generate_response
        
    @pytest.mark.asyncio
    async def test_extract_financial_data_with_tools(self, sample_pdf_data, mock_tool_response):
        """Test extracting financial data with tools"""
        # Setup
        self.service.generate_response_with_tools = AsyncMock(return_value={
            "content": json.dumps({
                "metrics": [{"name": "Revenue", "value": 1500000}],
                "ratios": [{"name": "Profit Margin", "value": 0.25}]
            }),
            "tool_uses": [
                {
                    "type": "tool_use",
                    "name": "generate_graph_data",
                    "input": {
                        "chartType": "bar",
                        "config": {"title": "Revenue", "description": "Revenue by year"},
                        "data": [{"year": "2023", "value": 1500000}],
                        "chartConfig": {"value": {"label": "Revenue"}}
                    }
                },
                {
                    "type": "tool_use",
                    "name": "generate_table_data",
                    "input": {
                        "tableType": "simple",
                        "config": {
                            "title": "Financial Metrics",
                            "description": "Key metrics",
                            "columns": [{"key": "metric", "label": "Metric"}]
                        },
                        "data": [{"metric": "Revenue", "value": 1500000}]
                    }
                }
            ]
        })
        
        # Execute
        result = await self.service.extract_financial_data_with_tools(
            pdf_content=sample_pdf_data,
            filename="financial_report.pdf",
            document_type=DocumentContentType.BALANCE_SHEET
        )
        
        # Verify
        assert self.service.generate_response_with_tools.called
        assert "metrics" in result
        assert "visualization_data" in result
        assert "visualizationData" in result
        assert len(result["visualization_data"]["charts"]) == 1
        assert len(result["visualization_data"]["tables"]) == 1
        assert "bar" in str(result["visualization_data"])
        assert "monetaryValues" in result["visualizationData"]
        
    @pytest.mark.asyncio
    async def test_extract_financial_data_with_tools_fallback(self, sample_pdf_data, monkeypatch):
        """Test fallback to regular extraction when tools not supported"""
        # Setup - TOOLS_SUPPORT is False
        monkeypatch.setattr("pdf_processing.claude_service.TOOLS_SUPPORT", False)
        
        # Mock the regular extraction method
        self.service._extract_financial_data_with_citations = AsyncMock(return_value=(
            {"financial_data": {"revenue": 1500000}},
            []
        ))
        
        # Execute
        result = await self.service.extract_financial_data_with_tools(
            pdf_content=sample_pdf_data,
            filename="financial_report.pdf",
            document_type=DocumentContentType.BALANCE_SHEET
        )
        
        # Verify
        assert self.service._extract_financial_data_with_citations.called
        assert "financial_data" in result
        assert result["financial_data"]["revenue"] == 1500000
        
    @pytest.mark.asyncio
    async def test_extract_financial_data_with_tools_error_handling(self, sample_pdf_data):
        """Test error handling in tool-based extraction"""
        # Setup - Generate response raises an exception
        self.service.generate_response_with_tools = AsyncMock(side_effect=Exception("API error"))
        
        # Execute
        result = await self.service.extract_financial_data_with_tools(
            pdf_content=sample_pdf_data,
            filename="financial_report.pdf",
            document_type=DocumentContentType.BALANCE_SHEET
        )
        
        # Verify
        assert "error" in result
        assert "API error" in result["error"]
        assert "visualization_data" in result
        assert "visualizationData" in result 