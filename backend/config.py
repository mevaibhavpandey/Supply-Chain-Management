from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="AI Trust Validator")
    app_version: str = Field(default="1.0.0")
    database_url: str = Field(default="sqlite+aiosqlite:///./data/trust_validator.db")
    storage_path: str = Field(default="./storage")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    llm_enabled: bool = Field(default=False)
    cors_origins: List[str] = Field(default=["http://localhost:3000"])


settings = Settings()
