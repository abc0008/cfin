import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock, MagicMock
import json
from typing import Dict, Any, List, Optional

from fastapi.testclient import TestClient
from main import app
from database.repository import DocumentRepository
from services.document_service import DocumentService
from services.analysis_service import AnalysisService
from pdf_processing.claude_service import ClaudeService
from models.document import ProcessedDocument, DocumentMetadata, DocumentContentType, ProcessingStatus


@pytest.fixture
def sample_pdf_data():
    """Sample PDF content for testing"""
    # Just a minimal PDF header for testing
    return b"%PDF-1.5\nSample financial report with revenue data"


@pytest.fixture
def test_client():
    """Create a FastAPI test client"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_document_service():
    """Mock document service for testing"""
    service = MagicMock(spec=DocumentService)
    
    # Create a sample document
    doc = ProcessedDocument(
        id="integration-test-doc",
        file_hash="test123",
        metadata=DocumentMetadata(
            filename="financial_report_test.pdf",
            filetype="application/pdf",
            size=12345,
            document_type=DocumentContentType.FINANCIAL_REPORT,
            upload_time="2023-12-01T12:00:00Z",
            page_count=5
        ),
        processing_status=ProcessingStatus.COMPLETED,
        extracted_text="Financial report with revenue of $1,500,000 for 2023.",
        extracted_data={
            "metrics": [
                {"name": "Revenue", "value": 1500000, "unit": "USD"}
            ],
            "visualizationData": {
                "monetaryValues": [
                    {"title": "Revenue", "value": 1500000, "change": 0.25}
                ]
            }
        }
    )
    
    # Mock methods
    service.get_document.return_value = doc
    service.get_pdf_content.return_value = sample_pdf_data()
    
    return service


@pytest.fixture
def mock_claude_service():
    """Mock Claude service for testing"""
    service = AsyncMock(spec=ClaudeService)
    
    # Mock the tool-based financial data extraction
    service.extract_financial_data_with_tools.return_value = {
        "metrics": [
            {"name": "Revenue", "value": 1500000, "unit": "USD"},
            {"name": "Net Income", "value": 350000, "unit": "USD"}
        ],
        "visualization_data": {
            "charts": [
                {
                    "chartType": "bar",
                    "config": {
                        "title": "Revenue by Year",
                        "description": "Annual revenue analysis",
                        "xAxisKey": "year"
                    },
                    "data": [
                        {"year": "2021", "value": 1000000},
                        {"year": "2022", "value": 1200000},
                        {"year": "2023", "value": 1500000}
                    ],
                    "chartConfig": {
                        "value": {
                            "label": "Revenue (USD)",
                            "color": "#0066CC"
                        }
                    }
                },
                {
                    "chartType": "line",
                    "config": {
                        "title": "Net Income Trend",
                        "description": "Net income over time",
                        "xAxisKey": "year"
                    },
                    "data": [
                        {"year": "2021", "value": 200000},
                        {"year": "2022", "value": 280000},
                        {"year": "2023", "value": 350000}
                    ],
                    "chartConfig": {
                        "value": {
                            "label": "Net Income (USD)",
                            "color": "#00CC66"
                        }
                    }
                }
            ],
            "tables": [
                {
                    "tableType": "simple",
                    "config": {
                        "title": "Key Financial Metrics",
                        "description": "Summary of important metrics",
                        "columns": [
                            {"key": "metric", "label": "Metric"},
                            {"key": "value", "label": "Value (USD)", "format": "currency"},
                            {"key": "change", "label": "YoY Change", "format": "percent"}
                        ]
                    },
                    "data": [
                        {"metric": "Revenue", "value": 1500000, "change": 0.25},
                        {"metric": "Net Income", "value": 350000, "change": 0.25},
                        {"metric": "Operating Expenses", "value": 850000, "change": 0.15}
                    ]
                }
            ]
        },
        "visualizationData": {
            "monetaryValues": [
                {"title": "Revenue", "value": 1500000, "change": 0.25},
                {"title": "Net Income", "value": 350000, "change": 0.25}
            ],
            "keywordFrequency": [
                {"keyword": "revenue", "frequency": 15},
                {"keyword": "profit", "frequency": 10}
            ]
        }
    }
    
    return service


@pytest.mark.integration
class TestFinancialAnalysisToolsIntegration:
    """Integration tests for financial analysis with tool-based approach"""
    
    @pytest.mark.asyncio
    @patch('app.routes.analysis.get_analysis_service')
    @patch('app.routes.analysis.get_document_service')
    async def test_financial_analysis_endpoint_with_tools(
        self, mock_get_doc_service, mock_get_analysis_service, 
        test_client, mock_document_service, mock_claude_service
    ):
        """Test the financial analysis endpoint with tool-based analysis"""
        # Setup
        analysis_service = AnalysisService(
            document_service=mock_document_service,
            claude_service=mock_claude_service
        )
        
        # Configure mocks for dependency injection
        mock_get_doc_service.return_value = mock_document_service
        mock_get_analysis_service.return_value = analysis_service
        
        # Execute
        response = test_client.post(
            "/api/analysis/",
            json={
                "document_id": "integration-test-doc",
                "analysis_type": "financial",
                "use_tools": True
            }
        )
        
        # Verify
        assert response.status_code == 200
        
        data = response.json()
        assert "visualization_data" in data
        assert "charts" in data["visualization_data"]
        assert "tables" in data["visualization_data"]
        
        # Verify chart data
        charts = data["visualization_data"]["charts"]
        assert len(charts) == 2
        assert charts[0]["chartType"] == "bar"
        assert charts[1]["chartType"] == "line"
        assert "Revenue" in charts[0]["config"]["title"]
        
        # Verify table data
        tables = data["visualization_data"]["tables"]
        assert len(tables) == 1
        assert tables[0]["tableType"] == "simple"
        assert "Key Financial Metrics" in tables[0]["config"]["title"]
        
        # Verify legacy data format is also included
        assert "visualizationData" in data
        assert "monetaryValues" in data["visualizationData"]
        assert data["visualizationData"]["monetaryValues"][0]["title"] == "Revenue"
    
    @pytest.mark.asyncio
    @patch('app.routes.documents.get_document_service')
    async def test_document_upload_and_analysis_flow(
        self, mock_get_doc_service, test_client, 
        mock_document_service, mock_claude_service, sample_pdf_data
    ):
        """Test the full document upload and analysis flow"""
        # Setup - Mock document upload
        mock_get_doc_service.return_value = mock_document_service
        
        # Mock the create_document method
        mock_document_service.create_document.return_value = "integration-test-doc"
        
        # 1. Upload document
        with patch('app.routes.documents.UploadFile', autospec=True) as MockUploadFile:
            mock_file = MockUploadFile()
            mock_file.filename = "financial_report_test.pdf"
            mock_file.content_type = "application/pdf"
            mock_file.file.read.return_value = sample_pdf_data
            
            # Execute upload
            with patch('app.routes.documents.get_document_service', return_value=mock_document_service):
                upload_response = test_client.post(
                    "/api/documents/upload",
                    files={"file": (mock_file.filename, sample_pdf_data, "application/pdf")}
                )
                
                # Verify upload
                assert upload_response.status_code == 200
                assert "document_id" in upload_response.json()
                assert upload_response.json()["document_id"] == "integration-test-doc"
        
        # 2. Now test analysis with tools
        # Modify mock_document_service to include visualization data in response
        processed_doc = mock_document_service.get_document.return_value
        processed_doc.extracted_data["visualization_data"] = mock_claude_service.extract_financial_data_with_tools.return_value["visualization_data"]
        mock_document_service.get_document.return_value = processed_doc
        
        # Setup analysis service with the mocks
        analysis_service = AnalysisService(
            document_service=mock_document_service,
            claude_service=mock_claude_service
        )
        
        # Mock the analysis service dependency
        with patch('app.routes.analysis.get_analysis_service', return_value=analysis_service):
            # Execute analysis request
            analysis_response = test_client.post(
                "/api/analysis/",
                json={
                    "document_id": "integration-test-doc",
                    "analysis_type": "financial",
                    "use_tools": True
                }
            )
            
            # Verify analysis
            assert analysis_response.status_code == 200
            assert "visualization_data" in analysis_response.json()
            
            # Verify specific charts
            charts = analysis_response.json()["visualization_data"]["charts"]
            assert any(chart["chartType"] == "bar" for chart in charts)
            assert any(chart["chartType"] == "line" for chart in charts)
            
            # Verify data transformation
            assert "visualizationData" in analysis_response.json()
            assert "monetaryValues" in analysis_response.json()["visualizationData"]
            
    @pytest.mark.asyncio
    @patch('app.routes.analysis.get_analysis_service')
    async def test_visualization_data_endpoint(
        self, mock_get_analysis_service, test_client, 
        mock_document_service, mock_claude_service
    ):
        """Test the dedicated visualization data endpoint"""
        # Setup
        analysis_service = AnalysisService(
            document_service=mock_document_service,
            claude_service=mock_claude_service
        )
        
        # Add visualization data to the mock document
        processed_doc = mock_document_service.get_document.return_value
        processed_doc.extracted_data["visualization_data"] = mock_claude_service.extract_financial_data_with_tools.return_value["visualization_data"]
        mock_document_service.get_document.return_value = processed_doc
        
        # Configure mock for dependency injection
        mock_get_analysis_service.return_value = analysis_service
        
        # Execute
        response = test_client.get(
            "/api/analysis/visualization-data/integration-test-doc"
        )
        
        # Verify
        assert response.status_code == 200
        
        data = response.json()
        assert "charts" in data
        assert "tables" in data
        
        # Verify charts
        assert len(data["charts"]) == 2
        assert data["charts"][0]["chartType"] == "bar"
        assert data["charts"][1]["chartType"] == "line"
        
        # Verify tables
        assert len(data["tables"]) == 1
        assert data["tables"][0]["tableType"] == "simple" 