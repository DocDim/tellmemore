# config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict # Import SettingsConfigDict

class Settings(BaseSettings):
    # This will load environment variables from .env file
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    FRONTEND_PORT: int = 8080
    BACKEND_API_URL: str = "http://127.0.0.1:8000/api/v1"
    # New setting for the LLM API base URL
    LLM_API_BASE_URL: str = "http://127.0.0.1:8001" # Default value as provided by you

settings = Settings()

print(f"DEBUG (frontend config.py): BACKEND_API_URL loaded: {settings.BACKEND_API_URL}")
print(f"DEBUG (frontend config.py): LLM_API_BASE_URL loaded: {settings.LLM_API_BASE_URL}")