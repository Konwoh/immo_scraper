import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from backend.database.models import get_db, User
from datetime import datetime, timedelta, timezone
from backend.schemas.token import TokenData
from fastapi import Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_SECRET_KEY = str(os.getenv("REFRESH_SECRET_KEY"))  # Keep this different from access secret
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encode_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    
    return encode_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[str(ALGORITHM)])
        
        id = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    
    return token_data

def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if not access_token:
        raise credentials_exception

    token_data = verify_access_token(token=access_token, credentials_exception=credentials_exception)
    
    user = db.query(User).filter(User.id == token_data.id).first()
    if not user:
        raise credentials_exception

    return user

def create_refresh_token(data: dict, expires_delta: timedelta|None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=str(ALGORITHM))
