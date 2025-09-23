from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from ..deps import tenant_guard, db_dep
from ..models import Product, Sale
from ..utils.s3 import presign_csv_post, read_csv_from_s3

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    content = await file.read()
    df = pd.read_csv(BytesIO(content))  # product_sku,sale_date,units_sold,revenue
    skus = df["product_sku"].unique().tolist()
    existing = {p.sku:p for p in db.query(Product).filter(Product.tenant_id==tenant_id, Product.sku.in_(skus)).all()}
    for sku in skus:
        if sku not in existing:
            db.add(Product(tenant_id=tenant_id, sku=sku, name=sku))
    db.flush()
    existing = {p.sku:p for p in db.query(Product).filter(Product.tenant_id==tenant_id, Product.sku.in_(skus)).all()}

    for row in df.itertuples(index=False):
        db.add(Sale(
            tenant_id=tenant_id,
            product_id=existing[row.product_sku].id,
            sale_date=pd.to_datetime(getattr(row,'sale_date')).date(),
            units_sold=float(getattr(row,'units_sold')),
            revenue=float(getattr(row,'revenue'))
        ))
    db.commit()
    return {"rows": len(df)}

@router.get("/anomalies")
def anomalies(tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    from ..services.anomaly import zscore_anomalies
    return zscore_anomalies(db, tenant_id)


@router.get("/presign-upload")
def presign(filename: str):
    """Returns fields & url to POST directly to S3."""
    return presign_csv_post(filename)


@router.post("/ingest-s3")
def ingest_s3(key: str, tenant_id: int = Depends(tenant_guard), db: Session = Depends(db_dep)):
    df = read_csv_from_s3(key)
    # same ingest logic as /upload-csv
    skus = df["product_sku"].unique().tolist()
    existing = {p.sku: p for p in db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku.in_(skus)).all()}
    for sku in skus:
        if sku not in existing:
            db.add(Product(tenant_id=tenant_id, sku=sku, name=sku))
    db.flush()
    existing = {p.sku: p for p in db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku.in_(skus)).all()}
    for row in df.itertuples(index=False):
        db.add(Sale(
            tenant_id=tenant_id,
            product_id=existing[row.product_sku].id,
            sale_date=pd.to_datetime(getattr(row, 'sale_date')).date(),
            units_sold=float(getattr(row, 'units_sold')),
            revenue=float(getattr(row, 'revenue')),
        ))
    db.commit()
    return {"rows": len(df), "source": f"s3://{settings.S3_BUCKET}/{key}"}

