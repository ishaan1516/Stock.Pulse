from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal, List


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # LLM via OpenRouter
    OPENROUTER_API_KEY: str
    LLM_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    LLM_TEMPERATURE: float = 0.4
    MAX_NEWS_TOKENS: int = 8000

    # Search
    TAVILY_API_KEY: str

    # Embeddings
    HF_API_KEY: str
    HF_MODEL_URL: str = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

    # Database
    SUPABASE_URL: str 
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""

    # Security
    INTERNAL_API_KEY: str = "dev-key-change-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:8000"

   
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()