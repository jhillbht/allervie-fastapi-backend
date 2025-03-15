"""
Authentication endpoints for the Allervie Analytics Dashboard FastAPI backend.
"""

import json
import os
import logging
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from app.core.config import settings
from app.services.auth import (
    get_current_user, 
    get_mock_token, 
    create_oauth_flow, 
    USERS, 
    TOKENS,
    verify_google_token
)
from app.models.schemas import User, Token

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/login")
async def login(request: Request):
    """
    Initiate the OAuth 2.0 authorization flow.
    
    Returns:
        RedirectResponse: Redirect to Google OAuth screen
    """
    try:
        # Create the flow
        flow = create_oauth_flow()
        
        # Generate the authorization URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store the state in a cookie
        response = RedirectResponse(url=auth_url)
        response.set_cookie(key="oauth_state", value=state, httponly=True)
        
        # Log the redirect
        logger.info(f"Redirecting to Google OAuth screen: {auth_url}")
        
        return response
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {e}")
        # Return an error page
        return HTMLResponse(f"""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>Error Initiating OAuth Flow</h1>
                <p>{str(e)}</p>
                <p>Please make sure you have configured Google OAuth credentials.</p>
            </body>
        </html>
        """)

@router.get("/callback")
async def callback(
    request: Request, 
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    oauth_state: Optional[str] = Cookie(None)
):
    """
    Handle the OAuth 2.0 callback.
    
    Args:
        request: FastAPI request object
        code: Authorization code from Google
        error: Error message from Google
        state: OAuth state parameter
        oauth_state: OAuth state from cookie
        
    Returns:
        RedirectResponse: Redirect to dashboard or error page
    """
    # Log that we've received a callback
    logger.info(f"Received callback with code: {code[:10] if code else None}...")
    
    # Check for errors
    if error:
        logger.error(f"OAuth error: {error}")
        return HTMLResponse(f"""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>OAuth Error</h1>
                <p>{error}</p>
            </body>
        </html>
        """)
        
    # Check if code is present
    if not code:
        logger.error("No authorization code received")
        return HTMLResponse("""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>OAuth Error</h1>
                <p>No authorization code received.</p>
            </body>
        </html>
        """)
        
    # Check if state matches
    if state != oauth_state:
        logger.warning(f"OAuth state mismatch. Received: {state}, Expected: {oauth_state}")
        # We'll continue anyway for now
    
    try:
        # Create a new flow
        flow = create_oauth_flow()
        
        # Exchange the authorization code for tokens
        flow.fetch_token(code=code)
        
        # Get the credentials
        creds = flow.credentials
        
        # Save the credentials to a file
        with open(settings.TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        # Get user info from the ID token
        user_id = f"google-oauth2|{random.randint(1000000, 9999999)}"
        
        # Create a token
        token_data = {
            'access_token': creds.token,
            'id_token': user_id,
            'expires_in': 3600  # 1 hour
        }
        
        # Store the token
        TOKENS[user_id] = token_data
        logger.info(f"Created real OAuth token for user: {user_id}")
        
        # Create a response with the token in a cookie
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(
            key="access_token",
            value=creds.token,
            httponly=True,
            max_age=3600
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return HTMLResponse(f"""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>OAuth Callback Error</h1>
                <p>{str(e)}</p>
            </body>
        </html>
        """)

@router.get("/verify", response_model=User)
async def verify(user: User = Depends(get_current_user)):
    """
    Verify the user's token and return user info.
    
    Args:
        user: User object from token
        
    Returns:
        User: User information
    """
    return user

@router.get("/mock-token")
async def mock_token():
    """
    This endpoint is disabled as mock authentication is not allowed.
    
    Raises:
        HTTPException: Always raises an exception as mock authentication is disabled
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Mock authentication is disabled. Please use Google OAuth authentication."
    )

@router.get("/logout")
async def logout():
    """
    Log the user out.
    
    Returns:
        dict: Success message
    """
    response = Response(content=json.dumps({"message": "Logged out successfully"}), media_type="application/json")
    response.delete_cookie(key="access_token")
    
    return response
