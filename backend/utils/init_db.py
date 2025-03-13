import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from .database import engine, Base, SessionLocal

logger = logging.getLogger(__name__)

async def create_tables():
    """Create database tables."""
    try:
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

async def create_default_user():
    """Create a default user if no users exist."""
    # Import here to avoid circular imports
    from models.database_models import User
    
    try:
        async with SessionLocal() as session:
            # Check if any users exist
            result = await session.execute(select(User).limit(1))
            existing_user = result.scalars().first()
            
            if not existing_user:
                logger.info("Creating default user...")
                default_user = User(
                    username="default",
                    email="default@example.com",
                    hashed_password="notarealpassword",  # In a real app, this would be properly hashed
                    is_active=True
                )
                session.add(default_user)
                await session.commit()
                logger.info(f"Default user created with ID: {default_user.id}")
                return default_user
            
            logger.info("Default user already exists.")
            return existing_user
    except Exception as e:
        logger.error(f"Error creating default user: {str(e)}")
        raise

async def init_db():
    """Initialize the database."""
    try:
        await create_tables()
        await create_default_user()
        logger.info("Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def run_init_db():
    """Run the database initialization."""
    asyncio.run(init_db())

if __name__ == "__main__":
    run_init_db()