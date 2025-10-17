# app/routers/tenant_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Our project-standard DB dependency
from ..utils.deps import get_db

router = APIRouter(prefix="/tenant", tags=["tenant"])

# --- Local/dev “tenant” helpers ---------------------------------------------
# In dev we don't require auth; just say tenant_id = 1.
def tenant_guard() -> int:
    return 1

# Alias for dependency signature parity with older code
def db_dep() -> Session:
    return next(get_db())

# --- Routes ------------------------------------------------------------------
@router.get("/me")
def me(
    tenant_id: int = Depends(tenant_guard),
    db: Session = Depends(get_db),
):
    # In a real app, you’d look up the tenant record using tenant_id.
    # For local/dev, return a simple stub.
    return {"id": tenant_id, "name": "local"}
