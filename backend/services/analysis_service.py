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
from pdf_processing.financial_agent import FinancialAnalysisAgent
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
        self.financial_agent = FinancialAnalysisAgent()
    
    async def run_analysis(
        self,
        document_id: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run financial analysis on a document.
        
        Args:
            document_id: ID of the document to analyze
            analysis_type: Type of analysis to run
            parameters: Optional parameters for the analysis
            
        Returns:
            Dictionary containing the analysis results
        """
        # Get the document
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Initialize parameters if not provided
        if parameters is None:
            parameters = {}
        
        # Run the appropriate analysis based on type
        try:
            if analysis_type == "financial_ratios":
                result_data = await self._run_financial_ratio_analysis(document, parameters)
            elif analysis_type == "trend_analysis":
                result_data = await self._run_trend_analysis(document, parameters)
            elif analysis_type == "benchmarking":
                result_data = await self._run_benchmark_analysis(document, parameters)
            elif analysis_type == "sentiment_analysis":
                result_data = await self._run_sentiment_analysis(document, parameters)
            else:
                # Default to comprehensive analysis
                result_data = await self._run_comprehensive_analysis(document, parameters)
            
            # Save the analysis result
            analysis = await self.analysis_repository.create_analysis(
                document_id=document_id,
                analysis_type=analysis_type,
                result_data=result_data
            )
            
            # Return the result with metadata
            return {
                "analysis_id": analysis.id,
                "document_id": document_id,
                "analysis_type": analysis_type,
                "created_at": analysis.created_at.isoformat(),
                "result_data": result_data
            }
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}", exc_info=True)
            raise
    
    async def _run_financial_ratio_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run financial ratio analysis.
        
        Args:
            document: Document to analyze
            parameters: Analysis parameters
            
        Returns:
            Dictionary containing the analysis results
        """
        # Extract financial data from the document
        financial_data = document.extracted_data.get("financial_data", {})
        
        if not financial_data:
            raise ValueError("No financial data found in document")
        
        # Use the financial agent to calculate ratios
        ratios = await self.financial_agent.calculate_financial_ratios(
            financial_data=financial_data,
            parameters=parameters
        )
        
        # Build the result data
        result_data = {
            "ratios": ratios,
            "document_type": document.document_type.value if document.document_type else "other",
            "periods": document.periods or [],
            "insights": []
        }
        
        # Generate insights if requested
        if parameters.get("generate_insights", True):
            insights = await self.financial_agent.generate_insights_from_ratios(ratios)
            result_data["insights"] = insights
        
        # Prepare chart data if requested
        if parameters.get("generate_charts", True):
            chart_data = await self.financial_agent.prepare_chart_data(
                financial_data=financial_data,
                ratios=ratios,
                parameters=parameters
            )
            result_data["chart_data"] = chart_data
        
        return result_data
    
    async def _run_trend_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run trend analysis.
        
        Args:
            document: Document to analyze
            parameters: Analysis parameters
            
        Returns:
            Dictionary containing the analysis results
        """
        # Extract financial data from the document
        financial_data = document.extracted_data.get("financial_data", {})
        
        if not financial_data:
            raise ValueError("No financial data found in document")
        
        # Get time periods from the document
        periods = document.periods
        if not periods or len(periods) < 2:
            raise ValueError("Trend analysis requires at least two time periods")
        
        # Use the financial agent to analyze trends
        trends = await self.financial_agent.analyze_trends(
            financial_data=financial_data,
            periods=periods,
            parameters=parameters
        )
        
        # Build the result data
        result_data = {
            "trends": trends,
            "document_type": document.document_type.value if document.document_type else "other",
            "periods": periods,
            "insights": []
        }
        
        # Generate insights if requested
        if parameters.get("generate_insights", True):
            insights = await self.financial_agent.generate_insights_from_trends(trends)
            result_data["insights"] = insights
        
        # Prepare chart data if requested
        if parameters.get("generate_charts", True):
            chart_data = await self.financial_agent.prepare_trend_chart_data(
                trends=trends,
                periods=periods,
                parameters=parameters
            )
            result_data["chart_data"] = chart_data
        
        return result_data
    
    async def _run_benchmark_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run benchmark analysis.
        
        Args:
            document: Document to analyze
            parameters: Analysis parameters
            
        Returns:
            Dictionary containing the analysis results
        """
        # Extract financial data from the document
        financial_data = document.extracted_data.get("financial_data", {})
        
        if not financial_data:
            raise ValueError("No financial data found in document")
        
        # Get benchmark data (in a real implementation, this would come from a database or API)
        industry = parameters.get("industry", "general")
        benchmark_data = await self.financial_agent.get_industry_benchmarks(industry)
        
        # Use the financial agent to compare with benchmarks
        comparison = await self.financial_agent.compare_with_benchmarks(
            financial_data=financial_data,
            benchmarks=benchmark_data,
            parameters=parameters
        )
        
        # Build the result data
        result_data = {
            "benchmark_comparison": comparison,
            "industry": industry,
            "document_type": document.document_type.value if document.document_type else "other",
            "periods": document.periods or [],
            "insights": []
        }
        
        # Generate insights if requested
        if parameters.get("generate_insights", True):
            insights = await self.financial_agent.generate_insights_from_benchmark(comparison)
            result_data["insights"] = insights
        
        # Prepare chart data if requested
        if parameters.get("generate_charts", True):
            chart_data = await self.financial_agent.prepare_benchmark_chart_data(
                comparison=comparison,
                parameters=parameters
            )
            result_data["chart_data"] = chart_data
        
        return result_data
    
    async def _run_sentiment_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run sentiment analysis on document text.
        
        Args:
            document: Document to analyze
            parameters: Analysis parameters
            
        Returns:
            Dictionary containing the analysis results
        """
        # Get document text
        text = document.raw_text
        
        if not text:
            raise ValueError("No text content found in document")
        
        # Use Claude to analyze sentiment
        sentiment_analysis = await self.claude_service.analyze_document_sentiment(text)
        
        # Build the result data
        result_data = {
            "sentiment": sentiment_analysis["sentiment"],
            "sentiment_score": sentiment_analysis["score"],
            "document_type": document.document_type.value if document.document_type else "other",
            "key_phrases": sentiment_analysis.get("key_phrases", []),
            "insights": sentiment_analysis.get("insights", [])
        }
        
        # Prepare chart data if requested
        if parameters.get("generate_charts", True):
            chart_data = [{
                "type": "gauge",
                "title": "Sentiment Score",
                "data": {
                    "value": sentiment_analysis["score"],
                    "min": -1,
                    "max": 1,
                    "thresholds": [
                        { "value": -0.5, "color": "red" },
                        { "value": 0, "color": "yellow" },
                        { "value": 0.5, "color": "green" }
                    ]
                }
            }]
            
            result_data["chart_data"] = chart_data
        
        return result_data
    
    async def _run_comprehensive_analysis(
        self,
        document: Document,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run comprehensive financial analysis.
        
        Args:
            document: Document to analyze
            parameters: Analysis parameters
            
        Returns:
            Dictionary containing the analysis results
        """
        # Extract financial data from the document
        financial_data = document.extracted_data.get("financial_data", {})
        
        if not financial_data:
            raise ValueError("No financial data found in document")
        
        # Use the financial agent to perform comprehensive analysis
        analysis_results = await self.financial_agent.analyze_financial_document(
            document_type=document.document_type.value if document.document_type else "other",
            financial_data=financial_data,
            periods=document.periods or [],
            parameters=parameters
        )
        
        return analysis_results
    
    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get an analysis by ID.
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            Dictionary containing the analysis
        """
        # Get the analysis
        analysis = await self.analysis_repository.get_analysis(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # Format the result
        formatted_analysis = {
            "id": analysis.id,
            "document_id": analysis.document_id,
            "analysis_type": analysis.analysis_type,
            "created_at": analysis.created_at.isoformat(),
            "result_data": analysis.result_data
        }
        
        return formatted_analysis
    
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
            List of analyses
        """
        # Get the analyses
        analyses = await self.analysis_repository.list_document_analyses(
            document_id=document_id,
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )
        
        # Format the results
        formatted_analyses = []
        for analysis in analyses:
            formatted_analyses.append({
                "id": analysis.id,
                "document_id": analysis.document_id,
                "analysis_type": analysis.analysis_type,
                "created_at": analysis.created_at.isoformat(),
                # Include a summary instead of full result data
                "summary": self._generate_analysis_summary(analysis.result_data)
            })
        
        return formatted_analyses
    
    def _generate_analysis_summary(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of analysis results.
        
        Args:
            result_data: Full analysis result data
            
        Returns:
            Dictionary containing a summary of the analysis
        """
        summary = {
            "insights_count": len(result_data.get("insights", [])),
            "has_charts": "chart_data" in result_data,
            "charts_count": len(result_data.get("chart_data", [])),
        }
        
        # Include a sample insight if available
        if result_data.get("insights") and len(result_data["insights"]) > 0:
            summary["sample_insight"] = result_data["insights"][0]
        
        # Include metrics summary if available
        if "ratios" in result_data:
            summary["ratios_count"] = len(result_data["ratios"])
        elif "trends" in result_data:
            summary["trends_count"] = len(result_data["trends"])
        elif "benchmark_comparison" in result_data:
            summary["benchmarks_count"] = len(result_data["benchmark_comparison"])
        
        return summary