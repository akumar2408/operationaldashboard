# api/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import engine
from .models import Base
from .routers import (
    auth_routes,
    tenant_routes,
    product_routes,
    sales_routes,
    forecast_routes,
    alerts_routes,
    stats_routes,  # new stats endpoints
)

# --- Optional middlewares (fallback to no-ops if not present)
try:
    from app.middleware import RequestIDMiddleware  # type: ignore
except Exception:  # pragma: no cover
    class RequestIDMiddleware:  # fallback no-op
        def __init__(self, app): ...
        def __call__(self, scope, receive, send):  # type: ignore
            return app(scope, receive, send)       # noqa: F821


try:
    from app.prom import MetricsASGIMiddleware, metrics  # type: ignore
except Exception:  # pragma: no cover
    class MetricsASGIMiddleware:
        def __init__(self, app): ...
        def __call__(self, scope, receive, send):  # type: ignore
            return app(scope, receive, send)       # noqa: F821

    async def metrics(scope, receive, send):  # type: ignore
        # minimal placeholder endpoint
        from starlette.responses import PlainTextResponse
        resp = PlainTextResponse("metrics_unavailable\n", media_type="text/plain")
        await resp(scope, receive, send)


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables once at startup; safe to re-run.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Operational Dashboard API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---- Middleware
app.add_middleware(RequestIDMiddleware)

if getattr(settings, "CORS_ORIGINS", None):
    allow_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
else:
    allow_origins = [getattr(settings, "CORS_ORIGIN", "http://localhost:5173")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
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
