from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.models import get_db, User, RefreshToken
from backend.api.auth.utils import verify_password
from backend.api.auth.oauth2 import create_access_token, create_refresh_token
from backend.schemas.token import Token, RefreshTokenRequest
import os
import jwt
from jwt.exceptions import PyJWTError
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    db.add(RefreshToken(token=refresh_token, user_id = user.id))
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token/refresh", response_model=Token)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.refresh_token, str(os.getenv("REFRESH_SECRET_KEY")), algorithms=[str(os.getenv("ALGORITHM"))])
        user_Id = payload.get("user_id")

    except PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")
    token_in_db = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()

    if not token_in_db:
        raise HTTPException(status_code=403, detail="Refresh token not found")
    user = db.query(User).filter(User.id == user_Id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token({"user_id": user.id})
    new_refresh_token = create_refresh_token({"user_id": user.id})
    # Token rotation: delete old and insert new
    db.delete(token_in_db)
    db.add(RefreshToken(token=new_refresh_token, user_id=user.id))
    db.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }