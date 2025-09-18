import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")   
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    debug: bool = Field(..., env="DEBUG")

    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    usda_api_url: str = Field(..., env="USDA_API_URL")
    usda_api_key: str = Field(..., env="USDA_API_KEY")
    usda_page_size: int = Field(default=5, env="USDA_PAGE_SIZE")

    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")
    redis_db: int = Field(..., env="REDIS_DB")

    rate_limit_time: int = Field(default=5, env="RATE_LIMIT_TIME")
    rate_limit: int = Field(default=1, env="RATE_LIMIT")

    class Config:
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()