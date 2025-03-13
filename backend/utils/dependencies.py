from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from utils.database import get_db
from repositories.document_repository import DocumentRepository
from repositories.conversation_repository import ConversationRepository
from repositories.analysis_repository import AnalysisRepository
from pdf_processing.document_service import DocumentService
from services.conversation_service import ConversationService
from services.analysis_service import AnalysisService
from utils.storage import StorageService

# Document dependencies
async def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    """
    Get document repository with DB session dependency.
    """
    storage_service = StorageService.get_storage_service()
    return DocumentRepository(db, storage_service)

async def get_document_service(
    document_repository: DocumentRepository = Depends(get_document_repository)
) -> DocumentService:
    """
    Get document service with repository dependency.
    """
    return DocumentService(document_repository)

# Conversation dependencies
async def get_conversation_repository(db: AsyncSession = Depends(get_db)) -> ConversationRepository:
    """
    Get conversation repository with DB session dependency.
    """
    return ConversationRepository(db)

async def get_conversation_service(
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    document_repository: DocumentRepository = Depends(get_document_repository)
) -> ConversationService:
    """
    Get conversation service with repository dependencies.
    """
    return ConversationService(conversation_repository, document_repository)

# Analysis dependencies
async def get_analysis_repository(db: AsyncSession = Depends(get_db)) -> AnalysisRepository:
    """
    Get analysis repository with DB session dependency.
    """
    return AnalysisRepository(db)

async def get_analysis_service(
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository),
    document_repository: DocumentRepository = Depends(get_document_repository)
) -> AnalysisService:
    """
    Get analysis service with repository dependencies.
    """
    return AnalysisService(analysis_repository, document_repository) 