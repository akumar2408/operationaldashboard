from pydantic import BaseModel
import os

class Settings(BaseModel):
    cors_origin: str = os.getenv("CORS_ORIGIN", "*")
    env: str = os.getenv("ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
