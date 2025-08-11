# app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database settings
    database_url: str = Field(..., env="DATABASE_URL")

    # Security settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(30, env="ACCESS_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")

    # API settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Todo API"

    # API
    debug: bool = Field(False, env="DEBUG")
    backend_cors_origins: List[str] = Field(
        ["http://localhost:3000"],
        env="BACKEND_CORS_ORIGINS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
