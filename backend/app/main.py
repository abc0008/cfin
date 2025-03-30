from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import logging
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import uvicorn
from fastapi.responses import JSONResponse

from .routes import document, conversation, analysis
from utils.init_db import init_db
from utils.error_handling import http_exception_handler, validation_exception_handler, add_cors_headers
from utils.response import add_cors_headers as add_response_cors_headers

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
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3003"
).split(",")
logger.info(f"CORS: Allowing origins: {allowed_origins}")

# Add CORS middleware directly to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Total-Count"]
)

# Register exception handlers for standardized error responses
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation exception handler that adds CORS headers."""
    response = await validation_exception_handler(request, exc)
    return add_response_cors_headers(response)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler that adds CORS headers."""
    response = await http_exception_handler(request, exc)
    return add_response_cors_headers(response)

# Handle unexpected errors with CORS headers - this needs to be BEFORE the handle_options middleware
@app.middleware("http")
async def add_cors_headers_to_errors(request: Request, call_next):
    """Add CORS headers to all responses including errors."""
    try:
        # Get the origin from the request
        origin = request.headers.get("origin", "*")
        # Check if the origin is allowed
        if origin in allowed_origins or origin == "*":
            allowed_origin = origin
        else:
            allowed_origin = allowed_origins[0] if allowed_origins else "*"
            
        try:
            response = await call_next(request)
            
            # Add CORS headers if needed
            if "access-control-allow-origin" not in response.headers:
                response.headers["Access-Control-Allow-Origin"] = allowed_origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
            
            return response
            
        except Exception as e:
            # For any uncaught exception, make sure we return a response with CORS headers
            logging.exception(f"Unhandled exception: {str(e)}")
            
            # Create error response with CORS headers
            response = JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"}
            )
            response.headers["Access-Control-Allow-Origin"] = allowed_origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            
            return response
    except Exception as outer_e:
        # Last resort fallback
        logging.exception(f"Critical error in CORS middleware: {str(outer_e)}")
        response = JSONResponse(
            status_code=500,
            content={"detail": "Critical internal server error"}
        )
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

# Add a middleware to handle OPTIONS requests for CORS preflight
@app.middleware("http")
async def handle_options(request: Request, call_next):
    if request.method == "OPTIONS":
        # Get the origin from the request
        origin = request.headers.get("origin", "*")
        # Check if the origin is allowed
        if origin in allowed_origins or origin == "*":
            allowed_origin = origin
        else:
            allowed_origin = allowed_origins[0] if allowed_origins else "*"
            
        # Return empty response with CORS headers for preflight requests
        response = JSONResponse(
            status_code=200,
            content={}
        )
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    
    # For non-OPTIONS requests, proceed normally
    return await call_next(request)

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

if __name__ == "__main__":
    # Run the app with uvicorn when script is executed directly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)