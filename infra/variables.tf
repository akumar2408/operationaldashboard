variable "name"        { type = string, default = "smb-dashboard" }
variable "aws_region"  { type = string, default = "us-east-1" }
variable "s3_bucket"   { type = string }
variable "db_name"     { type = string, default = "dashboard" }
variable "db_user"     { type = string, default = "dashboard" }
variable "db_password" { type = string, sensitive = true }
variable "domain_name" { type = string, default = "" } # optional, if using Route53/ACM
