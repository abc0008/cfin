#!/usr/bin/env python
import sys
import os
from pathlib import Path
import uvicorn

# Configure Python's path to include the project root
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(current_dir))
sys.path.append(str(parent_dir))

if __name__ == "__main__":
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"sys.path: {sys.path}")
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(current_dir)],
    ) 