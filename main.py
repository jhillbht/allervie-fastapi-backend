"""
Allervie Analytics Dashboard - FastAPI Backend

This FastAPI application serves as the backend for the Allervie Analytics Dashboard,
providing API endpoints for authentication and analytics data.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.api.routers import api_router
from app.core.logging import setup_logging
import logging

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Allervie Analytics API",
    description="Backend API for Allervie Analytics Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Redirect to documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "Allervie Analytics API",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    # Default port is 5002 (to match the Flask app)
    port = int(os.getenv("PORT", 5002))
    
    # Default to development mode
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    # Bind to localhost for development
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 70)
    print(f"Starting Allervie Analytics API on port {port}")
    print(f"Server bound to: {host}")
    print(f"Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"API documentation: http://localhost:{port}/api/docs")
    print(f"Environment: {settings.ENVIRONMENT}")
    print("=" * 70)
    
    # Run the app
    uvicorn.run("main:app", host=host, port=port, reload=debug)
