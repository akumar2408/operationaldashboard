from fastapi import Depends
from sqlalchemy.orm import Session
from .auth import get_current_user
from .db import get_db
from .models import User

def tenant_guard(current_user: User = Depends(get_current_user)):
    return current_user.tenant_id

def db_dep(db: Session = Depends(get_db)):
    return db
