"""
Main FastAPI application module.
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth, google_ads
from app.core.config import settings, AVAILABLE_ENDPOINTS

# Set up logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Allervie Analytics Dashboard API",
    description="API for the Allervie Analytics Dashboard",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="allervie_session",
    max_age=60 * 60 * 24,  # 1 day
    same_site="lax",
    https_only=settings.ENVIRONMENT == "production",
)

# Create credentials directory if it doesn't exist
os.makedirs(settings.CREDENTIALS_DIR, exist_ok=True)

# Create static directory for serving files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(google_ads.router, prefix="/api")


# Root endpoint that redirects to the OAuth login
@app.get("/")
async def root():
    """
    Root endpoint that redirects to OAuth login.
    """
    return {"message": "Allervie Analytics Dashboard API", "redirect": "/api/auth/login"}


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "Allervie Analytics API",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


# List available API endpoints
@app.get("/api/endpoints")
async def list_endpoints():
    """
    List all available API endpoints.
    """
    return AVAILABLE_ENDPOINTS


# Add exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", settings.PORT))
    
    print("=" * 70)
    print(f"Starting Allervie Analytics API on port {port}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {'enabled' if settings.DEBUG else 'disabled'}")
    print(f"Documentation: http://localhost:{port}/api/docs")
    print(f"Allowed origins: {settings.CORS_ORIGINS}")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=port,
        reload=settings.ENVIRONMENT == "development",
        log_level="info" if settings.ENVIRONMENT == "production" else "debug",
    )
