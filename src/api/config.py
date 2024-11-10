# src/api/config.py

from pydantic import BaseModel
from typing import List

class Settings(BaseModel):
    """
    Server configuration settings using Pydantic.
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GPU-Accelerated AI Server"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # GPU Settings
    MIN_MEMORY_AVAILABLE: int = 4000  # Minimum 4GB required
    MAX_BATCH_SIZE: int = 32
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()