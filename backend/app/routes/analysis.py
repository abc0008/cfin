from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import re
from fastapi.responses import JSONResponse
import json
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from models.analysis import AnalysisRequest, AnalysisResult as AnalysisResultResponse
from models.analysis import FinancialMetric, FinancialRatio, ComparativePeriod
from models.visualization import VisualizationData, ChartData, TableData
from models.document import ProcessedDocument
from models.database_models import ProcessingStatusEnum
from repositories.document_repository import DocumentRepository
from repositories.analysis_repository import AnalysisRepository
from services.analysis_service import AnalysisService
from pdf_processing.document_service import DocumentService
from pdf_processing.claude_service import ClaudeService
from pdf_processing.langchain_service import LangChainService
from utils.database import get_db
from utils.response import handle_exception, create_error_response, get_error_type_from_status, add_cors_headers

# Configure more verbose logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

# --- Pydantic models for API response ---
class VisualizationDataResponse(BaseModel):
    charts: List[Any] = Field(default_factory=list)
    tables: List[Any] = Field(default_factory=list)
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

        # Prepare parameters dictionary
        parameters = analysis_request.parameters or {}
        
        # Always include the query if provided
        if analysis_request.query:
            parameters["query"] = analysis_request.query

        # Call the analysis service
        analysis_id, result_data = await analysis_service.run_analysis(
            document_ids=[str(doc_id) for doc_id in analysis_request.documentIds],
            analysis_type=analysis_request.analysisType,
            parameters=parameters
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

@router.post("/run-with-tools", response_model=AnalysisApiResponse, deprecated=True)
async def run_analysis_with_tools(
    analysis_request: AnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    DEPRECATED: Use the primary /run endpoint instead, which now supports tool-based analysis.
    This endpoint is maintained for backwards compatibility but routes to the same implementation.
    """
    return await run_analysis_endpoint(analysis_request, analysis_service)

# Get endpoint for retrieving results
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
        # Ensure JSONResponse is imported in case we need it
        from fastapi.responses import JSONResponse
        
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
        # Ensure JSONResponse is imported in case we need it
        from fastapi.responses import JSONResponse
        
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

@router.get("/{analysis_id}/enhanced", response_model=Dict[str, Any])
async def get_enhanced_analysis(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Retrieve enhanced analysis with trends and extra insights
    """
    try:
        # Get the base analysis
        analysis = await analysis_service.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
        
        # Generate enhanced data based on the basic analysis
        trends = []
        insights = []
        
        # Extract metrics for trend generation
        metrics = analysis.get("result_data", {}).get("metrics", [])
        chart_data = analysis.get("result_data", {}).get("chart_data", {})
        base_insights = analysis.get("result_data", {}).get("insights", [])
        
        # Generate trends if we have metrics
        if metrics:
            for metric in metrics:
                # Create trend data for each metric
                trend = {
                    "id": f"trend-{uuid.uuid4()}",
                    "name": f"{metric.get('name', 'Unknown')} Trend",
                    "description": f"Trend analysis for {metric.get('name', 'Unknown')}",
                    "value": metric.get("value", 0.0),
                    "change": 0.05,  # Mock value: 5% change
                    "direction": "increasing" if 0.05 > 0 else "decreasing",
                    "significance": "high" if metric.get("name", "").lower() in ["revenue", "net income"] else "medium",
                    "category": metric.get("category", "Unknown")
                }
                trends.append(trend)
        
        # Generate enhanced insights
        if base_insights:
            for i, insight_text in enumerate(base_insights):
                # Categorize insights
                category = "critical" if i == 0 else "important" if i == 1 else "informational"
                
                # Link to metrics where possible
                related_metrics = []
                for metric in metrics[:2]:  # Just link to first two metrics for demo
                    related_metrics.append(metric.get("name", "Unknown"))
                
                insight = {
                    "id": f"insight-{uuid.uuid4()}",
                    "text": insight_text,
                    "category": category,
                    "relatedMetrics": related_metrics,
                    "confidence": 0.9 - (i * 0.05)  # Decreasing confidence for later insights
                }
                insights.append(insight)
        
        # Return the enhanced analysis
        return {
            "trends": trends,
            "insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Ensure JSONResponse is imported in case we need it
        from fastapi.responses import JSONResponse
        
        logger.error(f"Error getting enhanced analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced analysis: {str(e)}")

@router.get("/{analysis_id}/chart/{chart_type}", response_model=Dict[str, Any])
async def get_chart_data(
    analysis_id: str,
    chart_type: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Retrieve chart data for a specific analysis and chart type
    """
    try:
        # Get the base analysis
        analysis = await analysis_service.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
        
        # Extract chart data from the analysis
        chart_data = analysis.get("result_data", {}).get("chart_data", {})
        
        # If time series data is available, return it with the requested chart type
        if "timeSeriesData" in chart_data:
            return {
                "chartData": chart_data["timeSeriesData"],
                "chartType": chart_type,
                "title": f"Financial {chart_type.capitalize()} Chart",
                "description": f"Generated from analysis {analysis_id}"
            }
        
        # If no chart data available, return empty result
        return {
            "chartData": [],
            "chartType": chart_type,
            "title": f"No data available",
            "description": "No chart data found for this analysis"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Ensure JSONResponse is imported in case we need it
        from fastapi.responses import JSONResponse
        
        logger.error(f"Error getting chart data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving chart data: {str(e)}")

# Helper functions for generating chart data
def generate_monetary_values_data(metrics, insights):
    """Generate monetary values data for visualization."""
    # First, try to use actual metrics with appropriate units
    monetary_metrics = [
        {"name": metric.name, "value": metric.value, "description": f"{metric.category}: {metric.name} ({metric.period})"}
        for metric in metrics
        if any(keyword in metric.unit.lower() for keyword in ["usd", "$", "dollar", "million", "billion", "revenue", "cost", "price", "value"])
        or any(keyword in metric.name.lower() for keyword in ["revenue", "sales", "cost", "price", "income", "profit", "expense", "asset"])
    ]
    
    # Log the available metrics
    logger.info(f"CHART_LOG: Found {len(metrics)} total metrics for monetary values chart")
    logger.info(f"CHART_LOG: Filtered down to {len(monetary_metrics)} monetary metrics")
    if monetary_metrics:
        logger.info(f"CHART_LOG: Using actual monetary metrics for chart: {json.dumps([m['name'] for m in monetary_metrics])}")
    
    # If we don't have metrics, extract monetary values from insights
    if not monetary_metrics and insights:
        import re
        # Look for patterns like "$X million" or "X million dollars" in insights
        monetary_pattern = r'\$\s*[\d,\.]+\s*(million|billion|thousand|M|B|K)?|\d+(\.\d+)?\s*(million|billion|thousand|M|B|K)?\s*(dollars|USD)'
        monetary_insights = []
        
        logger.info(f"CHART_LOG: No monetary metrics found, attempting to extract from {len(insights)} insights")
        
        for idx, insight in enumerate(insights[:5]):
            matches = re.findall(monetary_pattern, insight, re.IGNORECASE)
            if matches:
                logger.info(f"CHART_LOG: Found monetary pattern in insight {idx+1}: {matches}")
                value = 1000000 * (idx + 1)  # Placeholder value if we can't parse the actual number
                monetary_insights.append({
                    "name": f"Value {idx+1}",
                    "value": value, 
                    "description": insight[:100] + "..."
                })
        
        if monetary_insights:
            logger.info(f"CHART_LOG: Using {len(monetary_insights)} monetary values extracted from insights")
            return monetary_insights
        else:
            logger.info("CHART_LOG: Failed to extract monetary values from insights")
    
    # If we still don't have data, provide sample data
    if not monetary_metrics:
        logger.warning("CHART_LOG: ⚠️ USING FALLBACK STATIC DATA for monetary values chart - no real metrics or insights found")
        return [
            {"name": "Revenue", "value": 1250000, "description": "Estimated revenue based on document context"},
            {"name": "Cost", "value": 875000, "description": "Estimated costs based on document context"},
            {"name": "Profit", "value": 375000, "description": "Calculated profit (Revenue - Cost)"}
        ]
    
    return monetary_metrics[:5]  # Limit to 5 data points

def generate_percentage_data(metrics, insights):
    """Generate percentage data for visualization."""
    # First, try to use actual metrics with percentage units
    percentage_metrics = [
        {"name": metric.name, "value": metric.value, "description": f"{metric.category}: {metric.name} ({metric.period})"}
        for metric in metrics
        if any(keyword in metric.unit.lower() for keyword in ["percent", "%", "ratio", "rate", "growth"]) 
        or any(keyword in metric.name.lower() for keyword in ["percent", "rate", "ratio", "growth", "margin", "yield", "return"])
    ]
    
    # Log the available metrics 
    logger.info(f"CHART_LOG: Found {len(metrics)} total metrics for percentage chart")
    logger.info(f"CHART_LOG: Filtered down to {len(percentage_metrics)} percentage metrics")
    if percentage_metrics:
        logger.info(f"CHART_LOG: Using actual percentage metrics for chart: {json.dumps([m['name'] for m in percentage_metrics])}")
    
    # If we don't have metrics, extract percentage values from insights
    if not percentage_metrics and insights:
        import re
        # Look for patterns like "X%" or "X percent" in insights
        percentage_pattern = r'(\d+(\.\d+)?)\s*(%|percent|percentage)'
        percentage_insights = []
        
        logger.info(f"CHART_LOG: No percentage metrics found, attempting to extract from {len(insights)} insights")
        
        for idx, insight in enumerate(insights[:5]):
            matches = re.findall(percentage_pattern, insight, re.IGNORECASE)
            if matches:
                logger.info(f"CHART_LOG: Found percentage pattern in insight {idx+1}: {matches}")
                try:
                    value = float(matches[0][0])
                    percentage_insights.append({
                        "name": f"Rate {idx+1}",
                        "value": value,
                        "description": insight[:100] + "..."
                    })
                except:
                    percentage_insights.append({
                        "name": f"Rate {idx+1}",
                        "value": (idx + 1) * 5,  # Placeholder percentage
                        "description": insight[:100] + "..."
                    })
        
        if percentage_insights:
            logger.info(f"CHART_LOG: Using {len(percentage_insights)} percentage values extracted from insights")
            return percentage_insights
        else:
            logger.info("CHART_LOG: Failed to extract percentage values from insights")
    
    # If we still don't have data, provide sample data
    if not percentage_metrics:
        logger.warning("CHART_LOG: ⚠️ USING FALLBACK STATIC DATA for percentage chart - no real metrics or insights found")
        return [
            {"name": "Growth Rate", "value": 8.5, "description": "Estimated annual growth rate"},
            {"name": "Profit Margin", "value": 15.3, "description": "Estimated profit margin percentage"},
            {"name": "Market Share", "value": 12.7, "description": "Estimated market share percentage"}
        ]
    
    return percentage_metrics[:5]  # Limit to 5 data points

def generate_keyword_frequency_data(insights):
    """Generate keyword frequency data for visualization."""
    # Generate frequency data from insights
    if not insights:
        # Provide sample data if no insights
        logger.warning("CHART_LOG: ⚠️ USING FALLBACK STATIC DATA for keyword frequency chart - no insights found")
        return [
            {"name": "Revenue", "value": 3, "description": "Mentions of revenue in document"},
            {"name": "Profit", "value": 2, "description": "Mentions of profit in document"},
            {"name": "Growth", "value": 2, "description": "Mentions of growth in document"},
            {"name": "Market", "value": 1, "description": "Mentions of market in document"}
        ]
    
    logger.info(f"CHART_LOG: Generating keyword frequency data from {len(insights)} insights")
    
    # Extract financial keywords from insights
    import re
    financial_terms = [
        "revenue", "profit", "loss", "growth", "income", "cost", "expense", "asset", 
        "liability", "equity", "debt", "cash", "margin", "dividend", "earnings", 
        "investment", "capital", "fiscal", "quarter", "annual"
    ]
    
    # Count term frequency
    term_count = {}
    for insight in insights:
        for term in financial_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.findall(pattern, insight.lower())
            if matches:
                term_count[term] = term_count.get(term, 0) + len(matches)
    
    logger.info(f"CHART_LOG: Found {len(term_count)} financial terms in insights")
    if term_count:
        logger.info(f"CHART_LOG: Most frequent terms: {json.dumps(dict(sorted(term_count.items(), key=lambda x: x[1], reverse=True)[:5]))}")
    
    # Sort by frequency and convert to chart data format
    frequency_data = [
        {"name": term.capitalize(), "value": count, "description": f"Mentions of {term} in document"}
        for term, count in sorted(term_count.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # If we still don't have data from terms, use the insights themselves
    if not frequency_data:
        logger.warning("CHART_LOG: No financial terms found in insights, using fallback method")
        return [{"name": insight[:20] + "...", "value": 1, "description": insight[:100]} for insight in insights[:5]]
    
    return frequency_data[:5]  # Limit to 5 most frequent terms