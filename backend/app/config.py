"""
Configuration settings for WeatherGPT backend.
Reads from environment variables and .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "WeatherGPT"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Databases
    DATABASE_URL: str = "sqlite+aiosqlite:///./weathergpt.db"
    MONGODB_URL: str = "mongodb://localhost:27017/weathergpt"
    USE_LOCAL_BULLETIN_STORE: bool = True

    # LLM configuration
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Weather Endpoints
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    GEOCODING_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1"
    HISTORICAL_METEO_BASE_URL: str = "https://archive-api.open-meteo.com/v1"
    IMD_BULLETIN_FEED_URL: str = "https://mausam.imd.gov.in/responsive/all_india_bulletin.php"
    GDACS_FEED_URL: str = "https://www.gdacs.org/xml/rss.xml"

    # Cache TTLs (in seconds)
    CACHE_TTL_LIVE_OBS: int = 600       # 10 minutes
    CACHE_TTL_FORECAST: int = 3600      # 1 hour
    CACHE_TTL_NWP: int = 10800          # 3 hours
    CACHE_TTL_BULLETINS: int = 900      # 15 minutes
    CACHE_TTL_CLIMATE: int = 86400      # 24 hours

settings = Settings()
