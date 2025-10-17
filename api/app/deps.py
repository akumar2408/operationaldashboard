# app/deps.py
from typing import Generator, Optional
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .db import SessionLocal

# DB session dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple “tenant guard”: read X-Tenant-Id header, default to 1 for local dev
def tenant_guard(x_tenant_id: Optional[int] = Header(default=1, alias="X-Tenant-Id")) -> int:
    # You could enforce >0 or lookups here; for now just return an int
    if x_tenant_id is None:
        return 1
    return int(x_tenant_id)
