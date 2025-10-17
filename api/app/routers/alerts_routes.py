# app/routers/alerts_routes.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

try:
    from ..utils.deps import get_db, tenant_guard
    from ..models import Sale
except Exception:  # pragma: no cover
    from app.utils.deps import get_db, tenant_guard  # type: ignore
    from app.models import Sale  # type: ignore

router = APIRouter(tags=["alerts"])


def eval_alerts(*, tenant_id: int, db: Session, days: int = 7) -> Dict[str, Any]:
    """
    Recompute simple alerts: compare 'today' vs last N-day average.
    Returns: {"alerts": [{type, date, value, baseline}, ...]}
    """
    today = date.today()
    start = today - timedelta(days=days)

    # Pull today's totals
    t_units, t_rev = (
        db.query(
            func.coalesce(func.sum(Sale.units_sold), 0),
            func.coalesce(func.sum(Sale.revenue), 0.0),
        )
        .filter(Sale.sale_date == today)
        .one()
    )

    # Pull baseline totals over the last N days (excluding today)
    b_units, b_rev = (
        db.query(
            func.coalesce(func.avg(Sale.units_sold), 0),
            func.coalesce(func.avg(Sale.revenue), 0.0),
        )
        .filter(Sale.sale_date >= start, Sale.sale_date < today)
        .one()
    )

    alerts: List[Dict[str, Any]] = []

    # Simple heuristics; tweak as desired
    if b_units and t_units < 0.5 * b_units:
        alerts.append(
            {
                "type": "units_drop",
                "date": today.isoformat(),
                "value": float(t_units),
                "baseline": float(b_units),
            }
        )
    if b_rev and t_rev < 0.5 * b_rev:
        alerts.append(
            {
                "type": "revenue_drop",
                "date": today.isoformat(),
                "value": float(t_rev),
                "baseline": float(b_rev),
            }
        )

    return {"alerts": alerts}


@router.get("/alerts")
def list_alerts(
    days: int = Query(7, ge=1, le=60),
    tenant_id: int = Depends(tenant_guard),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Pass a plain int to the helper (no Query objects in helpers)
    return eval_alerts(tenant_id=tenant_id, db=db, days=days)  # type: ignore[arg-type]
