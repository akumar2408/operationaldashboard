from sqlalchemy.orm import Session
from sqlalchemy import select
from collections import defaultdict
import numpy as np
from ..models import Sale, Alert, Product

def zscore_anomalies(db: Session, tenant_id: int, z=2.5):
    rows = db.execute(
        select(Sale.product_id, Sale.sale_date, Sale.units_sold)
        .where(Sale.tenant_id==tenant_id)
        .order_by(Sale.product_id, Sale.sale_date)
    ).all()
    by_prod = defaultdict(list)
    for pid, d, u in rows:
        by_prod[pid].append((d, float(u)))

    out = []
    for pid, seq in by_prod.items():
        vals = np.array([u for _, u in seq], dtype=float)
        if len(vals) < 14:  # need some history
            continue
        # rolling 7-day mean & std (simple)
        for i in range(7, len(vals)):
            window = vals[i-7:i]
            mu, sd = float(window.mean()), float(window.std() or 1.0)
            zval = (vals[i] - mu) / sd
            if abs(zval) >= z:
                kind = "spike" if zval > 0 else "dip"
                sev = "high" if abs(zval) >= 3.5 else ("medium" if abs(zval)>=3.0 else "low")
                out.append({"product_id": pid, "date": seq[i][0], "units": vals[i], "z": float(zval), "type": kind, "severity": sev})
    return out

def create_anomaly_alerts(db: Session, tenant_id: int):
    hits = zscore_anomalies(db, tenant_id)
    # Deduplicate by (product_id,date,type)
    seen = set()
    for h in hits:
        key = (h["product_id"], str(h["date"]), h["type"])
        if key in seen: 
            continue
        seen.add(key)
        msg = f"{h['type']} on {h['date']}: units {h['units']:.1f} (z={h['z']:.2f})"
        db.add(Alert(
            tenant_id=tenant_id,
            product_id=h["product_id"],
            alert_type=h["type"],
            severity=h["severity"],
            message=msg
        ))
    db.commit()
    return {"created": len(seen)}
