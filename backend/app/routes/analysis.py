from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.analysis import AnalysisRequest, AnalysisResult, FinancialMetric, FinancialRatio
from models.document import ProcessedDocument
from models.database_models import ProcessingStatusEnum
from repositories.document_repository import DocumentRepository
from repositories.analysis_repository import AnalysisRepository
from services.analysis_service import AnalysisService
from pdf_processing.document_service import DocumentService
from pdf_processing.claude_service import ClaudeService
from pdf_processing.langchain_service import LangChainService
from utils.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Dependencies
async def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepository(db)

async def get_document_service(db: AsyncSession = Depends(get_db)):
    document_repository = DocumentRepository(db)
    return DocumentService(document_repository)

async def get_analysis_repository(db: AsyncSession = Depends(get_db)):
    return AnalysisRepository(db)

async def get_analysis_service(
    db: AsyncSession = Depends(get_db),
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository),
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    return AnalysisService(analysis_repository, document_repository)

async def get_claude_service():
    return ClaudeService()

async def get_langchain_service():
    return LangChainService()

@router.post("/run", response_model=AnalysisResult)
async def run_analysis(
    analysis_request: AnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    document_repository: DocumentRepository = Depends(get_document_repository)
):
    """
    Initiate a financial analysis on selected documents, including citation extraction.
    Uses database-backed storage for analysis results.
    """
    try:
        # Verify all documents exist and are processed
        for doc_id in analysis_request.document_ids:
            document = await document_repository.get_document(doc_id)
            if not document:
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
            if document.processing_status != ProcessingStatusEnum.COMPLETED:
                raise HTTPException(status_code=400, detail=f"Document {doc_id} is not fully processed")
        
        # Run the analysis
        result = await analysis_service.run_analysis(
            document_id=analysis_request.document_ids[0],  # Primary document for analysis
            analysis_type=analysis_request.analysis_type,
            parameters=analysis_request.parameters
        )
        
        # Convert the result to the API schema
        return AnalysisResult(
            id=result["analysis_id"],
            document_ids=analysis_request.document_ids,
            analysis_type=analysis_request.analysis_type,
            timestamp=datetime.fromisoformat(result["created_at"]),
            metrics=[
                FinancialMetric(
                    category=metric.get("category", "Unknown"),
                    name=metric.get("name", "Unknown"),
                    period=metric.get("period", "Unknown"),
                    value=metric.get("value", 0.0),
                    unit=metric.get("unit", ""),
                    is_estimated=metric.get("is_estimated", False)
                )
                for metric in result.get("result_data", {}).get("metrics", [])
            ],
            ratios=[
                FinancialRatio(
                    name=ratio.get("name", "Unknown"),
                    value=ratio.get("value", 0.0),
                    description=ratio.get("description", ""),
                    benchmark=ratio.get("benchmark"),
                    trend=ratio.get("trend")
                )
                for ratio in result.get("result_data", {}).get("ratios", [])
            ],
            insights=result.get("result_data", {}).get("insights", []),
            visualization_data=result.get("result_data", {}).get("chart_data", {}),
            citation_references=result.get("result_data", {}).get("citation_references", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running analysis: {str(e)}")

@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_result(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Retrieve analysis results along with linked citation references.
    """
    try:
        # Get the analysis from the database
        analysis = await analysis_service.get_analysis(analysis_id)
        
        # Convert to the API schema
        return AnalysisResult(
            id=analysis["id"],
            document_ids=[analysis["document_id"]],
            analysis_type=analysis["analysis_type"],
            timestamp=datetime.fromisoformat(analysis["created_at"]),
            metrics=[
                FinancialMetric(
                    category=metric.get("category", "Unknown"),
                    name=metric.get("name", "Unknown"),
                    period=metric.get("period", "Unknown"),
                    value=metric.get("value", 0.0),
                    unit=metric.get("unit", ""),
                    is_estimated=metric.get("is_estimated", False)
                )
                for metric in analysis.get("result_data", {}).get("metrics", [])
            ],
            ratios=[
                FinancialRatio(
                    name=ratio.get("name", "Unknown"),
                    value=ratio.get("value", 0.0),
                    description=ratio.get("description", ""),
                    benchmark=ratio.get("benchmark"),
                    trend=ratio.get("trend")
                )
                for ratio in analysis.get("result_data", {}).get("ratios", [])
            ],
            insights=analysis.get("result_data", {}).get("insights", []),
            visualization_data=analysis.get("result_data", {}).get("chart_data", {}),
            citation_references=analysis.get("result_data", {}).get("citation_references", {})
        )
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@router.get("/document/{document_id}", response_model=List[Dict[str, Any]])
async def list_document_analyses(
    document_id: str,
    analysis_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    List analyses for a document.
    """
    try:
        # Get the analyses from the database
        analyses = await analysis_service.list_document_analyses(
            document_id=document_id,
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )
        
        return analyses
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository)
):
    """
    Delete an analysis.
    """
    try:
        # Check if analysis exists
        analysis = await analysis_repository.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
        
        # Delete the analysis
        success = await analysis_repository.delete_analysis(analysis_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete analysis")
        
        return {"message": f"Analysis {analysis_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")

# Helper functions to generate mock data for demonstration/testing
def generate_mock_metrics(period: str) -> List[FinancialMetric]:
    """Generate mock financial metrics for demo purposes."""
    return [
        FinancialMetric(
            category="Revenue",
            name="Total Revenue",
            period=period,
            value=24.5,
            unit="million USD"
        ),
        FinancialMetric(
            category="Revenue",
            name="YoY Growth",
            period=period,
            value=12.0,
            unit="percent"
        ),
        FinancialMetric(
            category="Expenses",
            name="Operating Expenses",
            period=period,
            value=18.3,
            unit="million USD"
        ),
        FinancialMetric(
            category="Profitability",
            name="Net Income",
            period=period,
            value=4.2,
            unit="million USD"
        ),
        FinancialMetric(
            category="Liquidity",
            name="Cash Position",
            period=period,
            value=15.6,
            unit="million USD"
        )
    ]

def generate_mock_ratios() -> List[FinancialRatio]:
    """Generate mock financial ratios for demo purposes."""
    return [
        FinancialRatio(
            name="Current Ratio",
            value=1.8,
            description="Measures the company's ability to pay short-term obligations",
            benchmark=2.1,
            trend=-0.1
        ),
        FinancialRatio(
            name="Quick Ratio",
            value=1.2,
            description="Measures the company's ability to pay short-term obligations using liquid assets",
            benchmark=1.5,
            trend=-0.05
        ),
        FinancialRatio(
            name="Debt-to-Equity",
            value=0.85,
            description="Measures the company's financial leverage",
            benchmark=0.7,
            trend=0.03
        ),
        FinancialRatio(
            name="Profit Margin",
            value=12.4,
            description="Measures the company's profitability as a percentage of revenue",
            benchmark=10.2,
            trend=0.5
        ),
        FinancialRatio(
            name="Return on Assets",
            value=8.2,
            description="Measures how efficiently the company is using its assets to generate profit",
            benchmark=7.5,
            trend=0.3
        )
    ]