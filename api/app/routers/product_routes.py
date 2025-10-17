from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.deps import tenant_guard, db_dep
from ..models import Product
from ..schemas import ProductIn
from fastapi import Query

router = APIRouter(prefix="/products", tags=["products"])

@router.post("")
def create_product(payload: ProductIn, tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    p = Product(tenant_id=tenant_id, sku=payload.sku, name=payload.name)
    db.add(p); db.commit()
    return {"id": p.id, "sku": p.sku, "name": p.name}

@router.get("")
def list_products(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    rows = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    return [{"sku": r.sku, "name": r.name} for r in rows]

@router.post("/{sku}/stock")
def set_stock(sku: str, qty: float = Query(..., ge=0), tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    p = db.query(Product).filter(Product.tenant_id==tenant_id, Product.sku==sku).first()
    if not p: 
        return {"detail":"product not found"}
    p.current_stock = float(qty)
    db.commit()
    return {"sku": p.sku, "current_stock": p.current_stock}

@router.get("/coverage")
def coverage(horizon: int = 14, tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    from ..models import Forecast
    res=[]
    prods = db.query(Product).filter(Product.tenant_id==tenant_id).all()
    for p in prods:
        f = (db.query(Forecast)
                .filter(Forecast.tenant_id==tenant_id, Forecast.product_id==p.id)
                .order_by(Forecast.horizon_date).limit(horizon).all())
        daily = sum(r.units_forecast for r in f)/max(1,len(f))
        cover = (p.current_stock or 0)/daily if daily>0 else None
        res.append({"sku": p.sku, "current_stock": p.current_stock or 0.0, "avg_daily": round(daily,2), "days_of_cover": None if cover is None else round(cover,1)})
    return res