from pydantic import BaseModel, HttpUrl, EmailStr
from database.models import Status
from typing import Literal, Optional

class JobRequest(BaseModel):
    job_type: Literal["scraper", "crawler"]
    status: Status = Status.open

class UrlQueueRequest(BaseModel):
    url: HttpUrl
    status: Status = Status.open

class UserRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int