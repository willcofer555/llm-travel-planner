import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # These will automatically map to OPENAI_API_KEY and GOOGLE_MAPS_API_KEY
    openai_api_key: str = ""
    google_maps_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://yourdomain.com"
    
    # OpenAI Configuration
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000
    
    # Rate limiting
    max_requests_per_minute: int = 10
    
    class Config:
        env_file = ".env"


settings = Settings()