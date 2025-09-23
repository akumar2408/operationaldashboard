# SMB Operational Dashboard – Quick Start

## Local Dev
1. `cp .env.example .env` and edit values if needed
2. `docker compose up --build`
3. Open web at http://localhost:5173 and API at http://localhost:8000/docs

### First Run
- Register via UI, then upload a CSV with columns: `product_sku,sale_date,units_sold,revenue`
- Hit `POST /forecast/run` to generate 30‑day forecasts
- View chart + alerts

## Deployment (AWS)
- Create `infra/terraform.tfvars` with your values (see variables.tf)
- `terraform -chdir=infra init && terraform -chdir=infra apply`
- Build & push Docker images to ECR (or let CI do it)
- ECS services will come online behind the ALB; note ALB DNS output

## Notes
- Forecasting uses ExponentialSmoothing to avoid heavy Prophet deps; swap in Prophet later if desired.
- Multi‑tenant: each user belongs to a tenant; data is filtered by `tenant_id` in all queries.
- Add role‑based access by checking `User.role` in route guards.
