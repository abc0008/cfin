from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

from .routes import document, conversation, analysis
from utils.init_db import init_db

# Load environment variables from .env file in the project root
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logging.info(f"Loaded environment variables from {env_path}")
else:
    logging.warning(f".env file not found at {env_path}")

# Verify critical environment variables
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
if not claude_api_key:
    logging.warning("ANTHROPIC_API_KEY not found in environment variables")
else:
    # Mask API key for logging (show first 8 chars and last 4)
    if len(claude_api_key) > 12:
        masked_key = f"{claude_api_key[:8]}...{claude_api_key[-4:]}"
    else:
        masked_key = "***masked***"
    logging.info(f"ANTHROPIC_API_KEY loaded: {masked_key}")

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") != "True" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Financial Document Analysis System API",
    description="API for analyzing financial documents with Claude API",
    version="0.1.0",
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router)
app.include_router(conversation.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Financial Document Analysis System API",
        "version": "0.1.0",
        "endpoints": {
            "documents": "/api/documents",
            "conversation": "/api/conversation",
            "analysis": "/api/analysis"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Continue even if database initialization fails
        # In production, you might want to exit the application
        pass