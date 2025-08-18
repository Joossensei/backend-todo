# app/core/config.py
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database settings
    database_url: str = Field(..., json_schema_extra={"env": "DATABASE_URL"})

    # Security settings
    SECRET_KEY: str = Field(..., json_schema_extra={"env": "SECRET_KEY"})
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(
        30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_DAYS"}
    )
    ALGORITHM: str = Field("HS256", json_schema_extra={"env": "ALGORITHM"})
    JWT_ISSUER: str = Field("todo-api", json_schema_extra={"env": "JWT_ISSUER"})
    JWT_AUDIENCE: str = Field(
        "todo-api-client", json_schema_extra={"env": "JWT_AUDIENCE"}
    )
    JWT_LEEWAY: int = Field(60, json_schema_extra={"env": "JWT_LEEWAY"})

    # API settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Todo API"

    # API
    debug: bool = Field(False, json_schema_extra={"env": "DEBUG"})
    backend_cors_origins: List[str] = Field(
        ["http://localhost:3000"], json_schema_extra={"env": "BACKEND_CORS_ORIGINS"}
    )

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    db_pool_min: int = Field(1, json_schema_extra={"env": "DB_POOL_MIN"})
    db_pool_max: int = Field(10, json_schema_extra={"env": "DB_POOL_MAX"})


settings = Settings()
