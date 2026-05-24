from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    id: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str