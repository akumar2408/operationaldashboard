resource "aws_s3_bucket" "ingest" {
  bucket        = var.s3_bucket
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "ingest" {
  bucket = aws_s3_bucket.ingest.id
  rule { object_ownership = "BucketOwnerEnforced" }
}
