from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Any, Dict
import csv, io
from ..deps import get_db, tenant_guard
from ..models import Product, Sale

router = APIRouter()

@router.post("/sales/upload/local")
async def upload_sales_csv_local(
    file: UploadFile = File(...),
    tenant_id: int = Depends(tenant_guard),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Local dev upload: parse a CSV directly (no S3). Expected columns:
    date, sku, units, revenue
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw = await file.read()
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read CSV as UTF-8")

    rows = 0
    for row in reader:
        # basic validation / normalization
        sku = (row.get("sku") or "").strip()
        dt = (row.get("date") or "").strip()
        units = float(row.get("units") or 0)
        revenue = float(row.get("revenue") or 0)

        if not sku or not dt:
            # skip bad rows quietly (or collect errors if you prefer)
            continue

        prod = (
            db.query(Product)
            .filter(Product.tenant_id == tenant_id, Product.sku == sku)
            .first()
        )
        if not prod:
            prod = Product(tenant_id=tenant_id, sku=sku, name=sku)
            db.add(prod)
            db.flush()

        sale = Sale(
            tenant_id=tenant_id,
            product_id=prod.id,
            sale_date=dt,  # ISO yyyy-mm-dd works with SQLite/Pg date columns
            units_sold=units,
            revenue=revenue,
        )
        db.add(sale)
        rows += 1

    db.commit()
    return {"ok": True, "inserted": rows}
