# app/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- CORS / misc ---
    CORS_ORIGINS: str = ""            # comma-separated list, optional
    cors_origin: str = "http://localhost:5173"  # single-origin fallback

    # --- AWS (optional) ---
    AWS_REGION: str | None = None
    S3_BUCKET: str | None = None

    # --- Database ---
    # Accept a single DATABASE_URL (works for Postgres or SQLite)
    DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")

    # Or, build from parts if you prefer PG piecewise envs:
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # IMPORTANT: don't crash on extra env vars
    )

    def db_uri(self) -> str:
        """Resolve the SQLAlchemy database URI."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.POSTGRES_HOST and self.POSTGRES_USER and self.POSTGRES_DB:
            pw = self.POSTGRES_PASSWORD or ""
            return (
                f"postgresql+psycopg://{self.POSTGRES_USER}:{pw}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Default: file-based SQLite in the api/ folder (great for local dev)
        return "sqlite:///./local.db"


_settings_cache: Settings | None = None


def get_settings() -> Settings:
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = Settings()
    return _settings_cache
