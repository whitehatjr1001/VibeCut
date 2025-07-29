"""
Configuration management for Video Editing Agent
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # VideoDB Settings
    videodb_api_key: str
    videodb_base_url: str = "https://api.videodb.io"
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Application Settings
    log_level: str = "INFO"
    max_upload_size_mb: int = 500
    temp_dir: Path = Path("./temp")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
