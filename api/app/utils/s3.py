import boto3, os, io, pandas as pd
from ..config import get_settings
settings = get_settings()

s3 = boto3.client("s3", region_name=settings.AWS_REGION)

def presign_csv_post(filename: str, expires=3600):
    return s3.generate_presigned_post(
        Bucket=settings.S3_BUCKET,
        Key=filename,
        Fields={"Content-Type": "text/csv"},
        Conditions=[{"Content-Type":"text/csv"}],
        ExpiresIn=expires,
    )

def read_csv_from_s3(key: str) -> pd.DataFrame:
    obj = s3.get_object(Bucket=settings.S3_BUCKET, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()))
