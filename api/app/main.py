from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import auth_routes, tenant_routes, product_routes, sales_routes, forecast_routes, alerts_routes

settings = get_settings()
app = FastAPI(title="SMB Operational Dashboard")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(',') if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(tenant_routes.router)
app.include_router(product_routes.router)
app.include_router(sales_routes.router)
app.include_router(forecast_routes.router)
app.include_router(alerts_routes.router)

@app.get("/")
def root():
    return {"status": "ok"}
