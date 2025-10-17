# app/routers/stats_routes.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

# Prefer relative imports; fall back to absolute if needed
try:
    from ..utils.deps import get_db
    from ..models import Sale, Product  # Product is only used to count SKUs if helpful
except Exception:  # pragma: no cover
    from app.utils.deps import get_db
    from app.models import Sale, Product  # type: ignore

router = APIRouter(tags=["stats"])


@router.get("/kpis")
def kpis(
    start: date | None = Query(None, description="Start date (inclusive)"),
    end: date | None = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Aggregate simple KPIs over a window:
      - total revenue
      - total units
      - average order value (revenue / units)
      - SKU count (best effort based on your schema)
    """
    end = end or date.today()
    start = start or (end - timedelta(days=90))

    # Figure out how to identify SKUs, depending on actual DB columns
    has_product_sku = hasattr(Sale, "product_sku")
    has_product_id = hasattr(Sale, "product_id")

    if has_product_sku:
        q = (
            db.query(Sale.product_sku, Sale.sale_date, Sale.units_sold, Sale.revenue)
            .filter(Sale.sale_date >= start, Sale.sale_date <= end)
        )
        rows = q.all()
        revenue = float(sum((r[3] or 0) for r in rows))
        units = int(sum((r[2] or 0) for r in rows))
        skus = len({r[0] for r in rows})
    elif has_product_id:
        q = (
            db.query(Sale.product_id, Sale.sale_date, Sale.units_sold, Sale.revenue)
            .filter(Sale.sale_date >= start, Sale.sale_date <= end)
        )
        rows = q.all()
        revenue = float(sum((r[3] or 0) for r in rows))
        units = int(sum((r[2] or 0) for r in rows))
        # Distinct product_ids in the same window
        skus = int(
            db.query(func.count(func.distinct(Sale.product_id)))
            .filter(Sale.sale_date >= start, Sale.sale_date <= end)
            .scalar()
            or 0
        )
    else:
        # No SKU-ish field on Sale; still compute the basics
        q = (
            db.query(Sale.sale_date, Sale.units_sold, Sale.revenue)
            .filter(Sale.sale_date >= start, Sale.sale_date <= end)
        )
        rows = q.all()
        revenue = float(sum((r[2] or 0) for r in rows))
        units = int(sum((r[1] or 0) for r in rows))
        skus = 0

    aov = (revenue / units) if units else 0.0
    return {"revenue": revenue, "units": units, "aov": aov, "skus": skus}


@router.get("/chart/series")
def chart_series(
    start: date | None = Query(None, description="Start date (inclusive)"),
    end: date | None = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return a simple daily time series:
      [{ date: 'YYYY-MM-DD', revenue: number, units: number }, ...]
    """
    end = end or date.today()
    start = start or (end - timedelta(days=90))

    rows = (
        db.query(Sale.sale_date, Sale.units_sold, Sale.revenue)
        .filter(Sale.sale_date >= start, Sale.sale_date <= end)
        .order_by(Sale.sale_date)
        .all()
    )

    if not rows:
        return []

    series_map: Dict[str, Dict[str, Any]] = {}
    for d, u, r in rows:
        key = d.isoformat()
        entry = series_map.setdefault(key, {"date": key, "revenue": 0.0, "units": 0})
        entry["revenue"] += float(r or 0)
        entry["units"] += int(u or 0)

    return [series_map[k] for k in sorted(series_map.keys())]
