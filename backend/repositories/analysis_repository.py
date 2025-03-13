import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, and_, desc, or_

from models.database_models import AnalysisResult, Document, User

logger = logging.getLogger(__name__)

class AnalysisRepository:
    """Repository for analysis operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the analysis repository."""
        self.db = db
    
    async def create_analysis(
        self,
        document_id: str,
        analysis_type: str,
        result_data: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Create a new analysis result.
        
        Args:
            document_id: ID of the document being analyzed
            analysis_type: Type of analysis (e.g., "financial_ratios", "sentiment", etc.)
            result_data: JSON data containing analysis results
            
        Returns:
            Created analysis result
        """
        # Create the analysis record
        analysis = AnalysisResult(
            id=str(uuid.uuid4()),
            document_id=document_id,
            analysis_type=analysis_type,
            result_data=result_data,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        
        return analysis
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """
        Get an analysis result by ID.
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            Analysis result if found, None otherwise
        """
        result = await self.db.execute(
            select(AnalysisResult).where(AnalysisResult.id == analysis_id)
        )
        return result.scalars().first()
    
    async def list_document_analyses(
        self,
        document_id: str,
        analysis_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisResult]:
        """
        List analysis results for a document.
        
        Args:
            document_id: ID of the document
            analysis_type: Optional analysis type to filter by
            limit: Maximum number of results to return
            offset: Starting index
            
        Returns:
            List of analysis results
        """
        query = select(AnalysisResult).where(AnalysisResult.document_id == document_id)
        
        if analysis_type:
            query = query.where(AnalysisResult.analysis_type == analysis_type)
        
        query = query.order_by(desc(AnalysisResult.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def list_latest_analyses(
        self,
        document_ids: List[str],
        analysis_type: Optional[str] = None,
        limit: int = 10
    ) -> List[AnalysisResult]:
        """
        List the latest analysis results for multiple documents.
        
        Args:
            document_ids: List of document IDs
            analysis_type: Optional analysis type to filter by
            limit: Maximum number of results to return per document
            
        Returns:
            List of analysis results
        """
        query = (
            select(AnalysisResult)
            .where(AnalysisResult.document_id.in_(document_ids))
        )
        
        if analysis_type:
            query = query.where(AnalysisResult.analysis_type == analysis_type)
        
        query = query.order_by(desc(AnalysisResult.created_at))
        
        # Use a window function to get the latest N analyses per document
        # This is a bit complex with SQLAlchemy, so we'll just get all and filter
        result = await self.db.execute(query)
        all_analyses = result.scalars().all()
        
        # Group by document_id
        analyses_by_document = {}
        for analysis in all_analyses:
            if analysis.document_id not in analyses_by_document:
                analyses_by_document[analysis.document_id] = []
            
            if len(analyses_by_document[analysis.document_id]) < limit:
                analyses_by_document[analysis.document_id].append(analysis)
        
        # Flatten the dictionary into a list
        latest_analyses = []
        for doc_analyses in analyses_by_document.values():
            latest_analyses.extend(doc_analyses)
        
        # Sort by created_at (newest first)
        latest_analyses.sort(key=lambda x: x.created_at, reverse=True)
        
        return latest_analyses
    
    async def update_analysis(
        self,
        analysis_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[AnalysisResult]:
        """
        Update an analysis result.
        
        Args:
            analysis_id: ID of the analysis
            update_data: Dictionary of fields to update
            
        Returns:
            Updated analysis result if found, None otherwise
        """
        await self.db.execute(
            update(AnalysisResult)
            .where(AnalysisResult.id == analysis_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_analysis(analysis_id)
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis result.
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            True if analysis was deleted, False otherwise
        """
        # Delete from database
        await self.db.execute(
            delete(AnalysisResult).where(AnalysisResult.id == analysis_id)
        )
        await self.db.commit()
        
        return True
    
    async def count_document_analyses(
        self,
        document_id: str,
        analysis_type: Optional[str] = None
    ) -> int:
        """
        Count the number of analysis results for a document.
        
        Args:
            document_id: ID of the document
            analysis_type: Optional analysis type to filter by
            
        Returns:
            Number of analysis results
        """
        query = select(func.count()).select_from(AnalysisResult).where(AnalysisResult.document_id == document_id)
        
        if analysis_type:
            query = query.where(AnalysisResult.analysis_type == analysis_type)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def search_analyses(
        self,
        document_ids: List[str],
        query: str,
        analysis_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisResult]:
        """
        Search analysis results by content.
        
        Args:
            document_ids: List of document IDs to search within
            query: Search query
            analysis_type: Optional analysis type to filter by
            limit: Maximum number of results to return
            offset: Starting index
            
        Returns:
            List of matching analysis results
        """
        # We need to search in the JSON result_data, which is more complex
        # For simplicity, we'll convert the JSON to a string and search in that
        # In a real implementation, you might want to use the database's JSON search capabilities
        
        # Get all analyses for the documents
        base_query = (
            select(AnalysisResult)
            .where(AnalysisResult.document_id.in_(document_ids))
        )
        
        if analysis_type:
            base_query = base_query.where(AnalysisResult.analysis_type == analysis_type)
        
        # For PostgreSQL you would use something like:
        # base_query = base_query.where(
        #     func.json_to_string(AnalysisResult.result_data).ilike(f"%{query}%")
        # )
        
        # Since we're using SQLite for development, we'll fetch all and filter in Python
        result = await self.db.execute(base_query)
        all_analyses = result.scalars().all()
        
        # Filter by query
        matching_analyses = []
        for analysis in all_analyses:
            result_data_str = str(analysis.result_data)
            if query.lower() in result_data_str.lower():
                matching_analyses.append(analysis)
        
        # Sort by created_at (newest first) and apply limit/offset
        matching_analyses.sort(key=lambda x: x.created_at, reverse=True)
        return matching_analyses[offset:offset + limit]