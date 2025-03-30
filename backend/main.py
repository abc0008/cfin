import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

from cfin.backend.app.routes import document, conversation, analysis
from pdf_processing.langgraph_service import LangGraphService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize application
app = FastAPI(title="Financial Document Analysis Service API")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://fdas.vercel.app",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing services...")
    # Initialize LangGraph service (will be created on demand through dependency injection)
    try:
        # Validate environment variables are set for LangGraph
        if not os.getenv("ANTHROPIC_API_KEY"):
            logger.warning("ANTHROPIC_API_KEY environment variable not set")
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")

# Include API routers
app.include_router(document.router, prefix="/api")
app.include_router(conversation.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.2.0"}

# Add version endpoint
@app.get("/version")
async def version():
    return {
        "version": "0.2.0",
        "name": "Financial Document Analysis Service",
        "features": [
            "Document processing",
            "Claude integration with citations",
            "LangGraph conversation state management",
            "Financial data extraction"
        ]
    } 