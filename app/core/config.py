"""
Configuration settings for the Allervie Analytics Dashboard FastAPI backend.
"""

import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    # API Settings
    API_V1_STR: str = "/v1"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "allervie-dashboard-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://allervie.bluehighlightedtext.com",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    
    # Google OAuth and Ads API Settings
    REDIRECT_URI: str = os.getenv("REDIRECT_URI", "http://localhost:5002/api/auth/callback")
    SCOPES: List[str] = [
        "https://www.googleapis.com/auth/analytics.readonly", 
        "https://www.googleapis.com/auth/adwords",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/analytics",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/analytics.edit",
        "openid"
    ]
    
    # Credentials Paths
    CREDENTIALS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "credentials")
    CLIENT_SECRET_PATH: str = os.path.join(CREDENTIALS_DIR, "client_secret.json")
    TOKEN_PATH: str = os.path.join(CREDENTIALS_DIR, "token.json")
    
    # Google Ads Settings
    CLIENT_CUSTOMER_ID: str = os.getenv("CLIENT_CUSTOMER_ID", "8127539892")
    
    # Feature Flags
    USE_REAL_ADS_CLIENT: bool = os.getenv("USE_REAL_ADS_CLIENT", "true").lower() == "true"
    ALLOW_MOCK_DATA: bool = os.getenv("ALLOW_MOCK_DATA", "true").lower() == "true"
    ALLOW_MOCK_AUTH: bool = os.getenv("ALLOW_MOCK_AUTH", "true").lower() == "true"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 5002))
    
    # Templates Directory
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

# Create settings instance
settings = Settings()

# Create credentials directory if it doesn't exist
os.makedirs(settings.CREDENTIALS_DIR, exist_ok=True)
