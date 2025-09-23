from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Date, DateTime, Float, Boolean, UniqueConstraint, func
from .db import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    users = relationship("User", back_populates="tenant")
    products = relationship("Product", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="users")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    sku: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    current_stock: Mapped[float] = mapped_column(Float, default=0.0)
    tenant = relationship("Tenant", back_populates="products")
    __table_args__ = (UniqueConstraint('tenant_id','sku', name='uq_tenant_sku'),)

class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    sale_date: Mapped[Date] = mapped_column(Date, index=True)
    units_sold: Mapped[float] = mapped_column(Float)
    revenue: Mapped[float] = mapped_column(Float)

class Forecast(Base):
    __tablename__ = "forecasts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    forecast_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    horizon_date: Mapped[Date] = mapped_column(Date)
    units_forecast: Mapped[float] = mapped_column(Float)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    alert_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16), default="info")
    message: Mapped[str] = mapped_column(String(500))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
