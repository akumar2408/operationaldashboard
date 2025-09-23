from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserLogin, Token
from ..models import User, Tenant
from ..utils.hashing import hash_password, verify_password
from ..auth import create_access_token
from ..db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already used")
    tenant = Tenant(name=payload.tenant_name)
    db.add(tenant); db.flush()
    user = User(email=payload.email, password_hash=hash_password(payload.password), role="admin", tenant_id=tenant.id)
    db.add(user); db.commit()
    token = create_access_token(sub=user.email)
    return Token(access_token=token)

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=user.email)
    return Token(access_token=token)
