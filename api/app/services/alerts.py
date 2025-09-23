from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from ..models import Sale, Alert, Product

def evaluate_alerts(db: Session, tenant_id: int, product: Product, low_stock_threshold: float = 5.0):
    last_7 = (db.query(func.avg(Sale.units_sold))
                .filter(Sale.tenant_id==tenant_id, Sale.product_id==product.id)
                .filter(Sale.sale_date >= date.today()-timedelta(days=7)).scalar())
    if last_7 is not None and last_7 < low_stock_threshold:
        msg = f"7-day avg units {last_7:.1f} below threshold {low_stock_threshold}"
        db.add(Alert(tenant_id=tenant_id, product_id=product.id, alert_type="trend_down", message=msg))
        db.commit()

def evaluate_low_cover(db: Session, tenant_id: int, product: Product, horizon=14, threshold_days=5):
    from ..models import Forecast, Alert
    f = (db.query(Forecast)
            .filter(Forecast.tenant_id==tenant_id, Forecast.product_id==product.id)
            .order_by(Forecast.horizon_date).limit(horizon).all())
    if not f: 
        return
    avg_daily = sum(r.units_forecast for r in f)/len(f)
    if avg_daily <= 0:
        return
    stock = product.current_stock or 0.0
    days_left = stock / avg_daily
    if days_left < threshold_days:
        sev = "high" if days_left < threshold_days/2 else "medium"
        msg = f"Low coverage: {days_left:.1f} days left (stock={stock:.0f}, avg_daily={avg_daily:.1f})"
        db.add(Alert(tenant_id=tenant_id, product_id=product.id, alert_type="low_cover", severity=sev, message=msg))
        db.commit()

