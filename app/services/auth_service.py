import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from jose import JWTError, jwt

from app.core.config import (
    CLIENT_SECRET_PATH, 
    REDIRECT_URI, 
    SCOPES, 
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication and authorization."""
    
    @staticmethod
    def create_oauth_flow() -> Flow:
        """Create and return a Google OAuth flow."""
        try:
            flow = Flow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH),
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            return flow
        except Exception as e:
            logger.error(f"Error creating OAuth flow: {e}")
            raise e
    
    @staticmethod
    def get_authorization_url(flow: Flow) -> tuple[str, str]:
        """Get the authorization URL from the flow."""
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        return auth_url, state
    
    @staticmethod
    async def exchange_code_for_tokens(flow: Flow, code: str) -> Dict:
        """Exchange authorization code for tokens."""
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Save the credentials to a token file
            token_path = Path(__file__).resolve().parent.parent.parent / "credentials" / "token.json"
            with open(token_path, "w") as token_file:
                token_file.write(credentials.to_json())
            
            # Create a token dictionary
            token_data = {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            return token_data
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise e
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def validate_token(token: str) -> Optional[Dict]:
        """Validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
            
    @staticmethod
    async def get_user_info(access_token: str) -> Dict:
        """Get Google user info using an access token."""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting user info: {response.text}")
                raise Exception(f"Error getting user info: {response.status_code}")
                
            return response.json()
    
    @staticmethod
    def load_credentials_from_file() -> Optional[Credentials]:
        """Load Google OAuth credentials from a file."""
        token_path = Path(__file__).resolve().parent.parent.parent / "credentials" / "token.json"
        
        if not token_path.exists():
            logger.warning("Token file does not exist")
            return None
        
        try:
            with open(token_path, "r") as token_file:
                token_data = json.load(token_file)
                
            credentials = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes")
            )
            
            return credentials
        except Exception as e:
            logger.error(f"Error loading credentials from file: {e}")
            return None
