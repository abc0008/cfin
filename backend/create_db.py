#!/usr/bin/env python3
"""
Script to create the database schema for FDAS.
Run this script to initialize the database.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import os

from models.database_models import Base
from utils.database import get_db, SyncSessionLocal, sync_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fdas.db")

async def create_database():
    """Create the database tables."""
    try:
        # Create tables
        from models.database_models import (
            User, Document, Citation, MessageCitation, 
            Conversation, ConversationDocument, Message,
            AnalysisResult, AnalysisBlock
        )
        
        # Explicitly import Message for content_blocks column
        logger.info("Ensuring Message model includes content_blocks column")
        
        # Create tables
        async with create_async_engine(
            DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1) if DATABASE_URL.startswith("sqlite") else DATABASE_URL, 
            echo=True
        ) as engine:
            async with engine.begin() as conn:
                logger.info("Creating database tables...")
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully.")
            
            # Create default user
            async with AsyncSession(engine) as session:
                # Check if default user exists
                result = await session.execute(text("SELECT id FROM users WHERE username = 'default'"))
                user = result.scalar_one_or_none()
                
                if not user:
                    # Create default user
                    logger.info("Creating default user...")
                    await session.execute(
                        text("""
                            INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
                            VALUES ('default-user', 'default', 'default@example.com', 'not-a-real-password', 1, CURRENT_TIMESTAMP)
                        """)
                    )
                    await session.commit()
                    logger.info("Default user created successfully.")
                else:
                    logger.info("Default user already exists.")
            
            logger.info("Database initialization completed successfully.")
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}", exc_info=True)
        raise

def create_database_sync():
    """Create the database tables synchronously."""
    try:
        # Create tables
        from models.database_models import (
            User, Document, Citation, MessageCitation, 
            Conversation, ConversationDocument, Message,
            AnalysisResult, AnalysisBlock
        )
        
        # Explicitly import Message for content_blocks column
        logger.info("Ensuring Message model includes content_blocks column")
        
        # Create tables using sync engine
        logger.info("Creating database tables synchronously...")
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        
        logger.info("Database tables created successfully.")
        
        # Create default user
        with SyncSessionLocal() as session:
            # Check if default user exists
            user = session.execute(text("SELECT id FROM users WHERE username = 'default'")).scalar_one_or_none()
            
            if not user:
                # Create default user
                logger.info("Creating default user...")
                session.execute(
                    text("""
                        INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
                        VALUES ('default-user', 'default', 'default@example.com', 'not-a-real-password', 1, CURRENT_TIMESTAMP)
                    """)
                )
                session.commit()
                logger.info("Default user created successfully.")
            else:
                logger.info("Default user already exists.")
        
        logger.info("Database initialization completed successfully.")
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Initializing database...")
    
    # Run the database creation
    if DATABASE_URL.startswith("sqlite"):
        # SQLite - use synchronous version for simplicity
        create_database_sync()
    else:
        # PostgreSQL or other async-compatible DB - use async version
        asyncio.run(create_database())