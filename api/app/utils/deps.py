# api/app/utils/deps.py
from typing import Generator
from fastapi import Depends

# --- Locate SessionLocal from your project (db.py or database.py) ------------
SessionLocal = None
try:
    from ..db import SessionLocal  # preferred path
except Exception:
    try:
        from ..database import SessionLocal  # alternate filename
    except Exception:
        SessionLocal = None

if SessionLocal is None:
    raise ImportError(
        "SessionLocal not found. Ensure api/app/db.py (or database.py) defines a SQLAlchemy SessionLocal."
    )

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dev shims so existing routers can import these without 401s --------------
# In prod, replace these with real guards.
def tenant_guard():
    """
    Permissive dev guard. Return a simple tenant context.
    Replace with real auth/tenant checks later.
    """
    return {"tenant_id": "dev"}

def db_dep(db=Depends(get_db)):
    """
    Convenience dependency some routers import.
    """
    return db
