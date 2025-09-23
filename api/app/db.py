from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

POSTGRES_USER = os.getenv("POSTGRES_USER","dashboard")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","dashboardpw")
POSTGRES_DB = os.getenv("POSTGRES_DB","dashboard")
POSTGRES_HOST = os.getenv("POSTGRES_HOST","postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT","5432")

DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
