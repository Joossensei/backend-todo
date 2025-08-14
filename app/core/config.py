# app/core/config.py
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database settings
    # Provide sensible defaults so the package can be imported without
    # relying on environment variables during tests.
    database_url: str = Field(
        "postgresql://user:pass@localhost:5432/db",
        json_schema_extra={"env": "DATABASE_URL"},
    )

    # Security settings
    SECRET_KEY: str = Field(
        "change-me", json_schema_extra={"env": "SECRET_KEY"}
    )
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(
        30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_DAYS"}
    )
    ALGORITHM: str = Field("HS256", json_schema_extra={"env": "ALGORITHM"})

    # API settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Todo API"

    # API
    debug: bool = Field(False, json_schema_extra={"env": "DEBUG"})
    backend_cors_origins: List[str] = Field(
        ["http://localhost:3000"], json_schema_extra={"env": "BACKEND_CORS_ORIGINS"}
    )

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
