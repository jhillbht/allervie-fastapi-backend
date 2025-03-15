"""
API routes for authentication.
"""

import secrets
from datetime import timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.services.auth import (
    create_auth_url,
    exchange_code_for_tokens,
    get_user_info,
    create_access_token,
    get_current_user,
    USERS,
    TOKENS
)
from app.models.ads_models import UserData, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginResponse(BaseModel):
    """
    Response model for login endpoint.
    """
    auth_url: str


class TokenResponse(BaseModel):
    """
    Response model for token endpoint.
    """
    access_token: str
    token_type: str
    id_token: Optional[str] = None
    expires_in: int


class VerifyResponse(BaseModel):
    """
    Response model for verify endpoint.
    """
    isAuthenticated: bool
    user: Optional[UserData] = None
    error: Optional[str] = None


@router.get("/login", response_model=LoginResponse)
async def login():
    """
    Initiate the OAuth 2.0 authorization flow.
    
    Returns:
        Dictionary with authorization URL and state parameter
    """
    auth_data = create_auth_url()
    
    # Set the state in a cookie and return the auth URL
    response = JSONResponse(content={"auth_url": auth_data["auth_url"]})
    response.set_cookie(
        key="oauth_state",
        value=auth_data["state"],
        httponly=True,
        max_age=600,  # 10 minutes
        secure=settings.ENVIRONMENT == "production",
        samesite="lax"
    )
    
    return response


@router.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    oauth_state: Optional[str] = Cookie(None)
):
    """
    Handle the OAuth 2.0 callback.
    
    This endpoint receives the authorization code from the OAuth provider
    and exchanges it for access and refresh tokens.
    
    Args:
        code: Authorization code from OAuth provider
        state: State parameter for CSRF protection
        error: Error message from OAuth provider
        oauth_state: State parameter from cookie
        
    Returns:
        Redirect to the frontend with success or error
    """
    # Check if there was an error
    if error:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={error}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Check if the code is present
    if not code:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=missing_code",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Validate state parameter to prevent CSRF attacks
    if not state or not oauth_state or state != oauth_state:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=invalid_state",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Exchange the authorization code for tokens
    token_data = await exchange_code_for_tokens(code)
    
    if not token_data:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=token_exchange_failed",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Get user info from the ID token or userinfo endpoint
    user_info = await get_user_info(token_data["access_token"])
    
    if not user_info:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=user_info_failed",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Generate a unique user ID
    user_id = f"google-oauth2|{user_info.get('id')}"
    
    # Store user in "database"
    USERS[user_id] = {
        "id": user_id,
        "name": user_info.get("name", "Unknown User"),
        "email": user_info.get("email", "unknown@example.com"),
        "picture": user_info.get("picture")
    }
    
    # Create a token for the user
    token_data = {
        "access_token": token_data["access_token"],
        "id_token": token_data.get("id_token"),
        "expires_in": token_data.get("expires_in", 3600)
    }
    
    # Store token
    TOKENS[user_id] = token_data
    
    # Create a JWT token for the frontend
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=access_token_expires
    )
    
    # Redirect to the frontend with the token
    redirect_url = f"{settings.FRONTEND_URL}/dashboard?token={access_token}"
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    
    # Clear the state cookie
    response.delete_cookie(key="oauth_state")
    
    return response


@router.get("/verify", response_model=VerifyResponse)
async def verify(current_user: Optional[UserData] = Depends(get_current_user)):
    """
    Verify the user's token and return user info.
    
    Args:
        current_user: User data from token
        
    Returns:
        VerifyResponse: Authentication status and user info
    """
    if current_user:
        return VerifyResponse(isAuthenticated=True, user=current_user)
    else:
        return VerifyResponse(isAuthenticated=False, error="Invalid token")


@router.get("/mock-token", include_in_schema=settings.ENVIRONMENT != "production")
async def mock_token():
    """
    Create a mock auth token for testing.
    
    This endpoint is only available in development mode.
    
    Returns:
        Dictionary with mock token and user info
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mock authentication is disabled in production mode"
        )
    
    # Create a mock user ID
    user_id = "google-oauth2|123456789"
    
    # Create a mock token
    token_data = {
        "access_token": f"mock-token-{secrets.token_hex(8)}",
        "id_token": user_id,
        "expires_in": 3600
    }
    
    # Store the token
    TOKENS[user_id] = token_data
    
    # Create a JWT token for the frontend
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "status": "success",
        "message": "Mock authentication successful",
        "token": access_token,
        "user_id": user_id
    }
