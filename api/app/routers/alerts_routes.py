from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import tenant_guard, db_dep
from ..models import Product, Alert
from ..services.alerts import evaluate_alerts, evaluate_low_cover

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/evaluate")
def eval_alerts(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    for p in products:
        evaluate_alerts(db, tenant_id, p)
    from ..services.anomaly import create_anomaly_alerts
    create_anomaly_alerts(db, tenant_id)
    for p in products:
        evaluate_low_cover(db, tenant_id, p)
    return {"status": "ok", **out}
    

@router.get("")
def list_alerts(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    rows = db.query(Alert).filter(Alert.tenant_id == tenant_id).order_by(Alert.created_at.desc()).all()
    return [{
        "id": r.id, "product_id": r.product_id, "alert_type": r.alert_type,
        "message": r.message, "acknowledged": r.acknowledged, "created_at": r.created_at.isoformat()
    } for r in rows]
