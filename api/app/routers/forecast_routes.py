from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import tenant_guard, db_dep
from ..models import Product, Forecast
from ..services.forecasting import generate_forecast_for_product

router = APIRouter(prefix="/forecast", tags=["forecast"])

@router.post("/run")
def run_forecast(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    total = 0
    for p in products:
        out = generate_forecast_for_product(db, tenant_id, p)
        total += len(out)
    return {"created": total}

@router.get("")
def list_forecast(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    rows = (db.query(Forecast).filter(Forecast.tenant_id==tenant_id).order_by(Forecast.product_id, Forecast.horizon_date).all())
    return [{"product_id": r.product_id, "horizon_date": r.horizon_date.isoformat(), "units_forecast": r.units_forecast} for r in rows]
