from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.models import get_db, User, RefreshToken
from backend.api.auth.utils import verify_password
from backend.api.auth.oauth2 import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_SECRET_KEY,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from backend.schemas.token import SessionStatus
from datetime import datetime, timedelta, timezone
import os
import jwt
from jwt.exceptions import PyJWTError
router = APIRouter(
    tags=["Authentication"]
)

COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")
COOKIE_PATH = "/"

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )

def clear_auth_cookies(response: Response):
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )

def purge_expired_refresh_tokens(db: Session, user_id: int) -> None:
    # expires_at is stored as a naive UTC timestamp, so compare against naive UTC now.
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.expires_at < cutoff,
    ).delete(synchronize_session=False)


def _refresh_token_expiry() -> datetime:
    # naive UTC, matching how the refresh_tokens.expires_at column stores values
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)


@router.post("/login", response_model=SessionStatus)
def login(response: Response, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.username).first()

    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    purge_expired_refresh_tokens(db, user.id)
    db.add(RefreshToken(token=refresh_token, user_id=user.id, expires_at=_refresh_token_expiry()))
    db.commit()
    set_auth_cookies(response, access_token, refresh_token)
    return {"authenticated": True}

@router.post("/token/refresh", response_model=SessionStatus)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token_value, str(REFRESH_SECRET_KEY), algorithms=[str(ALGORITHM)])
        user_id = payload.get("user_id")

    except PyJWTError:
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_in_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_value).first()

    if not token_in_db:
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    expires_at = token_in_db.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is not None and expires_at < datetime.now(timezone.utc):
        db.delete(token_in_db)
        db.commit()
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = create_access_token({"user_id": user.id})
    new_refresh_token = create_refresh_token({"user_id": user.id})
    db.delete(token_in_db)
    purge_expired_refresh_tokens(db, user.id)
    db.add(RefreshToken(token=new_refresh_token, user_id=user.id, expires_at=_refresh_token_expiry()))
    db.commit()
    set_auth_cookies(response, new_access_token, new_refresh_token)

    return {"authenticated": True}

@router.post("/logout", response_model=SessionStatus)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token_value:
        token_in_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_value).first()
        if token_in_db:
            db.delete(token_in_db)
            db.commit()

    clear_auth_cookies(response)
    return {"authenticated": False}

@router.get("/auth/session", response_model=SessionStatus)
def session_status(_current_user: User = Depends(get_current_user)):
    return {"authenticated": True}
