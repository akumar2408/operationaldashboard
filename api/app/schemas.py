from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProductIn(BaseModel):
    sku: str
    name: str

class SaleIn(BaseModel):
    product_sku: str
    sale_date: date
    units_sold: float
    revenue: float
