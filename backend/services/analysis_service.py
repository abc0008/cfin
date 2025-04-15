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

# Define the financial analysis template at module level
financial_analysis_template = """
You are an advanced AI system functioning as a Regional Bank Financial Analyst. Your primary role is to analyze internal financial documents, provide insights on financial trends or anomalies, and create visualizations to illustrate financial data.

First, review the following financial documents and knowledge base:

<financial_documents>
{document_text}
</financial_documents>

<knowledge_base>
{{KNOWLEDGE_BASE}}
</knowledge_base>

Now, analyze the following user query:

<user_query>
{{USER_QUERY}}
</user_query>

Before providing your final response, wrap your analysis planning inside <financial_analysis_planning> tags using the following structure:

1. Query Breakdown: Identify key areas to focus on based on the user query.
2. Relevant Information: Extract and quote pertinent data from the financial documents and knowledge base.
3. Key Data Points: List relevant data points from the provided sources.
4. Financial Ratios and Metrics: Identify and list key ratios and metrics relevant to the query, focusing on those specific to regional banks.
5. Industry Benchmarks: Consider industry benchmarks and how the bank's performance compares.
6. Time Periods: Analyze trends over multiple time periods (e.g., quarter-over-quarter, year-over-year, multi-year trends).
7. Analytical Approach: Outline your approach, including planned calculations and comparisons.
8. Visualization Planning: Plan the following visualizations:
   - Multi-period Balance Sheet Composition stacked Column Chart
   - Balance Sheet Change Analysis Column Chart
   - Asset Composition Line Chart
   - Liability Composition Line Chart
   - Margin Analysis
   - Non-Interest Revenue Trend Chart
   - Non-Interest Revenue Period over period Chart
   - Key Financial Ratio Trend Line Charts
   - Expense Composition Trend Stacked Bar Chart
9. Visualization Insights: For each proposed visualization, list key insights you expect to highlight. These insights should be rendered only within or beneath each chart component in the final artifact.
10. Next Actions: Brainstorm possible deeper analyses that could follow from your initial findings, focusing only on analyses possible with the provided files.
11. Challenges and Limitations: Consider potential challenges or limitations in your analysis.
12. Tool Evaluation: Assess whether the beta analysis tool in Claude.ai could benefit this specific query.
13. External Factors: Identify potential external factors affecting the financial data and explain their possible impacts.
14. Key Terms: List and define key financial terms relevant to the query.
15. Regional Bank Specifics: Identify any metrics or considerations that are particularly important for regional banks.

Guidelines for your analysis and response:

1. Incorporate information from both the financial documents and the knowledge base.
2. Focus on core banking concepts like Funds Transfer Pricing when relevant.
3. Use LaTeX rendering for all mathematical calculations, enclosing formulas in $$ symbols.
4. For period-over-period changes, use the most recent linked quarter unless specified otherwise.
5. Provide detailed explanations, breaking down complex concepts into understandable terms.
6. Highlight any inconsistencies or unusual patterns in the financial data, offering possible explanations.
7. Support all recommendations and insights with data from the financial documents.
8. Consider using the beta analysis tool in Claude.ai when appropriate for deeper financial analysis.
9. Generate a single visualization artifact containing all proposed charts, graphs, and text blocks.
10. Present all analysis and key insights within the artifact using a mixture of cards or text blocks.
11. Use React and Recharts for visualizations with multiple data views.
12. Ensure all cards have the current metric and a period-over-period change percentage.
13. Create all suggested charts without exception.
14. Ensure that "Key Findings" are only rendered in or beneath each chart component within the artifact.
15. For suggested next actions, only propose further analyses of details from the provided financials.

Structure your final response as follows:

<response>
Query Restatement: [Restate the user's query]

Approach Overview: [Brief explanation of your analytical approach]

Artifact:
[Single artifact containing all charts, graphs, text blocks, and cards]
[Include all analysis and key insights within this artifact]
[For each chart, graph, or analysis section:]
   Key Insights:
   - [First key insight]
   - [Second key insight]
   - [Third key insight]

Summary and Recommendations:
[Concise summary of findings and data-supported recommendations]

Suggested Next Actions:
1. [First suggested deeper analysis of provided financials, phrased to directly trigger the next analysis]
2. [Second suggested deeper analysis of provided financials, phrased to directly trigger the next analysis]
3. [Third suggested deeper analysis of provided financials, phrased to directly trigger the next analysis]
</response>

 Provide your response within <response> tags.
"""

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

            # Keep existing analysis type routing
            elif analysis_type == "trend_analysis":
                result_data = await self._run_trend_analysis(document, parameters)
            elif analysis_type == "benchmarking":
                result_data = await self._run_benchmark_analysis(document, parameters)
            elif analysis_type == "sentiment_analysis":
                result_data = await self._run_sentiment_analysis(document, parameters)
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

            # ---> ADD DETAILED LOGGING HERE <---
            logger.info(f"Constructed response_payload for analysis {analysis_response_id}:")
            logger.info(f"Payload keys: {list(response_payload.keys())}")
            try:
                logger.info(f"  - id type: {type(response_payload.get('id'))}")
                logger.info(f"  - documentIds type: {type(response_payload.get('documentIds'))}")
                logger.info(f"  - timestamp type: {type(response_payload.get('timestamp'))}")
                viz_data = response_payload.get('visualizationData')
                logger.info(f"  - visualizationData type: {type(viz_data)}")
                if isinstance(viz_data, dict):
                    logger.info(f"    - charts type: {type(viz_data.get('charts'))}")
                    logger.info(f"    - tables type: {type(viz_data.get('tables'))}")
                    # Log type of first chart/table if they exist
                    if isinstance(viz_data.get('charts'), list) and viz_data.get('charts'):
                        logger.info(f"      - First chart type: {type(viz_data['charts'][0])}")
                    if isinstance(viz_data.get('tables'), list) and viz_data.get('tables'):
                        logger.info(f"      - First table type: {type(viz_data['tables'][0])}")
                metrics_data = response_payload.get('metrics')
                logger.info(f"  - metrics type: {type(metrics_data)}")
                if isinstance(metrics_data, list) and metrics_data:
                    logger.info(f"    - first metric type: {type(metrics_data[0])}")
                # Add logging for other potentially complex fields
                logger.info(f"  - ratios type: {type(response_payload.get('ratios'))}")
                logger.info(f"  - comparativePeriods type: {type(response_payload.get('comparativePeriods'))}")
                logger.info(f"  - insights type: {type(response_payload.get('insights'))}")
                logger.info(f"  - citationReferences type: {type(response_payload.get('citationReferences'))}")
            except Exception as log_e:
                logger.error(f"Error during detailed logging of response_payload: {log_e}")
            # <--- END DETAILED LOGGING --->

            return analysis_response_id, response_payload

        except Exception as e:
            logger.error(f"Error running analysis for document {document_id}: {str(e)}", exc_info=True)
            # Re-raise the exception to be handled by the API layer
            raise

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