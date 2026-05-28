from pydantic import BaseModel

class TokenData(BaseModel):
    id: int

class SessionStatus(BaseModel):
    authenticated: bool
