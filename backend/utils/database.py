import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

# Import sqlite3 error classes for aiosqlite
import aiosqlite
aiosqlite.DatabaseError = sqlite3.DatabaseError
aiosqlite.Error = sqlite3.Error

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fdas.db")

# Convert SQLite URL to work with SQLAlchemy asynchronous
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, we need to convert to the async variant
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "True" else False,
    future=True,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# For non-async operations
sync_engine = None
SyncSessionLocal = None

if DATABASE_URL.startswith("sqlite+aiosqlite"):
    # Create sync engine for SQLite
    sync_url = DATABASE_URL.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
    sync_engine = create_engine(sync_url, connect_args={"check_same_thread": False})
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
else:
    # For PostgreSQL or other databases
    sync_url = DATABASE_URL.replace("+asyncpg", "", 1) if "+asyncpg" in DATABASE_URL else DATABASE_URL
    sync_engine = create_engine(sync_url)
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)