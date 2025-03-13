#!/usr/bin/env python
import sys
import os
from pathlib import Path
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure Python's path to include the project root
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(current_dir))
sys.path.append(str(parent_dir))

# Import the FastAPI app manually to see any import errors
print("Trying to import the FastAPI app...")
try:
    from app.main import app
    print("Successfully imported the FastAPI app!")
except Exception as e:
    print(f"ERROR importing app.main: {e}")
    raise

if __name__ == "__main__":
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"sys.path: {sys.path}")
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable reload to see errors
        log_level="debug",
    ) 