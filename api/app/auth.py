from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .utils.hashing import verify_password
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY","dev")
ALGORITHM = "HS256"
ACCESS_MINS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","60"))

def create_access_token(sub: str, minutes: int = ACCESS_MINS):
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials", headers={"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.email==email).first()
    if not user: raise cred_exc
    return user
