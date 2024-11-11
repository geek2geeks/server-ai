# src/api/config.py

from pydantic import BaseSettings, SecretStr, Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Server configuration settings using Pydantic with environment variables."""
    
    # Project Settings
    PROJECT_NAME: str = "GPU-Accelerated AI Server"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # API Settings
    API_SECRET_KEY: SecretStr = Field(..., env='API_SECRET_KEY')
    API_RATE_LIMIT: int = 100
    API_RATE_LIMIT_PERIOD: int = 60
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # GPU Settings
    GPU_MEMORY_FRACTION: float = 0.9
    MIN_MEMORY_AVAILABLE: int = 4000  # Minimum 4GB required
    MAX_BATCH_SIZE: int = 32
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr = Field(..., env='REDIS_PASSWORD')
    REDIS_TLS_ENABLED: bool = True
    REDIS_DB: int = 0
    
    # Storage Settings
    AI_DATA_PATH: Path = Field(..., env='AI_DATA_PATH')
    MODEL_CACHE_PATH: Path = Field(..., env='MODEL_CACHE_PATH')
    
    # Monitoring Settings
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name.endswith('_PATH'):
                return Path(raw_val)
            return cls.json_loads(raw_val)

# Create settings instance
settings = Settings()