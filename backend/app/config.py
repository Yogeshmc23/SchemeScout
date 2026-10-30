from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    enable_research_history: bool = False
    database_url: SecretStr | None = None
    tinyfish_api_key: SecretStr | None = None
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    frontend_origin: str = "http://localhost:3000"
    request_timeout: float = Field(90, ge=1, le=300)
    max_concurrent_workflows: int = Field(2, ge=1, le=8)


@lru_cache
def settings() -> Settings:
    return Settings()
