from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class Token(BaseModel):
    """Model for OAuth tokens."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None


class TokenData(BaseModel):
    """Model for token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    scopes: List[str] = []


class User(BaseModel):
    """Model for user data."""
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
