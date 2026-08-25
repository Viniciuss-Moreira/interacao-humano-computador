from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import BASE_DIR

class Settings(BaseSettings):
    APP_NAME: str = "Estoque API"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = False

    SQLITE_FILE: str = "lojas.db"

    LLM_MODEL: str = "openai/gemma-4-E2B-it-IQ4_XS"
    LLM_API_BASE: str = "http://localhost:1337/v1"
    LLM_API_KEY: str = "not-needed"

    TELEGRAM_TOKEN: str = ""
    WHISPER_MODEL: str = "tiny"

    MAX_LINHAS: int = 200
    TIMEOUT_SEGUNDOS: int = 5

    API_URL: str = "http://127.0.0.1:8000/api"

    @property
    def database_path(self) -> Path:
        return BASE_DIR / self.SQLITE_FILE

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we only parse the environment once."""
    return Settings()


settings = get_settings()