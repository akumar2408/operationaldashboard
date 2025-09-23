import pandas as pd
from datetime import date, timedelta
from sqlalchemy.orm import Session
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from ..models import Sale, Product, Forecast

def generate_forecast_for_product(db: Session, tenant_id: int, product: Product, horizon_days: int = 30):
    rows = (db.query(Sale.sale_date, Sale.units_sold)
              .filter(Sale.tenant_id==tenant_id, Sale.product_id==product.id)
              .order_by(Sale.sale_date).all())
    if len(rows) < 10:
        return []
    df = pd.DataFrame(rows, columns=["ds","y"]).set_index("ds").asfreq("D").fillna(0.0)
    model = ExponentialSmoothing(df["y"], trend="add", seasonal=None).fit()
    future_index = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    forecast = model.forecast(horizon_days)
    out = []
    for d, yhat in zip(future_index, forecast):
        f = Forecast(tenant_id=tenant_id, product_id=product.id, horizon_date=d.date(), units_forecast=float(max(yhat,0)))
        db.add(f); out.append(f)
    db.commit()
    return out
