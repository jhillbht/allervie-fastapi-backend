"""
Launcher script for the FastAPI application.
"""

import os
import sys
import logging
from app.main import app
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 5002))
    
    print("=" * 70)
    print(f"Starting Allervie Analytics API on port {port}")
    print(f"Server bound to: localhost")
    print(f"Documentation: http://localhost:{port}/api/docs")
    print(f"Dashboard URLs:")
    print(f" - http://localhost:3000/dashboard")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=port,
        reload=True,
        log_level="info",
    )
