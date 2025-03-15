"""
Authentication service for the Allervie Analytics Dashboard FastAPI backend.
"""

import os
import json
import logging
import random
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.core.config import settings
from app.models.schemas import TokenData, User, Token

logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Mock user database (in a real app, this would be a proper database)
USERS = {
    'google-oauth2|123456789': {
        'id': 'google-oauth2|123456789',
        'name': 'Test User',
        'email': 'test@example.com',
        'picture': 'https://ui-avatars.com/api/?name=Test+User&background=0D8ABC&color=fff'
    }
}

# Mock token storage (in a real app, this would be stored securely)
TOKENS = {}

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        str: Encoded JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.
    
    Args:
        token: JWT token
        
    Returns:
        User: User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id)
    except JWTError:
        # Try to check if this is a Google OAuth token
        try:
            user = verify_google_token(token)
            if user:
                return user
        except Exception:
            pass
                
        raise credentials_exception
        
    # Get the user from the database
    user = USERS.get(token_data.user_id)
    
    if user is None:
        raise credentials_exception
        
    return User(**user)

def verify_google_token(token: str) -> Optional[User]:
    """
    Verify a Google OAuth token.
    
    Args:
        token: Google OAuth token
        
    Returns:
        Optional[User]: User object if token is valid, None otherwise
    """
    try:
        # Create credentials from the token
        creds = Credentials(token=token)
        
        # Try to use the credentials to access userinfo API
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        
        # Create a user ID
        user_id = f"google-oauth2|{user_info['id']}"
        
        # Create a user if it doesn't exist
        if user_id not in USERS:
            USERS[user_id] = {
                'id': user_id,
                'name': user_info.get('name', 'Google User'),
                'email': user_info.get('email', 'unknown@example.com'),
                'picture': user_info.get('picture', '')
            }
            
        return User(**USERS[user_id])
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return None

def create_oauth_flow(redirect_uri: Optional[str] = None) -> InstalledAppFlow:
    """
    Create a Google OAuth 2.0 flow.
    
    Args:
        redirect_uri: Optional redirect URI
        
    Returns:
        InstalledAppFlow: OAuth 2.0 flow
        
    Raises:
        Exception: If client secret file not found
    """
    # Check if client_secret.json exists
    if not os.path.exists(settings.CLIENT_SECRET_PATH):
        # Try to find it in the current directory
        if os.path.exists('client_secret.json'):
            client_secret_path = 'client_secret.json'
        else:
            raise Exception("No client_secret.json found. Please configure Google OAuth credentials.")
    else:
        client_secret_path = settings.CLIENT_SECRET_PATH
        
    # Use provided redirect URI or default
    if not redirect_uri:
        redirect_uri = settings.REDIRECT_URI
        
    # Create the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_path,
        scopes=settings.SCOPES,
        redirect_uri=redirect_uri
    )
    
    return flow

def get_mock_token() -> Token:
    """
    Get a mock authentication token for testing.
    
    Returns:
        Token: Mock token
    
    Raises:
        HTTPException: Always raises an exception as mock authentication is disabled
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Mock authentication is disabled. Please use Google OAuth authentication."
    )
