import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.database_models import Document

logger = logging.getLogger(__name__)

async def verify_document_persistence(db: AsyncSession, document_id: str) -> bool:
    """
    Verify that a document exists in the database.
    
    Args:
        db: Database session
        document_id: ID of the document to verify
        
    Returns:
        True if document exists, False otherwise
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalars().first()
    
    if document:
        logger.info(f"Document {document_id} found in database.")
        return True
    else:
        logger.warning(f"Document {document_id} not found in database.")
        return False

async def test_db_setup(db: AsyncSession) -> bool:
    """
    Test database setup by querying the Document table.
    
    Args:
        db: Database session
        
    Returns:
        True if the database is set up correctly, False otherwise
    """
    try:
        # Test if the Document table exists and can be queried
        result = await db.execute(select(Document).limit(1))
        _ = result.scalars().first()  # Just to execute the query
        logger.info("Database connected successfully and Document table exists.")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False 