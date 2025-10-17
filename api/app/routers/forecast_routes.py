from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..deps import get_db, tenant_guard
from ..models import Product, Sale

router = APIRouter()


@router.post("/forecast/run")
def run_forecast(
    tenant_id: int = Depends(tenant_guard),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Very simple per-SKU forecast stub so the UI has something to render.
    Joins with Product via product_id (no product_sku column on Sale).
    """
    products: List[Product] = (
        db.query(Product).filter(Product.tenant_id == tenant_id).all()
    )
    if not products:
        return {"ok": True, "results": [], "message": "No products for tenant"}

    results: List[Dict[str, Any]] = []

    for p in products:
        # Aggregate daily history for this product
        series = (
            db.query(
                Sale.sale_date.label("ds"),
                func.sum(Sale.units_sold).label("y_units"),
                func.sum(Sale.revenue).label("y_revenue"),
            )
            .filter(
                Sale.tenant_id == tenant_id,
                Sale.product_id == p.id,  # <-- key fix (no Sale.product_sku)
            )
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date.asc())
            .all()
        )

        # Tiny baseline “forecast”:
        # use the average of the last 7 observed days (or all days if <7)
        if series:
            last_n = series[-7:] if len(series) >= 7 else series
            avg_units = float(sum(r.y_units or 0 for r in last_n)) / max(1, len(last_n))
            avg_rev = float(sum(r.y_revenue or 0 for r in last_n)) / max(1, len(last_n))
        else:
            avg_units = 0.0
            avg_rev = 0.0

        # Return 14 simple daily points starting tomorrow
        start = (series[-1].ds if series else date.today()) + timedelta(days=1)
        horizon = [
            {"ds": (start + timedelta(days=i)).isoformat(),
             "yhat_units": round(avg_units, 3),
             "yhat_revenue": round(avg_rev, 2)}
            for i in range(14)
        ]

        results.append(
            {
                "sku": p.sku,
                "name": p.name,
                "forecast": horizon,
            }
        )

    return {"ok": True, "results": results}
