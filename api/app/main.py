# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sales_routes, forecast_routes

from .config import get_settings
from .routers import (
    auth_routes,
    tenant_routes,
    product_routes,
    sales_routes,
    forecast_routes,
    alerts_routes,
)
from .routers import stats_routes  # new stats endpoints

# upgrade-pack helpers (safe to import; no-ops if you didn't add them)
try:
    from app.middleware import RequestIDMiddleware
except Exception:
    class RequestIDMiddleware:  # fallback no-op
        def __init__(self, app): pass

try:
    from app.prom import MetricsASGIMiddleware, metrics
except Exception:
    class MetricsASGIMiddleware:
        def __init__(self, app): pass
    def metrics(scope, receive, send): pass

# settings
settings = get_settings()

app = FastAPI(
    title="Operational Dashboard API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# ---- Middleware
app.add_middleware(RequestIDMiddleware)

cors_list = []
if getattr(settings, "CORS_ORIGINS", None):
    cors_list = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
else:
    # fallback env from upgrade-pack; else allow local
    cors_list = [getattr(settings, "CORS_ORIGIN", "http://localhost:5173")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

app.add_middleware(MetricsASGIMiddleware)

# ---- Health/metrics
@app.get("/", tags=["system"])
def root():
    return {"status": "ok"}

@app.get("/healthz", tags=["system"])
def healthz():
    return {"ok": True}

app.add_route("/metrics", metrics, methods=["GET"])

# ---- Routers
app.include_router(auth_routes.router)
app.include_router(tenant_routes.router)
app.include_router(product_routes.router)
app.include_router(sales_routes.router)
app.include_router(forecast_routes.router)
app.include_router(alerts_routes.router)
app.include_router(stats_routes.router)

