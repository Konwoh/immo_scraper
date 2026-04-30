from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.models import get_db, User
from core.api.utils import verify_password
from core.api.oauth2 import create_access_token
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    access_token = create_access_token({"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}