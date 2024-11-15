from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    # Azure AD Auth Settings
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    REDIRECT_URI: Optional[str] = None
    SESSION_SECRET_KEY: Optional[str] = None
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Static File Paths
    STATIC_DIR: str = "../frontend/build/static"
    ASSETS_DIR: str = "../frontend/build/assets"
    BUILD_DIR: str = "../frontend/build"
    
    # Azure Document Intelligence settings
    AZURE_ENDPOINT: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    
    # Azure OpenAI settings
    OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings() 