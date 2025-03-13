import uvicorn
import os
import logging
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def main():
    """Start the FastAPI server."""
    try:
        # Check for required environment variables
        required_vars = ["ANTHROPIC_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"The following required environment variables are missing: {', '.join(missing_vars)}")
            logger.error("Please set these variables in your environment or in a .env file")
            sys.exit(1)
        
        # Get server configuration from environment variables
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "False").lower() == "true"
        reload = debug
        log_level = "debug" if debug else "info"
        
        logger.info(f"Starting FastAPI server on {host}:{port} with debug={debug}")
        logger.info("LangChain and LangGraph integration enabled")
        
        # Start the FastAPI server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
        
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()