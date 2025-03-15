"""
API routers for the Allervie Analytics Dashboard FastAPI backend.
"""

from fastapi import APIRouter
from app.api.endpoints import auth, dashboard, google_ads, diagnostics

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(google_ads.router, prefix="/google-ads", tags=["google ads"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])
