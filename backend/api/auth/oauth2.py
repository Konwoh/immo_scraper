import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from backend.database.models import get_db, User
from datetime import datetime, timedelta, timezone
from backend.schemas.token import TokenData
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encode_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    
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

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_access_token(token=token, credentials_exception=credentials_exception)
    
    user = db.query(User).filter(User.id == token_data.id).first()
    return user 