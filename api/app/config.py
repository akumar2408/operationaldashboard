from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ENV: str = "local"
    SECRET_KEY: str = "dev"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    POSTGRES_USER: str = "dashboard"
    POSTGRES_PASSWORD: str = "dashboardpw"
    POSTGRES_DB: str = "dashboard"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""

    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
