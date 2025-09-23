from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import tenant_guard, db_dep
from ..models import Tenant

router = APIRouter(prefix="/tenant", tags=["tenant"])

@router.get("/me")
def me(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    t = db.get(Tenant, tenant_id)
    return {"tenant_id": t.id, "name": t.name}
