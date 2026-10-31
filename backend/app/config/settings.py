import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Google API Key
    GOOGLE_API_KEY: str = ""

    # Neon PostgreSQL connection string
    DATABASE_URL: str = ""

    # Embedding configuration
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768

    # LLM configuration (respects user-chosen model)
    GEMINI_CHAT_MODEL: str = "gemini-3.5-flash-lite"

    # Frontend configuration for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Hybrid Retrieval RRF parameter
    RRF_K: int = 60
    TOP_K: int = 10

    # Dataset default metadata
    DATASET_YEAR: int = 2026
    COUNSELLING_ROUND: int = 1
    SEAT_REGION: str = "Rest of Karnataka"

    # Check both .env.local and .env in backend directory
    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(__file__), "../../.env.local"),
            os.path.join(os.path.dirname(__file__), "../../.env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
