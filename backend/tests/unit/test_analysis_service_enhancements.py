import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from typing import Dict, List, Any, Optional

from services.analysis_service import AnalysisService
from models.document import ProcessedDocument, DocumentMetadata, DocumentContentType, ProcessingStatus
from models.tools import ChartGenerationTool, TableGenerationTool
from models.visualization import ChartData, TableData, VisualizationData
from pdf_processing.claude_service import ClaudeService


@pytest.fixture
def sample_document():
    """Create a sample document for testing"""
    return ProcessedDocument(
        id="doc123",
        file_hash="abc123",
        metadata=DocumentMetadata(
            filename="financial_report_2023.pdf",
            filetype="application/pdf",
            size=12345,
            document_type=DocumentContentType.BALANCE_SHEET,
            upload_time="2023-11-01T12:00:00Z",
            page_count=10
        ),
        processing_status=ProcessingStatus.COMPLETED,
        extracted_text="Sample financial report text with revenue of $1,500,000.",
        extracted_data={
            "metrics": [
                {"name": "Revenue", "value": 1500000, "unit": "USD"}
            ],
            "visualization_data": {
                "charts": [
                    {
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
                ],
                "tables": [
                    {
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
                ]
            },
            "visualizationData": {
                "monetaryValues": [
                    {"title": "Revenue", "value": 1500000, "change": 0.25},
                    {"title": "Net Income", "value": 350000, "change": 0.15}
                ],
                "keywordFrequency": [
                    {"keyword": "revenue", "frequency": 15},
                    {"keyword": "profit", "frequency": 10}
                ]
            }
        }
    )


@pytest.fixture
def mock_claude_service():
    """Create a mock Claude service"""
    service = AsyncMock(spec=ClaudeService)
    
    # Mock the tool-based extraction method
    service.extract_financial_data_with_tools.return_value = {
        "metrics": [{"name": "Revenue", "value": 1500000}],
        "visualization_data": {
            "charts": [
                {
                    "chartType": "bar",
                    "config": {"title": "Revenue", "description": "Revenue by year"},
                    "data": [{"year": "2023", "value": 1500000}],
                    "chartConfig": {"value": {"label": "Revenue"}}
                }
            ],
            "tables": []
        }
    }
    
    # Return the mocked service
    return service


class TestAnalysisServiceEnhancements:
    """Test suite for enhanced AnalysisService functionality"""
    
    def setup_method(self):
        """Set up for each test"""
        self.analysis_repository = MagicMock()
        self.document_repository = MagicMock()
        self.claude_service = MagicMock()
        
        # Create the service with the correct constructor parameters
        self.service = AnalysisService(
            analysis_repository=self.analysis_repository,
            document_repository=self.document_repository
        )
        
        # Replace the claude_service property after initialization
        self.service.claude_service = self.claude_service
    
    @pytest.mark.asyncio
    async def test_get_visualization_data(self, sample_document):
        """Test retrieving visualization data from a document"""
        # Setup
        self.document_repository.get_document.return_value = sample_document
        
        # Execute
        result = await self.service.get_visualization_data("doc123")
        
        # Verify
        assert result is not None
        assert "charts" in result
        assert "tables" in result
        assert len(result["charts"]) == 1
        assert len(result["tables"]) == 1
        assert result["charts"][0]["chartType"] == "bar"
        
    @pytest.mark.asyncio
    async def test_get_visualization_data_missing(self):
        """Test handling missing visualization data"""
        # Setup - document without visualization data
        doc_without_viz = ProcessedDocument(
            id="doc456",
            file_hash="def456",
            metadata=DocumentMetadata(
                filename="simple_doc.pdf",
                filetype="application/pdf",
                size=5000,
                document_type=DocumentContentType.BALANCE_SHEET,
                upload_time="2023-11-02T12:00:00Z",
                page_count=5
            ),
            processing_status=ProcessingStatus.COMPLETED,
            extracted_text="Simple document without visualization data",
            extracted_data={"metrics": []}
        )
        self.document_repository.get_document.return_value = doc_without_viz
        
        # Execute
        result = await self.service.get_visualization_data("doc456")
        
        # Verify - should get an empty visualization data structure
        assert result is not None
        assert "charts" in result
        assert "tables" in result
        assert len(result["charts"]) == 0
        assert len(result["tables"]) == 0
        
    @pytest.mark.asyncio
    async def test_get_document_not_found(self):
        """Test handling document not found"""
        # Setup
        self.document_repository.get_document.return_value = None
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Document not found"):
            await self.service.get_visualization_data("nonexistent")
    
    @pytest.mark.asyncio
    async def test_run_analysis_with_tools(self, sample_document, mock_claude_service):
        """Test running analysis with tool-based approach"""
        # Setup
        self.document_repository.get_document.return_value = sample_document
        self.service.claude_service = mock_claude_service
        
        # Mock PDF content
        pdf_content = b"%PDF-1.5\nSample PDF content"
        self.document_repository.get_pdf_content.return_value = pdf_content
        
        # Execute - Update to match the actual implementation
        result = await self.service.run_analysis(
            document_ids=["doc123"],
            analysis_type="financial",
            parameters={"use_tools": True}
        )
        
        # Verify - Adjust for the actual return value format (a tuple)
        analysis_id, result_data = result
        assert result_data is not None
        assert "result_data" in result_data
        assert "visualization_data" in result_data["result_data"]
        assert "charts" in result_data["result_data"]["visualization_data"]
        assert mock_claude_service.extract_financial_data_with_tools.called
        assert mock_claude_service.extract_financial_data_with_tools.call_args[1]["document_type"] == DocumentContentType.BALANCE_SHEET
    
    @pytest.mark.asyncio
    async def test_run_analysis_without_tools(self, sample_document):
        """Test running analysis with classic approach (without tools)"""
        # Setup
        self.document_repository.get_document.return_value = sample_document
        
        # Mock the comprehensive analysis method
        classic_analysis_result = {
            "metrics": [{"name": "Revenue", "value": 1500000}],
            "visualizationData": {
                "monetaryValues": [
                    {"title": "Revenue", "value": 1500000, "change": 0.25}
                ]
            }
        }
        
        self.service._run_comprehensive_analysis = AsyncMock(return_value=classic_analysis_result)
        
        # Execute - Update to match the actual implementation
        result = await self.service.run_analysis(
            document_ids=["doc123"],
            analysis_type="financial",
            parameters={"use_tools": False}
        )
        
        # Verify - Adjust for the actual return value format (a tuple)
        analysis_id, result_data = result
        assert result_data is not None
        assert "result_data" in result_data
        assert self.service._run_comprehensive_analysis.called
    
    @pytest.mark.asyncio
    async def test_transform_visualization_data(self):
        """Test transformation between visualization data formats"""
        # Setup
        tool_style_data = VisualizationData(
            charts=[
                ChartData(
                    chartType="bar",
                    config={
                        "title": "Revenue by Year",
                        "description": "Annual revenue trends",
                        "xAxisKey": "year"
                    },
                    data=[
                        {"year": "2021", "value": 1000000},
                        {"year": "2022", "value": 1200000}
                    ],
                    chartConfig={
                        "value": {
                            "label": "Revenue",
                            "color": "#0066CC"
                        }
                    }
                )
            ],
            tables=[
                TableData(
                    tableType="simple",
                    config={
                        "title": "Financial Metrics",
                        "description": "Key metrics",
                        "columns": [
                            {"key": "metric", "label": "Metric"},
                            {"key": "value", "label": "Value", "format": "currency"}
                        ]
                    },
                    data=[
                        {"metric": "Revenue", "value": 1200000}
                    ]
                )
            ]
        )
        
        # Execute
        legacy_data = self.service._transform_to_legacy_format(tool_style_data)
        
        # Verify
        assert legacy_data is not None
        assert "monetaryValues" in legacy_data
        assert "keywordFrequency" in legacy_data
        assert legacy_data["monetaryValues"][0]["title"] == "Revenue"
        assert legacy_data["monetaryValues"][0]["value"] == 1200000
        
    @pytest.mark.asyncio
    async def test_format_analysis_response(self, sample_document):
        """Test response formatting from different data sources"""
        # Setup
        tool_data = {
            "visualization_data": {
                "charts": [
                    {
                        "chartType": "bar",
                        "config": {"title": "Revenue", "description": ""},
                        "data": [{"year": "2023", "value": 1500000}],
                        "chartConfig": {"value": {"label": "Revenue"}}
                    }
                ],
                "tables": []
            }
        }
        
        # Execute
        result = await self.service._format_analysis_response(
            document=sample_document, 
            analysis_data=tool_data,
            analysis_type="financial"
        )
        
        # Verify
        assert result is not None
        assert "visualization_data" in result
        assert "visualizationData" in result
        assert result["visualization_data"]["charts"][0]["chartType"] == "bar" 